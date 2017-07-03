FROM ubuntu:yakkety
MAINTAINER Tim Byrne <sultan@locehilios.com>

# Install prerequisites
RUN apt-get update && apt-get install -y git gnupg1 make shellcheck bats expect curl python-pip lsb-release
RUN pip install envtpl

# Force GNUPG version 1 at path /usr/bin/gpg
RUN ln -fs /usr/bin/gpg1 /usr/bin/gpg

# /yadm will be the work directory for all tests
# docker commands should mount the local yadm project as /yadm
WORKDIR /yadm

# Create a Makefile to be used if no /yadm volume is mounted
RUN echo "test:\n\t@echo 'The yadm project must be mounted at /yadm'\n\t@echo 'Try using a docker parameter like -v \"\$\$PWD:/yadm:ro\"'\n\t@false" > /yadm/Makefile

# By default, run all tests defined
CMD make test
