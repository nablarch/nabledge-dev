# Reference Answers (qa-v6)

採点の正解データ。各シナリオに対して「これが答えられれば満点」という模範回答を1本ずつ置く。

## 用途

- **Stage 2 スクリプト判定**: 模範回答の citation から正解パス集合を機械抽出し、filter の候補に含まれるかを `in` 判定。
- **Stage 3 LLM judge**: 模範回答と生成回答を並べて judge に渡し、生成回答が模範回答と同等の内容をカバーしているか 4段階判定。

## ファイル

1シナリオ1ファイル、`{scenario_id}.md`。scenario JSON の `id` とリンク。

## format（in-scope：Nablarch に機能がある場合）

```
**質問**: {質問文}

---

**結論**: {1-3文の要約}。 — `{path#sid}`

**① {観点1}**
{内容}。 — `{path#sid}`

**② {観点2}**
{内容}。 — `{path#sid}`

...

**注意点**
- {補足1}。 — `{path#sid}`
- {補足2}。 — `{path#sid}`
```

**必須要素**:
- 冒頭に `**質問**:` 行（自己完結性のため）
- `**結論**:` 行（1-3文の要約 + citation）
- citation は **全ての事実主張** に付ける。1段落に複数ソースなら複数 citation を並べる（`、` で区切る）

**任意要素**:
- ①②③… の scaffolding は質問の性質に応じて採用（単純な Yes/No 質問は結論＋注意点だけで済むこともある）
- 「注意点」セクションは補足情報があるときのみ

## format（out-of-scope：Nablarch に機能がない場合）

`req-09`（レート制限）、`req-10`（監査ログ）など、Nablarch に該当機能がない質問:

```
**質問**: {質問文}

---

**結論**: Nablarch は {feature} をビルトイン提供しない。

**最も近い機能**: {近傍機能名}。{役割の概説}。 — `{path#sid}`

**代替案**:
- {案1}。 — `{path#sid}`
- {案2}（任意）。

**注意点**
- {補足}。 — `{path#sid}`（あれば）
```

**必須要素**:
- 「ビルトイン提供しない」を明言
- 最も近い機能（near-neighbor）を1つ以上、citation 付きで提示

**判定基準**:
- judge は「ビルトインなし明言 + 近傍提示」が揃えば level 3
- 「ビルトインなし」だけで近傍提示がない、または「ビルトインあり」と誤答すれば level ≤ 1

## citation 記法

- 形式: `` `{path}#{sid}` ``（バッククォート囲み、区切りは `#`）
  - `path` 例: `processing-pattern/nablarch-batch/nablarch-batch-architecture.json`
  - `sid` 例: `s1`, `s3`
- 1段落内に複数 citation は `、` で並列（`— \`path#s1\`、\`path#s3\``）
- 段落末尾に `— ` で区切って置く（regex で抽出しやすいため）

**抽出 regex**:
```python
import re
CITATION_RE = re.compile(r'`([^`]+\.json)#(s\d+)`')
# 使い方: for path, sid in CITATION_RE.findall(answer_md): ...
```

## 書き方のガイド

1. 質問を読み、scenario JSON の `expected_sections` にあるセクションを読む（ここが主要ソース）
2. 関連する他の知識ファイルも grep で探す（expected_sections は最低限で、他にも citation すべき内容があることが多い）
3. 「Nablarch ユーザーがこの回答だけで実装に動ける」レベルまで具体化（クラス名、メソッド名、アノテーション、設定項目名までは書く。行番号やフルパッケージ名までは書かない）
4. **citation は事実主張ごと**。「A と B と C をする」を1文で書いても、A/B/C が別ソースなら分割して書くか、段落末に3つ citation を並べる
5. 知識ファイルに書かれていない内容は書かない（外部知識の混入禁止）
6. 書いたら Prompt Engineer sub-agent にレビュー依頼（初回と、書き方が揺れたと感じたとき）
