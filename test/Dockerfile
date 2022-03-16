FROM ubuntu:18.04
MAINTAINER Tim Byrne <sultan@locehilios.com>

# Shellcheck and esh versions
ARG SC_VER=0.8.0
ARG ESH_VER=0.3.1

# Install prerequisites and configure UTF-8 locale
RUN \
  echo "en_US.UTF-8 UTF-8" > /etc/locale.gen \
  && apt-get update \
  && DEBIAN_FRONTEND=noninteractive \
    apt-get install -y --no-install-recommends \
    expect \
    git \
    gnupg \
    locales \
    lsb-release \
    make \
    man \
    python3-pip \
    vim-tiny \
    xz-utils \
  && rm -rf /var/lib/apt/lists/* \
  && update-locale LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'

ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'

# Convenience settings for the testbed's root account
RUN echo 'set -o vi' >> /root/.bashrc

# Create a flag to identify when running inside the yadm testbed
RUN touch /.yadmtestbed

# Install shellcheck
ADD https://github.com/koalaman/shellcheck/releases/download/v$SC_VER/shellcheck-v$SC_VER.linux.x86_64.tar.xz /opt
RUN cd /opt \
  && tar xf shellcheck-v$SC_VER.linux.x86_64.tar.xz \
  && rm -f shellcheck-v$SC_VER.linux.x86_64.tar.xz \
  && ln -s /opt/shellcheck-v$SC_VER/shellcheck /usr/local/bin

# Upgrade pip3 and install requirements
COPY test/requirements.txt /tmp/requirements.txt
RUN python3 -m pip install --upgrade pip setuptools \
  && python3 -m pip install --upgrade -r /tmp/requirements.txt \
  && rm -f /tmp/requirements

# Install esh
ADD https://raw.githubusercontent.com/jirutka/esh/v$ESH_VER/esh /usr/local/bin
RUN chmod +x /usr/local/bin/esh

# Create workdir and dummy Makefile to be used if no /yadm volume is mounted
RUN mkdir /yadm \
  && echo "test:" > /yadm/Makefile \
  && echo "\t@echo 'The yadm project must be mounted at /yadm'" >> /yadm/Makefile \
  && echo "\t@echo 'Try using a docker parameter like -v \"\$\$PWD:/yadm:ro\"'" >> /yadm/Makefile \
  && echo "\t@false" >> /yadm/Makefile

# Include released versions of yadm to test upgrades
ADD https://raw.githubusercontent.com/TheLocehiliosan/yadm/1.12.0/yadm /usr/local/bin/yadm-1.12.0
ADD https://raw.githubusercontent.com/TheLocehiliosan/yadm/2.5.0/yadm /usr/local/bin/yadm-2.5.0
RUN chmod +x /usr/local/bin/yadm-*

# Configure git to make it easier to test yadm manually
RUN git config --system user.email "test@yadm.io" \
  && git config --system user.name "Yadm Test"

# /yadm will be the work directory for all tests
# docker commands should mount the local yadm project as /yadm
WORKDIR /yadm

# By default, run all tests defined
CMD make test
