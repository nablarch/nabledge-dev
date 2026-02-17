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

### Release Procedure

To release a new version to [nablarch/nabledge](https://github.com/nablarch/nabledge):

1. **Update version files** (follow `.claude/rules/release.md`):
   - Update `.claude/skills/nabledge-6/plugin/CHANGELOG.md`
   - Update `.claude/skills/nabledge-6/plugin/plugin.json`
   - Update `.claude/marketplace/.claude-plugin/marketplace.json`
   - Update `.claude/marketplace/CHANGELOG.md`

2. **Merge to main** via pull request

3. **Merge main to release and push**:
   ```bash
   git checkout release
   git merge main
   git push origin release
   ```

4. GitHub Actions will automatically:
   - Validate version consistency (marketplace.json = CHANGELOG.md)
   - Validate version increment (new version > latest tag in nablarch/nabledge)
   - Deploy to nablarch/nabledge
   - Create version tag

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
