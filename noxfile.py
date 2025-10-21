from pathlib import Path

import nox


@nox.session
def tf(session):
    cluster_name = "demo"  # todo: arg when there's more than one
    session.chdir(Path("tf") / "clusters" / cluster_name)
    session.run("tofu", "apply", external=True)
