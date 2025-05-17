FROM public.ecr.aws/docker/library/python:3.12.10-slim-bullseye

RUN apt-get update && apt-get install -y \
    tar \
    gzip \
    pip \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install gcloud-sdk
RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then \
        curl -O "https://storage.googleapis.com/cloud-sdk-release/google-cloud-cli-443.0.0-linux-x86_64.tar.gz" && \
        tar -xf google-cloud-cli-443.0.0-linux-x86_64.tar.gz; \
    elif [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then \
        curl -O "https://storage.googleapis.com/cloud-sdk-release/google-cloud-cli-443.0.0-linux-arm.tar.gz" && \
        tar -xf google-cloud-cli-443.0.0-linux-arm.tar.gz; \
    else \
        echo "Unsupported architecture: $ARCH" && exit 1; \
    fi

RUN ./google-cloud-sdk/install.sh
ENV PATH=$PATH:/google-cloud-sdk/bin
RUN gcloud --version
RUN bq version

COPY main.py /app/main.py
COPY requirements.txt /app/requirements.txt

WORKDIR /app
RUN pip install -r requirements.txt

CMD ["python3", "main.py"]
