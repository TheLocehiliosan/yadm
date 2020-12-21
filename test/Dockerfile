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

# Create a flag to identify when running inside the yadm testbed
RUN touch /.yadmtestbed

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
    man \
    python3-pip \
    vim \
  && rm -rf /var/lib/apt/lists/*;

ARG SC_VER=0.7.1
RUN \
  curl -fLo - \
  https://github.com/koalaman/shellcheck/releases/download/v$SC_VER/shellcheck-v$SC_VER.linux.x86_64.tar.xz | \
  tar -xJv && \
  mv shellcheck-v$SC_VER/shellcheck /usr/bin && \
  rm -rf shellcheck-v$SC_VER

COPY test/requirements.txt /tmp/requirements.txt
RUN pip3 install --upgrade pip setuptools
RUN pip3 install --upgrade -r /tmp/requirements.txt

RUN \
  curl https://raw.githubusercontent.com/jirutka/esh/v0.3.0/esh > /usr/local/bin/esh && \
  chmod +x /usr/local/bin/esh

# /yadm will be the work directory for all tests
# docker commands should mount the local yadm project as /yadm
WORKDIR /yadm

# Create a Makefile to be used if no /yadm volume is mounted
RUN echo "test:\n\t@echo 'The yadm project must be mounted at /yadm'\n\t@echo 'Try using a docker parameter like -v \"\$\$PWD:/yadm:ro\"'\n\t@false" > /yadm/Makefile

# By default, run all tests defined
CMD make test
