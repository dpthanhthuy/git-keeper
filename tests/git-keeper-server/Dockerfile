
FROM ubuntu

# This file is based on the Dockerfile at
# https://github.com/jpetazzo/dind
# and is protected under the Apache 2.0 license.

# NOTE: all the following commands run as root

# The following taken from the "Docker in Docker (dind)" Dockerfile
# See https://github.com/jpetazzo/dind
RUN apt-get update && apt-get install -qqy \
    apt-transport-https \
    ca-certificates \
    curl \
    lxc \
    iptables \
    openssh-server \
    python3 \
    python3-pip \
    libffi-dev \
    libssl-dev \
    sudo \
    git \
    nano \
    screen

RUN pip3 install paramiko

# Install Docker from Docker Inc. repositories.
RUN curl -sSL https://get.docker.com/ | sh

# Install the magic wrapper.
ADD ./wrapdocker /usr/local/bin/wrapdocker
RUN chmod +x /usr/local/bin/wrapdocker

# Define additional metadata for our image.
VOLUME /var/lib/docker

RUN mkdir /var/run/sshd

# Create the gitkeeper group and the main gitkeeper account in that group
RUN groupadd gitkeeper
RUN useradd -ms /bin/bash keeper
RUN usermod -aG keeper keeper
# keeper must be in the docker group to be able to run docker commands
RUN usermod -aG docker keeper
RUN echo "keeper ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
RUN echo 'keeper:g1tk33p3r' | chpasswd

ADD ./ssh_server /etc/ssh
RUN chmod 600 /etc/ssh/*_key

RUN mkdir /email

ADD ./mysmtpd.py /usr/bin
RUN chmod +x /usr/bin/mysmtpd.py

# This will run the docker command and then all the sshd command to run
ENTRYPOINT ["wrapdocker"]

EXPOSE 22 25
CMD ["/usr/sbin/sshd", "-D"]
