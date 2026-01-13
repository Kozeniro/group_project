FROM mcr.microsoft.com/devcontainers/cpp:1-ubuntu-24.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev libpqxx-dev cmake build-essential && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only CMakeLists.txt and minimal source files needed for configuration
COPY CMakeLists.txt .
COPY src/ ./src
COPY include/ ./include

# Create build directory inside mounted volume
RUN mkdir -p /app/build

# Run cmake and make inside /app/build
CMD ["bash", "-c", "cd /app/build && cmake .. && make && ./main_module"]