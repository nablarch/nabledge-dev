# Phase 1: Unlock Your Assets (v2)

## 概要

Unlockフェーズの全体構造と情報の流れを示したダイアグラム。既存システムに眠る暗黙知と業務ルールを、AIが使える形に変換するプロセスを可視化している。

## ダイアグラムの見方

- **青系（濃青・明青）**: Nabledgeのコア機能とNablarchチーム
- **赤系**: 既存資産（★濃赤=起点となるソースコード）
- **橙系**: PJアダプター（汎用・PJ固有）
- **紫系**: Unlockの出力（知識・マッピング）
- **ピンク系**: 不整合リスト（対話ループのトリガー）
- **緑系**: 開発ガイド（Unlockの核心成果物）
- **グレー系**: 次フェーズ（Phase 2: Build）への接続

## 主要な流れ

1. **起点**: ソースコード（#5）を汎用アダプターで解析
2. **構造化**: 既存資産をPJアダプター（汎用・PJ固有）で構造化
3. **変換**: Nabledgeが知識・マッピング・不整合リストを生成
4. **対話**: 不整合リストを起点にロール別の対話ループで知識を確定
5. **核心成果**: 現行の開発ガイド導出 → AI-Readyの開発ガイド作成
6. **次フェーズ**: 開発ガイド・知識・マッピングがBuildの基盤になる

