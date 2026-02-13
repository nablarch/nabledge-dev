# Nablarch Skills Marketplace

Nablarch skills for AI-assisted development using Claude Code and GitHub Copilot.

## Available Plugins

### nabledge-6

Nablarch 6 skill for AI-assisted development.

**Features**:
- Knowledge Search: Search Nablarch 6 documentation and best practices
- Code Analysis: Analyze application code from Nablarch perspective

**Installation**:
```bash
# Add marketplace
/plugin marketplace add nablarch/nabledge

# Install nabledge-6 plugin
/plugin install nabledge-6@nabledge
```

**Usage**:
```bash
# Basic usage
/nabledge-6

# Knowledge search
/nabledge-6 "How do I implement batch processing?"

# Code analysis
/nabledge-6 code-analysis
```

**Coverage**: Nablarch 6u3
- Batch processing basics
- Database access
- Testing framework basics
- Security checklist

See [plugins/nabledge-6/README.md](plugins/nabledge-6/README.md) for details.

### nabledge-5 (Coming Soon)

Nablarch 5 skill for AI-assisted development will be available in the future.

## Versioning

Each plugin has independent versioning:
- **nabledge-6**: Uses `minor.patch` format (e.g., 0.1, 1.0, 2.0)
- Plugin name already indicates Nablarch major version

## License

Apache-2.0

## Links

- Distribution Repository: https://github.com/nablarch/nabledge
- Development Repository: https://github.com/nablarch/nabledge-dev
