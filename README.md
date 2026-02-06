# nabledge-dev
Nablarch knowledge development

## 前提条件

- WSL2 / Ubuntu
- 社内プロキシ環境の場合: CA証明書

## セットアップ

### 1. CA証明書の配置（プロキシ環境の場合）

```bash
sudo cp /path/to/your/ca.crt /usr/local/share/ca-certificates/ca.crt
sudo update-ca-certificates
```

### 2. 環境構築

```bash
./setup.sh
cp .env.example .env
# Edit .env and set your credentials
```

## 作業開始

```bash
source .env
claude
```
