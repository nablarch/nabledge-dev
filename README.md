# nabledge-dev

Nablarch knowledge development

## Documents

- [Design Document](doc/nabledge-design.md) - Architecture and design details
- [Development Status](doc/development-status.md) - Current progress and roadmap

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

## Development

### Testing nabledge Skills

Use the `nabledge-test` skill to validate nabledge-6 functionality:

```
# Run a single test scenario
/nabledge-test 6 handlers-001

# Run all test scenarios
/nabledge-test 6 --all

# Run tests for a specific category
/nabledge-test 6 --category handlers
```

Test scenarios are defined in `.claude/skills/nabledge-test/scenarios/nabledge-6/scenarios.json`. Results are saved to `work/YYYYMMDD/test-<id>-<timestamp>.md`.

The nabledge-test skill uses skill-creator's evaluation procedures to verify:
- Correct workflow execution (keyword-search, section-judgement)
- Expected keywords present in responses
- Relevant sections identified from knowledge files
- Knowledge file content used (not LLM training data)
