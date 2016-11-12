FROM fedora:21

MAINTAINER Andy Jones <andy.jones@gsacapital.com>

# Configure the locale and proxy settings
RUN localedef -i en_US -f UTF-8 en_US.UTF-8
ENV PATH=opt/conda/bin:$PATH \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8 

# This is the absolute minimum set of packages needed for qmspy to run.
# The X-Windows packages are required by matplotlib.
RUN yum install -y wget tar bzip2 ca-certificates libXext libSM libXrender

# Install miniconda and then and dask.distributed
RUN wget -O /tmp/Miniconda.sh --quiet https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    /bin/bash /tmp/Miniconda.sh -b -p /opt/conda  && \
    conda install dask distributed -y -c conda-forge && \
    rm -rf /mnt/conda-repo

# Copy in the startscheduler and startworker scripts
COPY start* /bin/
RUN chmod u+x /bin/start*

# Expose Dask ports
EXPOSE 80 8785
