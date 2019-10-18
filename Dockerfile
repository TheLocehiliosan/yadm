FROM jekyll/jekyll:4.0.0
MAINTAINER Tim Byrne <sultan@locehilios.com>

# Convenience settings for the testbed's root account
RUN echo 'set -o vi' >> /root/.bashrc

# Create a flag to identify when running inside the yadm/jekyll image
RUN touch /.yadmjekyll

# Extra dependencies for testing
RUN gem install html-proofer
RUN apk add --update py-pip
RUN pip install yamllint==1.15.0
