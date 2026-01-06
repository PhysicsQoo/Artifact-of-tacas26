# Copyright 2025-2026 Wei-Jia Huang
# SPDX-License-Identifier: MIT

# Base image: Miniconda3
FROM continuumio/miniconda3

# Set working directory
WORKDIR /app

# Update Conda, upgrade Python to 3.12, and clean up
RUN conda install -n base -c defaults python=3.12 pip -y && \
    conda clean --all -f -y
# Install required system packages and clean up
RUN apt update && \
    apt install -y --no-install-recommends \
    wget \
    libgmpxx4ldbl \
    libmpfr6 \
    libatomic1 \
    git && \
    rm -rf /var/lib/apt/lists/*

# Install libffi7 from .deb if needed, then clean up
RUN wget http://ftp.debian.org/debian/pool/main/libf/libffi/libffi7_3.3-6_amd64.deb && \
    dpkg -i libffi7_3.3-6_amd64.deb || apt --fix-broken install -y && \
    rm libffi7_3.3-6_amd64.deb && \
    rm -rf /var/lib/apt/lists/*

# Clone QuPRS repository into /app
RUN git clone --branch v0.9.1 --depth 1 https://github.com/PhysicsQoo/QuPRS.git /app

# Install Python dependencies and clean pip cache
RUN pip install -e .[dev] && \
    pip install tqdm psutil && \
    pip install quokka_sharp==2.7 mqt.qcec==2.8.2 pyzx==0.9.0 && \
    rm -rf ~/.cache/pip ./dist

# Copy test and benchmark files into the container
COPY ./experiments/table.py /app/experiments/table.py
COPY ./experiments/table_MQT.py /app/experiments/table_MQT.py
COPY ./experiments/table_MQT_Random_Rotation.py /app/experiments/table_MQT_Random_Rotation.py
COPY ./experiments/table_Feynman.py /app/experiments/table_Feynman.py

COPY ./experiments/feynver /app/experiments/feynver
COPY ./experiments/gpmc /app/experiments/gpmc
COPY ./experiments/config.json /app/experiments/config.json
COPY NOTICE.md /app/NOTICE.md

# License label
LABEL org.opencontainers.image.licenses="MIT"

# Default command
CMD ["/bin/bash"]
