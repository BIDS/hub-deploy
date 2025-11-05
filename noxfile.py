import os
from pathlib import Path

import nox

cluster_name = os.getenv("CLUSTER_NAME", "demo")
hub_name = os.getenv("HUB_NAME", "demo")

ROOT = Path(__file__).parent.resolve()
CHARTS = ROOT / "charts"
SUPPORT_CHART = CHARTS / "support"
HUB_CHART = CHARTS / "hub"


def tf_cluster_dir(cluster_name):
    return ROOT / "tf" / "clusters" / cluster_name


def cluster_dir(cluster_name):
    return ROOT / "clusters" / cluster_name


def hub_dir(cluster_name):
    return ROOT / "hubs" / cluster_name


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


@nox.session
def decrypt(session):
    cluster_path = cluster_dir(cluster_name)
    for parent_dir in (cluster_path, hub_dir(hub_name), hub_dir("_common")):
        for src in parent_dir.rglob("*.enc.*"):
            decrypt_file(session, src)


@nox.session
def helm_support(session):
    decrypt(session)
    cluster_path = cluster_dir(cluster_name)
    kubeconfig = cluster_path / "kubeconfig.dec.yaml"
    assert kubeconfig.exists()
    os.environ["KUBECONFIG"] = str(kubeconfig)
    session.run("helm", "dependency", "update", SUPPORT_CHART, external=True)
    values_args = []
    for path in (cluster_path / "support").rglob("*.yaml"):
        if ".enc." not in path.name:
            values_args.extend(["--values", str(path)])

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
    cluster_path = cluster_dir(cluster_name)
    common_path = hub_dir("_common")
    hub_path = hub_dir(hub_name)
    assert common_path.exists()
    assert hub_path.exists()
    kubeconfig = cluster_path / "kubeconfig.dec.yaml"
    assert kubeconfig.exists()
    os.environ["KUBECONFIG"] = str(kubeconfig)
    session.run("helm", "dependency", "update", HUB_CHART, external=True)
    values_args = []
    for config_dir in (common_path, hub_path):
        for path in config_dir.rglob("*.yaml"):
            if ".enc." not in path.name:
                values_args.extend(["--values", str(path)])

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
