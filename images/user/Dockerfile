FROM ghcr.io/prefix-dev/pixi:0.68.1 AS build

# copy source code, pixi.toml and pixi.lock to the container
COPY pixi* /srv/
WORKDIR /srv/
RUN pixi install
COPY *.sh /srv/
RUN pixi run install-opencode
# Create the shell-hook bash script to activate the environment
RUN pixi shell-hook > /shell-hook.sh

# extend the shell-hook script to run the command passed to the container
RUN echo 'exec "$@"' >> /shell-hook.sh

FROM debian:13

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        git \
        vim \ 
        nano \
 && rm -rf /var/lib/apt/lists/*
 
ARG UID=1000
RUN useradd -m -u 1000 jovyan
COPY --from=build /srv/.pixi/envs/default /srv/.pixi/envs/default
COPY --from=build /shell-hook.sh /shell-hook.sh

ENV PYTHONUNBUFFERED=1
WORKDIR /home/jovyan
USER $UID

ENTRYPOINT ["/bin/bash", "/shell-hook.sh"]
CMD ["jupyterhub-singleuser"]
