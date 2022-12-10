FROM python:3.9

WORKDIR /app

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Warsaw

RUN apt-get update && \
    apt-get install -y \
    software-properties-common \
    python3-pip \
    git \
    perl \
    curl \
    make \
    build-essential \
    wget \
    netcat \
    gcc && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/*

COPY backend/requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt


WORKDIR /packages/quap
COPY quap quap
COPY setup.py .

RUN pip3 install --no-cache-dir -e .


WORKDIR /app
COPY backend .

CMD ["bash", "run-server.sh"]
