# nabledge-dev

Nablarch knowledge development

## Prerequisites

- WSL2 / Ubuntu
- CA certificate (if behind corporate proxy)

## Setup

### 1. Install CA Certificate (for proxy environments)

```bash
sudo cp /path/to/your/ca.crt /usr/local/share/ca-certificates/ca.crt
sudo update-ca-certificates
```

### 2. Environment Setup

```bash
./setup.sh
cp .env.example .env
# Edit .env and set your credentials
```

## Getting Started

```bash
source .env
claude
```
