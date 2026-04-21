Closes #252

## Approach

v1.x (v1.4, v1.3, v1.2) テスト環境が SVN 由来の tutorial ディレクトリを使用していたため、`.git` がなく、CC/GHC の CLI がプロジェクトルート判定に失敗していた。

**解決策**: v1.x も v6 の `nablarch-example-batch` をベースプロジェクトとして使用
- 理由: 動的チェック（ナレッジ検索）は読み取り専用操作のため、v1.x でも v6 ベースで十分
- 効果: プロジェクトルート判定が安定し、テスト環境構成が単純化
- 削除: v1.x SVN 参照（setup.sh での tutorial チェックアウト不要に）

## Tasks

- [x] `tools/tests/test-setup.sh` で setup_env, verify_env, verify_dynamic 呼び出し更新
- [x] v1.x 用の不要な PROJECT_SRC と HINT 変数削除
- [x] 関連コメント更新（SVN 参照削除）
- [x] Syntax チェック＆tutorial 参照ゼロ確認
- [ ] `bash tools/tests/test-setup.sh` で検証実行（明日実施予定）
- [ ] Expert Review

## Changes

### tools/tests/test-setup.sh

#### setup_env 呼び出し（行167-172）
```diff
-should_run "v1.4" && setup_env "v1.4/test-cc"  "$V14_PROJECT_SRC" "tutorial"    ...
+should_run "v1.4" && setup_env "v1.4/test-cc"  "$V6_PROJECT_SRC"  "nablarch-example-batch" ...
```

#### verify_env 呼び出し（行385-390）
```diff
-should_run "v1.4" && verify_env "v1.4/test-cc"  "v1.4/test-cc/tutorial"    "1.4" ...
+should_run "v1.4" && verify_env "v1.4/test-cc"  "v1.4/test-cc/nablarch-example-batch" "1.4" ...
```

#### verify_dynamic 呼び出し（行401-406）
```diff
-should_run "v1.4" && verify_dynamic "v1.4/test-cc"  "v1.4/test-cc/tutorial"    "1.4" ...
+should_run "v1.4" && verify_dynamic "v1.4/test-cc"  "v1.4/test-cc/nablarch-example-batch" "1.4" ...
```

#### クリーンアップ
- 削除: `V14_PROJECT_SRC`, `V13_PROJECT_SRC`, `V12_PROJECT_SRC` 変数
- 削除: `HINT_V14`, `HINT_V13`, `HINT_V12` 変数
- 更新: コメント（SVN 参照削除）

## Success Criteria

- [x] Bash syntax チェック: OK
- [x] tutorial 参照ゼロ: grep -c 'tutorial' = 0
- [ ] 検証実行で全20行が [OK] または detection rate 50%以上
- [ ] 既存テスト・動作の劣化なし

## Notes

**残りの作業は明日に予定**:
1. `bash tools/tests/test-setup.sh` で実際の検証実行
2. Expert Review (Software Engineer)
3. PR本文最終化＆merge

**技術的背景**: `.claude/rules/expert-review.md` 参照

🤖 Generated with [Claude Code](https://claude.com/claude-code)
