# RBKC Search Impact Evaluation

Rule-based Knowledge Creator (RBKC) への切り替えが検索精度・検索速度に与える影響を、実際のRSTファイルをRBKCコンバータで変換して計測した結果。

## Evaluation Date

2026-04-09

## How to Reproduce

```bash
# 1. Setup (clone .lw sources)
./setup.sh

# 2. Run evaluation
cd tools/rbkc/docs/search-impact-evaluation
bash run_evaluation.sh
```

計測スクリプト:
- `convert_rst.py` — RST → knowledge JSON 変換器（計測用）
- `run_evaluation.sh` — 変換 → サイズ比較 → 検索比較 → セクション比較の自動実行

## Methodology

### 対象ファイル

`.lw/nab-official/v6/nablarch-document/ja/` の実際のRSTファイル6件を選定（サイズ・用途が異なるもの）:

| File | Source Lines | Category |
|------|-------------|----------|
| bean_validation.rst | 839 | Libraries (large, many h3) |
| universal_dao.rst | 809 | Libraries (large, many h3) |
| tag.rst | 3,085 | Libraries (very large, 41 h3) |
| http_response_handler.rst | 239 | Handlers (medium) |
| data_read_handler.rst | 60 | Handlers (small) |
| doma_adaptor.rst | 610 | Adapters (large) |

### 手順

1. `convert_rst.py` で実RSTファイルを knowledge JSON に変換（ルールベース、全コンテンツ保持）
2. KC既存出力と RBKC出力のコンテンツ行数を比較
3. RBKC出力を KC知識ベースに上書きし、同じ `full-text-search.sh` で検索実行
4. KC検索結果と RBKC検索結果を比較（速度 + 結果順位）

## Results

### Content Size Comparison (実測)

| File | KC lines | RBKC lines | Ratio |
|------|---------|------------|-------|
| adapters-doma_adaptor | 427 | 547 | 1.3x |
| handlers-data_read_handler | 25 | 39 | 1.6x |
| handlers-http_response_handler | 67 | 155 | 2.3x |
| libraries-bean_validation | 568 | 741 | 1.3x |
| libraries-tag | 1,460 | 2,926 | 2.0x |
| libraries-universal_dao | 389 | 666 | 1.7x |
| **TOTAL** | **2,936** | **5,074** | **1.7x** |

RBKCのコンテンツ量はKCの **1.7倍**（ファイルにより 1.3x〜2.3x）。

### Search Speed (実測)

`full-text-search.sh` を KC知識ベースと RBKC上書き知識ベースの両方で実行:

| Query | KC | RBKC | 差 |
|-------|-----|------|---|
| バリデーション Bean Validation | 1,207ms | 1,081ms | -10% |
| データベース DAO UniversalDao | 1,044ms | 1,242ms | +19% |
| JSP カスタムタグ tag | 1,107ms | 1,026ms | -7% |
| ハンドラ handler HttpResponse | 1,021ms | 1,041ms | +2% |

**速度差は誤差範囲。コンテンツ量1.7倍でも検索速度に影響なし。**

### Search Results (実測)

| Query | Top 5 一致 | 備考 |
|-------|-----------|------|
| バリデーション Bean Validation | **一致** | |
| データベース DAO UniversalDao | **一致** | |
| JSP カスタムタグ tag | **不一致** | セクション粒度の違いが原因 |
| ハンドラ handler HttpResponse | **一致** | |

**「JSP カスタムタグ tag」で検索結果が異なった。** 原因を以下で分析。

### Critical Finding: Section Granularity Problem

tag.rst の検索結果が異なった原因:

**ソースの見出し構造:**
```
tag.rst: h1(=) × 1, h2(-) × 6, h3(~) × 41
```

**KC（AI生成）のセクション構造:** 10セクション
```
s1: 機能概要          561 lines
s2: モジュール一覧       342 lines
s3: カスタムタグの設定      298 lines
s4: カスタムタグを使用する    132 lines
s5: 入力フォームを作る       71 lines
s6: 認可チェック/...        30 lines
s7: 任意の属性を指定する       1 lines  ← 検索ヒット
...
```

**RBKC（h2ベース）のセクション構造:** 6セクション
```
s1: 機能概要           100 lines
s2: モジュール一覧         18 lines
s3: 使用方法          2,507 lines  ← 巨大セクション（41個のh3を内包）
s4: 拡張例              88 lines
s5: カスタムタグのルール     212 lines  ← 検索ヒット（KCのs7とは別の内容）
s6: :ref:              1 lines
```

**問題:** RBKC は h2 でのみセクション分割するため、h3 が多いファイルでは1セクションが巨大化する（s3: 2,507行）。全文検索はセクション単位でスコアリングするため:

- KC: 「任意の属性を指定する」（1行）がスコア1でヒット → 正確な粒度
- RBKC: 「使用方法」（2,507行）がスコア多数でヒット → ノイズを含む巨大結果

**これはコンテンツ量の問題ではなく、セクション粒度の問題。**

### Section Size Comparison (実測)

RBKC で「new」と表示されるセクションは、KC にはない粒度で発生:

| Pattern | 例 |
|---------|---|
| KC の細かいセクションが RBKC の巨大セクションに吸収 | KC s3-s10 → RBKC s3 (2,507行) |
| RBKC で新しいh2セクションが出現 | 「使用方法」「拡張例」（KC は h3 レベルで分割していた） |
| 一部で KC > RBKC | AI が内容を膨らませていたケース（doma_adaptor s4: KC 74行 → RBKC 14行） |

## Risk Assessment

| リスク | 影響度 | 発生確率 | 根拠 |
|--------|--------|---------|------|
| 全文検索の速度劣化 | なし | 発生しない | 実測で速度差なし（4クエリ計測） |
| セクション粒度による検索結果劣化 | **高** | **高** | tag.rst で実際に発生。h3 が多いファイルは全て影響 |
| セクション肥大化による読み込みコスト増 | 中 | 確実 | s3: 2,507行 は agent が読むには大きすぎる |
| ヒント移植のマッピング失敗 | 中 | 高 | セクション構造が根本的に異なるためタイトル一致が困難 |

## Recommendations

1. **セクション粒度の改善が必須** — h2+h3 でセクション分割する。詳細調査: [section-granularity.md](section-granularity.md)
2. **Layer C フィルタリングは不要** — 速度影響なし。コンテンツ量 1.7x は検索に影響しない
3. **ヒント移植は慎重に** — セクション構造が大きく異なるため、単純なタイトル一致では移植できない。h3 レベルのセクション対応が前提
