# nabledge-dev

Nablarch knowledge development

## Documents

- [Development Status](doc/development-status.md) - Current progress and roadmap
- [Design Document](doc/nabledge-design.md) - Architecture and design details

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

This repository uses a single-branch development workflow:

| Branch | Purpose | Workflow |
|--------|---------|----------|
| **main** | Development branch | All development work is merged here via pull requests. Changes automatically sync to [nablarch/nabledge:develop](https://github.com/nablarch/nabledge/tree/develop) |

### Development Flow

```
Feature branch → main (via PR) → nablarch/nabledge:develop (auto-sync)
```

When changes are pushed to the `main` branch, GitHub Actions automatically:
1. Transforms the skill content to marketplace plugin structure
2. Syncs to the `develop` branch in [nablarch/nabledge](https://github.com/nablarch/nabledge)

This allows:
- Continuous integration of development work to nabledge:develop
- Users can test unreleased features from the develop branch
- Clear separation: nabledge-dev for development, nabledge for distribution

### Release Procedure

Releases are managed in the **[nablarch/nabledge](https://github.com/nablarch/nabledge)** repository, not here.

**In nablarch/nabledge repository:**

1. **Prepare release** - Update version files and CHANGELOG in develop branch
2. **Create release PR** - From `develop` to `main` branch
3. **Merge and tag** - After review, merge PR and create version tag
4. **Publish release** - Create GitHub release with release notes

See `.claude/rules/release.md` for detailed release workflow.

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

## Feedback

### For published nabledge skills
Report issues or request features in [nablarch/nabledge Issues](https://github.com/nablarch/nabledge/issues) - this helps users search and find solutions.

### For unreleased development work
Report issues or discuss changes in [nablarch/nabledge-dev Issues](https://github.com/nablarch/nabledge-dev/issues).
