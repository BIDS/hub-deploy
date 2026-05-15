FROM ghcr.io/prefix-dev/pixi:0.68.1 AS build

# copy source code, pixi.toml and pixi.lock to the container
COPY pixi* /srv/
WORKDIR /srv/
RUN pixi install
COPY install-opencode.sh /srv/
RUN pixi run install-opencode

FROM debian:13

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        git \
        nano \
        procps \
        vim \ 
 && rm -rf /var/lib/apt/lists/*
 
ARG UID=1000
RUN useradd -m -u 1000 jovyan
COPY --from=build /srv/.pixi/envs/default /srv/.pixi/envs/default
COPY entrypoint.sh /entrypoint.sh
COPY mambarc /srv/.pixi/envs/default/.condarc

ENV PYTHONUNBUFFERED=1
WORKDIR /home/jovyan
USER $UID


ENTRYPOINT ["/entrypoint.sh"]
CMD ["jupyterhub-singleuser"]
