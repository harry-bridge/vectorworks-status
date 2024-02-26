# Start with ARM base image
#FROM balenalib/raspberry-pi-python:3.6-latest-build
FROM python:3.10

# Create directorues
RUN mkdir /code
WORKDIR /code
COPY . /code

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN chmod +x /code/docker/docker_run.sh
RUN chmod +x /code/docker/worker_run.sh

# Install pip
RUN pip install -U pip setuptools wheel

# Install requirements
RUN pip3 install --no-cache-dir -r requirements.txt

# Collect our static media.
RUN python3 /code/manage.py collectstatic --noinput

CMD ["/code/docker/docker_run.sh"]