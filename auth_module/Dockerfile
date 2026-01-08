FROM golang:1.23-alpine AS builder

WORKDIR /app

# git нужен для go mod
RUN apk add --no-cache git

# ВАЖНО: правильный GOPROXY
ENV GOPROXY=https://goproxy.io,direct

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o app ./cmd/app

# ---------- runtime ----------
FROM alpine:3.19
WORKDIR /app
COPY --from=builder /app/app .
EXPOSE 8081
CMD ["./app"]