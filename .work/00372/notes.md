# Notes

## 2026-06-18

### Step 1: Commit analysis since marketplace 0.9 (2026-05-26)

Commits since last release (`dae955b59` = marketplace 0.9 / 2026-05-26):

| Hash | Title | Deployed content? | Impact |
|------|-------|-------------------|--------|
| `11b6bdf0d` | feat: generate classes.md for class-name-based page selection (#368) (#369) | ✅ Yes | nabledge-6/5/1.4/1.3/1.2: knowledge/classes.md 追加、workflows/qa.md + semantic-search.md 変更 |
| `26f2471ef` | chore: update metrics report (20260614) (#371) | ❌ No | docs/ のみ |
| `f87c8231e` | chore: update metrics report (20260607) (#370) | ❌ No | docs/ のみ |
| `f67fc9392` | docs: add task plan for Javadoc knowledge integration (#363) (#365) | ✅ Yes | nabledge-6/5/1.x の knowledge/*.json と docs/*.md が大量更新（4217ファイル）。コミットメッセージは "task plan" だが実体は knowledge/docs の大規模更新。PR #365 の本体 |
| `a0d0f3814` | feat: add DeepEval RAG metrics to benchmark pipeline (#361) (#362) | ❌ No | tools/benchmark のみ（dev-only） |
| `e9125d218` | chore: update metrics report (20260531) (#367) | ❌ No | docs/ のみ |
| `869800a43` | docs: limit dependency graph to 15 classes in code-analysis workflow (#176) (#366) | ✅ Yes | nabledge-6/5/1.4/1.3/1.2: workflows/code-analysis.md 変更（依存グラフ上限 15件） |
| `f8609535f` | docs: tighten Success Criteria rule (#360) | ❌ No | .claude/rules/ のみ |
| `bc3a5e921` | fix: eliminate false-positive FAILs in dynamic check (#358) (#359) | ❌ No | tools/tests のみ |
| `c87adbcfc` | feat: test-setup.sh branch selection, metrics (#354) (#355) | ❌ No | tools/tests のみ |
| `50ef3a423` | docs: show hyphen for unchanged plugins in marketplace CHANGELOG (#356) (#357) | ⚠️ marketplace/CHANGELOG.md のみ（表示ルール変更、内容変更なし） |
| `dae955b59` | docs: add tasks.md for nabledge release (#352) (#353) | ⚠️ これが marketplace 0.9 自体（リリース済み） |

**デプロイコンテンツに影響するコミット（ユーザー向け変更）**:

1. **`11b6bdf0d`** — classes.md 追加（全5バージョン）+ semantic-search.md 2経路マージ設計 + qa.md 上限20
   - nabledge-6: knowledge/classes.md, workflows/qa.md, workflows/semantic-search.md
   - nabledge-5: 同上
   - nabledge-1.4/1.3/1.2: 同上（classes.md は空内容 "_No class index available_"）

2. **`f67fc9392`** — Javadoc 知識統合 (#363 / PR #365) — 大規模 knowledge/docs 更新
   - nabledge-6/5: knowledge/javadoc/*.json 追加、既存 knowledge JSON に javadoc リンク追加、docs/javadoc/*.md 追加
   - nabledge-1.2/1.3/1.4: knowledge/*.json と docs/*.md の更新（issue #363 では v1.x は javadoc スコープ外とのことだが、このコミットで何が変わったか要詳細確認）

3. **`869800a43`** — code-analysis.md 依存グラフ上限 15件（全5バージョン）

### f67fc9392 の詳細確認が必要

コミットメッセージ "docs: add task plan for Javadoc knowledge integration (#363)" は PR #365 のマージコミット。
PR #365 の body を見ると「docs フォルダと knowledge フォルダの大規模更新」= Javadoc 知識の本体実装。
変更ファイル 4217件（deployed content のみ）は大規模更新。

### 現在の CHANGELOG 状態

- nabledge-6: `[Unreleased]` セクションなし。最終リリース `[0.8] - 2026-05-26`
- nabledge-5: `[Unreleased]` セクションなし。最終リリース `[0.3] - 2026-05-26`
- nabledge-1.4/1.3/1.2: `[Unreleased]` セクションなし。最終リリース `[0.2] - 2026-05-26`

→ 全バージョンに [Unreleased] セクション追加が必要
