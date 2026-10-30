import os
from pathlib import Path
from tempfile import NamedTemporaryFile

import nox
import yaml

cluster_name = os.environ["CLUSTER_NAME"]
hub_name = os.environ["HUB_NAME"]

ROOT = Path(__file__).parent.resolve()
CHARTS = ROOT / "charts"
SUPPORT_CHART = CHARTS / "support"
HUB_CHART = CHARTS / "hub"


def tf_cluster_dir(cluster_name):
    return ROOT / "tf" / "clusters" / cluster_name


def cluster_dir(cluster_name):
    return ROOT / "clusters" / cluster_name


def hub_dir(hub_name):
    return ROOT / "hubs" / hub_name


def set_kubeconfig(session, cluster_name: str) -> None:
    cluster_path = cluster_dir(cluster_name)
    kubeconfig = cluster_path / "kubeconfig.dec.yaml"
    if not kubeconfig.exists():
        load_kubeconfig(session, cluster_name, kubeconfig)
    assert kubeconfig.exists()
    os.environ["KUBECONFIG"] = str(kubeconfig)


def get_values_args(*values_dirs):
    args = []
    for values_dir in values_dirs:
        for values_yaml in values_dir.rglob("*.yaml"):
            if ".enc." not in values_yaml.name:
                args.extend(["--values", str(values_yaml)])
    return args


def load_kubeconfig(session, cluster_name: str, kubeconfig: Path) -> None:
    cluster_path = cluster_dir(cluster_name)
    config_file = cluster_path / "config.yaml"
    with config_file.open() as f:
        config = yaml.safe_load(f)
    env = os.environ.copy()
    gcp_cluster_name = config["gcp"].get("cluster_name", cluster_name)
    gcp_project = config["gcp"]["project"]
    gcp_zone = config["gcp"]["zone"]
    env["KUBECONFIG"] = kubeconfig
    # gcloud container clusters get-credentials --project=bids-jupyterhub demo --zone=us-central1
    session.run(
        "gcloud",
        "container",
        "clusters",
        "get-credentials",
        "--project",
        gcp_project,
        "--zone",
        gcp_zone,
        gcp_cluster_name,
        env=env,
        external=True,
    )


@nox.session
def tofu_apply(session):
    """apply tofu changes

    equivalent to nox -s tofu -- apply ...
    """
    session.notify("tofu", ["apply", *session.posargs])


@nox.session
def tofu(session):
    """run any tofu command on a cluster"""
    session.chdir(tf_cluster_dir(cluster_name))
    session.run("tofu", *session.posargs, external=True)


def decrypt_file(session, src: Path):
    dest = src.parent / src.name.replace(".enc.", ".dec.")
    assert dest != src
    session.run("sops", "decrypt", src, "--output", dest, external=True)


@nox.session(python=False)
def decrypt(session):
    cluster_path = cluster_dir(cluster_name)
    for parent_dir in (cluster_path, hub_dir(hub_name), hub_dir("_common")):
        for src in parent_dir.rglob("*.enc.*"):
            decrypt_file(session, src)


@nox.session(python=False)
def kubectl(session):
    decrypt(session)
    set_kubeconfig(session, cluster_name)
    session.run("kubectl", *session.posargs, external=True)


@nox.session(python=False)
def helm_support_upgrade_crds(session):
    decrypt(session)
    set_kubeconfig(session, cluster_name)
    session.run("helm", "dependency", "update", SUPPORT_CHART, external=True)
    # apply any CRD upgrades (e.g. cert-manager, envoy gateway)
    # helm cannot upgrade CRDs
    # from https://github.com/traefik/traefik-helm-chart?tab=readme-ov-file#upgrade-the-standalone-traefik-chart
    with NamedTemporaryFile() as f:
        session.run("helm", "show", "crds", SUPPORT_CHART, external=True, stdout=f)
        f.flush()
        session.run(
            "kubectl",
            "apply",
            "--server-side",
            "--force-conflicts",
            "-f",
            f.name,
            external=True,
        )


@nox.session
def helm_support(session):
    decrypt(session)
    cluster_path = cluster_dir(cluster_name)
    set_kubeconfig(session, cluster_name)
    session.run("helm", "dependency", "update", SUPPORT_CHART, external=True)
    values_args = get_values_args(cluster_path / "support")

    session.run(
        "helm",
        "upgrade",
        "--install",
        "--namespace=support",
        "support",
        SUPPORT_CHART,
        *values_args,
        external=True,
    )


@nox.session
def helm_hub(session):
    decrypt(session)
    common_path = hub_dir("_common")
    hub_path = hub_dir(hub_name)
    assert common_path.exists()
    assert hub_path.exists()
    set_kubeconfig(session, cluster_name)
    session.run("helm", "dependency", "update", HUB_CHART, external=True)
    values_args = get_values_args(common_path, hub_path)

    session.run(
        "helm",
        "upgrade",
        "--install",
        "--namespace",
        hub_name,
        hub_name,
        HUB_CHART,
        *values_args,
        external=True,
    )
