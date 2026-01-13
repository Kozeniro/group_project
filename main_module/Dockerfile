FROM mcr.microsoft.com/devcontainers/cpp:1-ubuntu-24.04

RUN apt-get update && apt-get install -y \
    libpq-dev \
    libpqxx-dev \
    cmake \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY . /app
WORKDIR /app

RUN mkdir -p build && cd build && \
    cmake .. && \
    make

CMD ["./build/main_module"]