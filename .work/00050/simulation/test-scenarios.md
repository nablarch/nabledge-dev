# Test Scenarios

## Knowledge Search Tests (10 scenarios)

1. "ページングを実装したい"
2. "バリデーションエラーの処理方法"
3. "RESTful APIの作成"
4. "バッチ処理の実装"
5. "トランザクション管理"
6. "ファイルアップロード"
7. "データベース接続"
8. "フォームのバリデーション"
9. "エラーハンドリング"
10. "セッション管理"

## Code Analysis Tests (10 scenarios)

Would require actual Java source files from a Nablarch project. Since this repository doesn't contain sample Nablarch application code, code analysis tests will validate the workflow instructions are executable but won't measure actual timing.

## Measurement Methodology

For each knowledge search:
1. Record start time
2. Execute nabledge-6 knowledge search workflow
3. Record end time
4. Count tool calls during execution
5. Verify output accuracy against expected results
6. Calculate tool call overhead percentage

Results saved to: `.pr/00050/simulation/results.md`
