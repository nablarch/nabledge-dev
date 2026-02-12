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

## Usage

### Using nabledge-6 Skill

Ask questions about Nablarch 6 framework:

```
データリードハンドラでファイルを読み込むにはどうすればいいですか？
UniversalDaoでページングを実装したい
トランザクション管理ハンドラの設定方法を教えてください
```

Analyze existing code:

```
このActionクラスの構造を説明して
proman-batchモジュール全体の構造を教えてください
```

### Example Questions

See [test scenarios](.claude/skills/nabledge-6/tests/scenarios.md) for 30+ example questions covering:
- Handlers (transaction management, data reading, DB connections)
- Libraries (UniversalDao, database access, file path management)
- Tools (NTF testing framework)
- Processing (Nablarch batch architecture)
- Adapters (SLF4J logging)
- Code Analysis (understanding existing code structure)
