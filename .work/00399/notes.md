# Notes

## 2026-07-10

### Decision: リファクタリングコミット(c1a37ad7)はCHANGELOGから除外

code-analysis.mdの書き直しはAIへの指示の整合性改善のみで、ユーザーが受け取る出力は変わらない。
`changelog.md`の「ユーザー影響が明確に示せないものは除外」方針に基づき除外。

### Problem: ローカルがorigin/mainより1コミット遅れていた

セッション開始時に`git fetch`を省略したため、`d5ca70e3`（section links追加）を見落とした。
`release.md` Step 1に`git fetch origin main`を追加して修正済み。

### Finding: release.mdのsetupスクリプトパスが実際と乖離

release.mdには`setup-6-cc.sh`等と書かれていたが、実際のsync-manifestは`setup-cc.sh`/`setup-ghc.sh`。
あわせてv1.x系のcommands/promptsも未記載だったため修正。

### Decision: CHANGELOGエントリはqa・code-analysis両方を記載

d5ca70e3はqa.md（参照欄）とcode-analysis/template-guide.md（詳細リンク）の両方を変更。
最初のエントリはqaのみを書いていたが、Craft/Verificationレビューで指摘され修正。
