# Start with ARM base image
FROM balenalib/raspberry-pi-python:3.6-latest-build

# Ubuntu 18.04 base image
#FROM amd64/ubuntu:18.04

# Create directorues
RUN mkdir /code
WORKDIR /code
COPY . /code

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN chmod +x /code/_bin/docker_run.sh
RUN chmod +x /code/_bin/worker_run.sh

# Install pip
RUN apt-get update -y
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3

# Install requirements
RUN python3 -m pip install --upgrade setuptools wheel
RUN python3 -m pip install -r requirements.txt

# Collect our static media.
RUN python3 /code/manage.py collectstatic --noinput

CMD ["/code/_bin/docker_run.sh"]