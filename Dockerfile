FROM ubuntu:18.04
MAINTAINER Tim Byrne <sultan@locehilios.com>

# No input during build
ENV DEBIAN_FRONTEND noninteractive

# UTF8 locale
RUN apt-get update && apt-get install -y locales
RUN locale-gen en_US.UTF-8
ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'

# Convenience settings for the testbed's root account
RUN echo 'set -o vi' >> /root/.bashrc

# Install prerequisites
RUN \
  apt-get update && \
  apt-get install -y \
    curl \
    expect \
    git \
    gnupg \
    lsb-release \
    make \
    python3-pip \
    shellcheck=0.4.6-1 \
    vim \
  ;
RUN pip3 install \
      envtpl \
      j2cli \
      flake8==3.7.8 \
      pylint==2.4.1 \
      pytest==5.1.3 \
      yamllint==1.17.0 \
    ;

# Create a flag to identify when running inside the yadm testbed
RUN touch /.yadmtestbed

# /yadm will be the work directory for all tests
# docker commands should mount the local yadm project as /yadm
WORKDIR /yadm

# Create a Makefile to be used if no /yadm volume is mounted
RUN echo "test:\n\t@echo 'The yadm project must be mounted at /yadm'\n\t@echo 'Try using a docker parameter like -v \"\$\$PWD:/yadm:ro\"'\n\t@false" > /yadm/Makefile

# By default, run all tests defined
CMD make test
