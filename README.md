# nabledge-dev

Nablarch knowledge development

**Documentation**: [Design Document](doc/nabledge-design.md) - Comprehensive architecture and design details

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

## Branch Strategy

This repository uses a two-branch strategy for controlled releases:

| Branch | Purpose | Workflow |
|--------|---------|----------|
| **main** | Development branch | All development work is merged here via pull requests |
| **release** | Release branch | Receives merges from main when ready to release. Triggers automatic deployment to [nablarch/nabledge](https://github.com/nablarch/nabledge) |

### Deployment Flow

```
Development → main (via PR) → release (manual merge) → nablarch/nabledge (auto-deploy)
```

When changes are pushed to the `release` branch, GitHub Actions automatically:
1. Transforms the skill content to marketplace plugin structure
2. Deploys to the `main` branch in [nablarch/nabledge](https://github.com/nablarch/nabledge)
3. Creates version tags

This allows maintainers to control release timing by deciding when to merge main → release.
