# Changelog

All notable changes to the nabledge-6 plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Changed
- Migrated to Claude Code marketplace distribution structure
- Plugin now distributed via marketplace catalog (nablarch/nabledge)
- Users should install via: `/plugin marketplace add nablarch/nabledge` then `/plugin install nabledge-6@nabledge`
- Simplified license management: single LICENSE at repository root applies to entire marketplace

### Fixed
- Fix plugin.json schema to comply with Claude Code specification
  - Changed author from string to object format
  - Changed repository from object to string format
  - Removed unsupported engines field

## [0.1] - 2026-02-12

### Added
- Initial release of nabledge-6 skill
- Knowledge search functionality for Nablarch 6 documentation
- Code analysis capability with structured templates
- Basic batch processing knowledge
- Database access libraries
- Testing framework basics
- Security checklist

[0.1]: https://github.com/nablarch/nabledge/releases/tag/v0.1
