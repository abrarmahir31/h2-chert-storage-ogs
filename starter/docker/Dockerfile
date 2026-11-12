# Container fallback: Ubuntu 24.04 (the version tested by the OGS team) + OGS via pip.
# Build:  docker build -t ogs-h2 -f starter/docker/Dockerfile .
# Run:    docker run --rm -it -v "${PWD}:/work" -w /work ogs-h2 python starter/00_check_install/check_install.py
FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive PYVISTA_OFF_SCREEN=true
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 python3-venv git ca-certificates \
        libgl1 libglu1-mesa libgomp1 libxcursor1 libxinerama1 libxft2 libxrender1 libosmesa6 \
    && rm -rf /var/lib/apt/lists/*
RUN python3 -m venv /opt/ogs-env
ENV PATH="/opt/ogs-env/bin:${PATH}"
COPY starter/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r /tmp/requirements.txt
WORKDIR /work
