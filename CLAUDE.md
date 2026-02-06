# nabledge-dev

言語は日本語

## 概要

このリポジトリは **Nablarchエージェント用の構造化知識基盤（スキル）** を作成・管理するためのものです。

- **nabledge-6**: Nablarch 6（Jakarta EE 10、Java 17以上）用のスキル
- **nabledge-5**: Nablarch 5（Java EE 7/8、Java 8以上）用のスキル

AI（Claude Code / GitHub Copilot）がNablarch開発を代行するための構造化された知識を提供します。

---

## ディレクトリ構成

```
nabledge-dev/
├── .claude/
│   └── skills/
│       ├── nabledge-6/            # Nablarch 6 スキル（作成予定）
│       └── nabledge-5/            # Nablarch 5 スキル（作成予定）
│
├── .lw/
│   ├── research/                  # 調査・設計ドキュメント
│   └── nab-official/              # Nablarch公式情報（クローン）
│
└── CLAUDE.md                      # このファイル
```

---

## 対象範囲

### 対象

| 項目 | 説明 |
|-----|------|
| **Nablarchバッチ（都度起動型）** | FILE to DB、DB to DB、DB to FILE パターン |
| **RESTful Webサービス** | JAX-RSサポート、REST API実装 |

### 対象外

| 項目 | 理由 |
|-----|------|
| Jakarta Batch | 仕様書で対象外と明記 |
| 常駐バッチ（テーブルキュー型） | 仕様書で対象外と明記 |
| ウェブアプリケーション（JSP/画面系） | バッチ・REST以外は対象外 |
| メッセージング（MOM） | 対象外 |

---

## 詳細設計

スキルの詳細なアーキテクチャ設計は以下を参照：

- [Step 3: 構造化アーキテクチャ設計](.lw/research/step3-architecture-design.md)
