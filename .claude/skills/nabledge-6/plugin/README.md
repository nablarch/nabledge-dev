# Nabledge-6 Plugin

Nablarch 6 skill for AI-assisted development.

## Features

- **Knowledge Search**: Search Nablarch 6 documentation and best practices
- **Code Analysis**: Analyze application code from Nablarch perspective

## Installation

### For Claude Code (WSL)

```bash
/plugin marketplace add nablarch/nabledge
```

### For GitHub Copilot (WSL or GitBash)

```bash
curl -sSL https://raw.githubusercontent.com/nablarch/nabledge/main/.claude/skills/nabledge-6/scripts/setup.sh | bash
```

## Usage

### Basic Usage

```bash
/nabledge-6
```

### Knowledge Search

```bash
/nabledge-6 "How do I implement batch processing?"
```

### Code Analysis

```bash
/nabledge-6 code-analysis
```

## Scope

### Nablarch Version
- Nablarch 6u3

### Supported Features
- On-demand Batch (FILE to DB, DB to DB, DB to FILE)
- RESTful Web Services (JAX-RS)
- Handlers and Libraries
- Tools and Testing

### Out of Scope
- Jakarta Batch
- Resident Batch (Table Queue)
- Web Applications (JSP/UI)
- Messaging (MOM)

## Versioning

This plugin uses a `minor.patch` versioning scheme:
- **Minor** (first digit): Incremented for feature additions (e.g., 0.1 → 1.0 → 2.0)
- **Patch** (second digit): Incremented for bug fixes and small changes (e.g., 0.1 → 0.2, 1.0 → 1.1)

The plugin name `nabledge-6` already indicates the major version (Nablarch 6), so the plugin version itself uses a simplified two-digit format. This approach keeps versioning straightforward while maintaining clear compatibility with Nablarch 6.

## License

Apache-2.0

## Links

- Distribution Repository: nablarch/nabledge
- Development Repository: nablarch/nabledge-dev
