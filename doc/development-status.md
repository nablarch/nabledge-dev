# Nabledge 開発状況

最終更新: 2026-02-24

## トレードオフスライダー

| 項目 | 固定 ← → 調整可能 | 意味 |
|------|:---:|------|
| リリース速度 | ■ □ □ □ □ | 早く出す。新規＞改善 |
| 導入の手軽さ | ■ □ □ □ □ | 導入障壁が高いと使われない |
| 知識のカバー範囲 | ■ □ □ □ □ | v6/v5のバッチ＞REST優先、1.4以前は後回し |
| 検索・回答の精度 | □ □ □ □ ■ | まず広く出して、精度は使われてから磨く |
| ワークフローの充実度 | □ □ □ □ ■ | まず知識検索で価値を証明してから追加 |

※ 知識ファイルは生成AIで生成・検証し人はサンプリングチェックのみ実施、正式リリース前に全量チェックを予定している

## ロードマップ

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'primaryColor':'#e5e7eb', 'primaryTextColor':'#1f2937', 'primaryBorderColor':'#d1d5db', 'secondaryColor':'#f3f4f6', 'tertiaryColor':'#9ca3af', 'background':'#ffffff', 'mainBkg':'#e5e7eb', 'secondBkg':'#f9fafb', 'activeBkg':'#4f46e5', 'activeTextColor':'#ffffff', 'activeBorderColor':'#4338ca', 'doneBkg':'#6b7280', 'doneTextColor':'#ffffff', 'doneBorderColor':'#4b5563', 'critBkg':'#f59e0b', 'critTextColor':'#ffffff', 'critBorderColor':'#d97706', 'todayLineColor':'#dc2626', 'gridColor':'#f3f4f6', 'fontFamily':'-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif', 'fontSize':'13px'}}}%%
gantt
    title Nabledge Roadmap 2026-2027
    dateFormat YYYY-MM-DD

    section 評価版＆ツール整備
    Nabledge評価版の開発             :done, 2026-02-01, 2026-02-14
    知識生成ツールの開発             :done, 2026-02-15, 2026-02-28

    section 知識拡充
    Nablarch v6/v5の知識生成        :active, 2026-03-01, 2026-03-14
    Nablarch v1.4/v1.3/v1.2の知識生成 :active, 2026-03-15, 2026-03-28

    section ワークフロー拡充
    ワークフロー拡充＆Nablarch改善    :2026-03-29, 2026-04-25
    GW                             :crit, 2026-04-26, 2026-05-09
    ワークフロー拡充＆Nablarch改善    :2026-05-10, 2026-05-31

    section AI-Ready Nablarch/Nabledgeリリース
    品質向上＆リリース準備                        :2026-06-01, 2026-06-29
    AI-Ready Nablarch/Nabledgeリリース          :milestone, 2026-06-30, 0d

    section 市場拡大に向けたSoR→Nablarch移行サービスNableapの開発
    Nableap評価版の開発             :2026-07-01, 2026-09-30
    Nableapの開発                  :2026-10-01, 2026-12-26
    年末年始休暇                    :crit, 2026-12-27, 2027-01-09
    Nableapリリース                :2027-01-10, 2027-03-31
```

## 現在の作業 (今週)

- 知識ファイル生成/検証整備
- バッチの追加
  - スコープ詳細: [nabledge-design.md § 1.5 スコープ](nabledge-design.md#15-スコープ) を参照

## 次の作業 (来週)

- チェック項目の追加
  - 詳細: [nabledge-design.md § 2.2 知識タイプ](nabledge-design.md#22-知識タイプ) を参照
- NTF（Nablarch Testing Framework）の追加

## 今後の作業 (4Q)

- RESTの追加
- 過去バージョン（1.4/1.3/1.2）の追加

## 今後の作業 (4月以降)

- 利用PJからのフィードバック対応
- ワークフローの追加
- PJ実績を積み重ねてから正式リリース（PJ利用状況次第、6月or9月頃）
