FROM ubuntu:20.04 as build

ENV TZ=US/Central
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /dependencies

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y \
    build-essential cmake ninja-build autoconf \
    clang libc++-dev libc++abi-dev gfortran \
    libblas-dev liblapack-dev libatlas-base-dev libhdf5-dev \
    zlib1g-dev libbz2-dev liblzma-dev protobuf-compiler \
    python3-dev git wget vim curl

ENV PATH="/root/miniconda3/bin:${PATH}"

RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64 \
    && conda install -c conda-forge openbabel \
    && conda install -c mcs07 pubchempy 

# Pip installs
RUN pip install pymp-pypi numpy pandas scipy setuptools rdkit-pypi umap-learn openpyxl

WORKDIR /work/

ENTRYPOINT ["bash"]