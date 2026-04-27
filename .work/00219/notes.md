# Notes

## 2026-03-24

### Preview: Nabledge Adoption セクション出力イメージ

サンプルデータで生成した `docs/metrics.md` の Adoption セクション。
実際のデータで workflow を手動実行すると以下の形式で出力される。

---

## Nabledge Adoption (nablarch/nabledge)

```mermaid
xychart-beta
  title "Page Views (weekly)"
  x-axis ["03/09", "03/16", "03/23"]
  y-axis "Views" 0 --> 76
  bar [45, 63, 44]
```

```mermaid
xychart-beta
  title "Unique Visitors (weekly)"
  x-axis ["03/09", "03/16", "03/23"]
  y-axis "Visitors" 0 --> 35
  bar [22, 29, 20]
```

```mermaid
xychart-beta
  title "Git Clones (weekly)"
  x-axis ["03/09", "03/16", "03/23"]
  y-axis "Clones" 0 --> 10
  bar [6, 7, 8]
```

---

### Decision: 週次集計・表なし・Unique Visitors グラフ追加

- 日次だと粒度が細かすぎてトレンドが見づらい → 他のグラフと同じ週次に統一
- サマリーテーブルは削除（グラフで十分）
- Unique Visitors をグラフ化（Page Views と同じ x-axis で並べて比較しやすい）
- Unique Visitors の週次値は日次の合計（同一人物の重複カウントあり、上限値として参照）
