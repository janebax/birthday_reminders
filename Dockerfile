# Updating to run in a lambda https://docs.aws.amazon.com/lambda/latest/dg/images-create.html
# Define function directory
ARG FUNCTION_DIR="/function"

###############################################
# Image
###############################################
FROM python:3.11.1-slim-buster

# Install aws-lambda-cpp build dependencies
RUN apt-get update && \
  apt-get install -y \
  g++ \
  make \
  cmake \
  unzip \
  libcurl4-openssl-dev

# Include global arg in this stage of the build
ARG FUNCTION_DIR
# Create function directory
RUN mkdir -p ${FUNCTION_DIR}

# Copy function code
COPY app/* ${FUNCTION_DIR}

# Install the runtime interface client
RUN pip install \
        --target ${FUNCTION_DIR} \
        awslambdaric

# Explanation of Docker code is here: https://stackoverflow.com/questions/53835198/integrating-python-poetry-with-docker/54763270#54763270
ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.2.2

# Include global arg in this stage of the build
ARG FUNCTION_DIR
# Set working directory to function root directory
WORKDIR ${FUNCTION_DIR}

# Install poetry
RUN pip install poetry==$POETRY_VERSION

# Copy only requirements to cache them in docker layer
# Only including README.md as it is referred to in the pyproject.toml
COPY poetry.lock pyproject.toml README.md app tests ${FUNCTION_DIR}

# Project initialization:
RUN poetry config virtualenvs.create false 
RUN poetry install --no-interaction

ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]
CMD ["lambda_handler.lambda_handler"]