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


COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY quap quap
COPY frontend web

COPY setup.py .
COPY .env .

RUN pip install --no-cache-dir -e .

COPY run-server.sh run-server.sh
# fixme "--server.address='0.0.0.0'"
#CMD ["streamlit", "run", "site.py", "--server.port=9100", "--theme.base='dark'"]
CMD ["bash", "run-server.sh"]
