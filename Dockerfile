###############################################################################
# Docker file for recipe app API
# Author: Anurag Bhatt
# Date: 2021-03-21
# Version: 1.0
# Description: Docker file to build the image for the Django application
# Usage: docker build .
# docker run -p 8000:8000 <image_id>
###############################################################################


# Use an existing docker image of python as a base (python:3.9-alpine3.13)
FROM python:3.9-alpine3.13
# Set the maintainer(name/mail_id/website/etc) of the image
LABEL maintainer="anuragbhatt1805@gmail.com"


# Set the environment variable to run the python in unbuffered mode
ENV PYTHONUNBUFFERED 1


# Copy the requirements.txt file to the image
COPY ./requirements.txt /tmp/requirements.txt
# Copy the requirements.dev.txt file to the image
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
# Copy the app folder to the image
COPY ./app /app
# Set the working directory to the app folder
WORKDIR /app
# Expose the port 8000, which allows the container to communicate with the host
EXPOSE 8000


# The development dependencies are required to run the tests
ARG DEV=false
# This is done to install the development dependencies in the image


# Install the dependencies
# Lines are divided using && to reduce the number of layers in the image, This is done to reduce the size of the image
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt; \
    fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser \
        --disabled-password \
        --no-create-home \
        anurag
# The above command creates a virtual environment in the image and installs the dependencies in the virtual environment
# The virtual environment is created in the /py folder
# The --upgrade flag is used to upgrade the pip to the latest version
# The -r flag is used to install the dependencies from the requirements.txt file
# Shell script is used to install the development dependencies if the DEV variable is set to true
# rm -rf /tmp is used to remove the temporary files created during the installation of the dependencies
# -----------------------------------------------------------------------------
# Create a user to run the application, this is done to avoid running the application as root user
# The --disabled-password flag is used to avoid setting a password for the user
# The --no-create-home flag is used to avoid creating a home directory for the user


# Updates the envoirnment variable of the image to use the virtual environment
ENV PATH="/py/bin:$PATH"


USER anurag