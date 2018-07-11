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
RUN apt-get update && apt-get install -y git gnupg1 make shellcheck=0.4.6-1 bats expect curl python3-pip lsb-release
RUN pip3 install envtpl pytest==3.6.4 pylint==1.9.2 flake8==3.5.0

# Force GNUPG version 1 at path /usr/bin/gpg
RUN ln -fs /usr/bin/gpg1 /usr/bin/gpg

# /yadm will be the work directory for all tests
# docker commands should mount the local yadm project as /yadm
WORKDIR /yadm

# Create a Makefile to be used if no /yadm volume is mounted
RUN echo "test:\n\t@echo 'The yadm project must be mounted at /yadm'\n\t@echo 'Try using a docker parameter like -v \"\$\$PWD:/yadm:ro\"'\n\t@false" > /yadm/Makefile

# By default, run all tests defined
CMD make test