```mermaid
---
title: "Phase 1: Unlock Your Assets (v2)"
---
graph TB
  %% ===== Unlockの核心：開発ガイド整備 =====
  subgraph CORE["Unlockの核心：開発ガイドの整備"]
    direction TB
    GUIDE_AS_IS["現行の開発ガイド<br/>今のPJが実際にどう作っているか"]
    GUIDE_AI["AI-Readyの開発ガイド<br/>Nablarch上でどう作るか<br/>方式設計＋開発標準＋手順を統合<br/>変更はアーキテクト承認"]
    GUIDE_AS_IS -->|"Nabチームの知識で変換"| GUIDE_AI
  end

  %% ===== 起点：ソースコード解析 =====
  CODE["ソースコード（#5）<br/>Java / SQL / XML / テストコード<br/>動いている＝検証済みの事実<br/>★ Unlockの起点"]

  %% ===== 既存資産（補助情報・検証対象） =====
  DESIGN_EXT["設計書・外部設計（#2）<br/>機能設計、画面設計<br/>バッチ外部仕様、IF定義"]
  DESIGN_INT["設計書・内部設計（#3）<br/>クラス設計、SQL設計<br/>開発ガイド充実なら薄い"]
  REQ["要件定義書（#1）<br/>スコープ、目的、目標値<br/>業務フロー、業務ルール"]
  TEST["テスト仕様書 / テストデータ（#6,#7）"]
  OTHER["不具合票 / チェックリスト<br/>工数見積（#8,#9,#10）"]

  %% ===== PJアダプター（2層） =====
  AD_GEN["汎用アダプター<br/>Nabチームが提供<br/>ソースコード・テーブル定義・<br/>マスタテーブルから業務仕様を<br/>機械的に抽出"]
  AD_PJ["PJ固有アダプター<br/>アーキテクトが設定<br/>業務仕様の所在を指定"]

  %% ===== Nabledge =====
  NE["Nabledge<br/>知識 x ワークフロー x 実績"]

  %% ===== Unlockの出力（3種） =====
  KNOWLEDGE["知識（JSON）<br/>抽出・検証・確定した情報"]
  MAPPING["マッピング（JSON）<br/>① 知識↔元成果物<br/>② 成果物間の依存（テーブル単位）<br/>③ 知識間の関係"]
  GAPS["不整合リスト<br/>コード↔設計書の矛盾<br/>規約↔実態の乖離"]

  %% ===== 知識供給 =====
  NAB["Nablarch<br/>規約・品質基準・テスト規約"]
  TEAM["Nabチーム<br/>知識・ワークフロー構築<br/>汎用アダプター提供"]

  %% ===== ロール =====
  ARCH["アーキテクト"]
  DESIGNER["要件定義者/設計者"]
  APPENG["アプリケーションエンジニア"]

  %% ===== Buildへの接続 =====
  BUILD["Phase 2: Build Like Experts<br/>カラム単位の依存特定は<br/>Build時にNabledgeが動的解析"]

  %% ===== ソースコード → 汎用アダプター（起点） =====
  CODE ==>|"★ 起点：コード解析"| AD_GEN
  TEST -->|"解析"| AD_GEN

  %% ===== 補助情報 → PJ固有アダプター =====
  DESIGN_EXT -->|"補助情報"| AD_PJ
  DESIGN_INT -.->|"開発ガイド充実なら<br/>マッピングのみ"| AD_PJ
  REQ -.->|"業務的意味の補足"| AD_PJ
  OTHER -->|"読解"| AD_PJ

  %% ===== アダプター → Nabledge → 出力 =====
  AD_GEN -->|"構造化"| NE
  AD_PJ -->|"構造化"| NE
  NE --> KNOWLEDGE
  NE --> MAPPING
  NE --> GAPS

  %% ===== 構造把握 → 開発ガイド導出 =====
  MAPPING -->|"構造から導出"| GUIDE_AS_IS
  KNOWLEDGE -->|"知識から導出"| GUIDE_AS_IS

  %% ===== 知識供給 =====
  NAB -->|"FW知識"| NE
  TEAM -->|"ワークフロー"| NE
  TEAM -->|"提供"| AD_GEN
  TEAM -->|"Nablarch化の知識"| GUIDE_AI
  ARCH -->|"PJ固有の構造定義"| AD_PJ
  ARCH -->|"変更承認"| GUIDE_AI

  %% ===== 不整合 → 対話ループ =====
  GAPS -->|"矛盾の確認"| ARCH
  GAPS -->|"設計意図の確認"| DESIGNER
  GAPS -->|"実装意図の確認"| APPENG
  ARCH -->|"回答"| NE
  DESIGNER -->|"回答"| NE
  APPENG -->|"回答"| NE

  %% ===== 対話結果の反映 =====
  NE -->|"確定"| KNOWLEDGE
  NE -->|"確定"| MAPPING

  %% ===== Buildへの接続 =====
  GUIDE_AI -->|"Buildの判断基準"| BUILD
  KNOWLEDGE -->|"判断基準"| BUILD
  MAPPING -->|"影響分析の基盤<br/>（テーブル単位）"| BUILD

  %% ===== スタイル =====
  classDef core fill:#1a73e8,stroke:#0d47a1,color:#fff
  classDef base fill:#4285f4,stroke:#1a73e8,color:#fff
  classDef asset fill:#fce4ec,stroke:#c62828,color:#b71c1c
  classDef asset_main fill:#ffcdd2,stroke:#b71c1c,color:#b71c1c,stroke-width:3px
  classDef adapter fill:#fff3e0,stroke:#e65100,color:#bf360c
  classDef output fill:#e8eaf6,stroke:#283593,color:#1a237e
  classDef gap fill:#ffebee,stroke:#b71c1c,color:#b71c1c
  classDef dev fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20
  classDef next fill:#f5f5f5,stroke:#9e9e9e,color:#616161
  classDef guide fill:#c8e6c9,stroke:#1b5e20,color:#1b5e20,stroke-width:3px

  class NE core
  class NAB,TEAM base
  class DESIGN_EXT,DESIGN_INT,REQ,TEST,OTHER asset
  class CODE asset_main
  class AD_GEN,AD_PJ adapter
  class KNOWLEDGE,MAPPING output
  class GAPS gap
  class ARCH,DESIGNER,APPENG dev
  class BUILD next
  class GUIDE_AS_IS,GUIDE_AI guide
```
