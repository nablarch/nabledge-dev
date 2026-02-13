# Nabledge-Test

Test framework for nabledge skills (nabledge-6 and nabledge-5), powered by skill-creator.

## Quick Start

```bash
# Single scenario
nabledge-test 6 handlers-001

# All scenarios  
nabledge-test 6 --all

# By category
nabledge-test 6 --category handlers
```

## Architecture

- **Interface Layer**: Nablarch-specific scenarios and reporting
- **Evaluation Engine**: skill-creator (executor, grader, analyzer agents)
- **Support**: nabledge-6 (Nablarch 6) and nabledge-5 (Nablarch 5, future)

## See SKILL.md for detailed documentation
