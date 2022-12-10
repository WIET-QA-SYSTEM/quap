FROM python:3.9

WORKDIR /frontend

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

COPY frontend/requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY frontend .

CMD ["streamlit", "run", "site.py", "--server.port=9000", "--theme.base=dark"]
