# Test: processing-005

**Date**: 2026-02-26 16:06:24
**Question**: バッチの起動方法を教えてください

## Scenario
- **Keywords** (5): -requestPath, コマンドライン引数, アクションのクラス名, リクエストID, 都度起動
- **Sections** (2): request-path, batch-types

## Results

**Pass Rate**: 8/8 (100%)

### Expectations
- ✓ Response includes '-requestPath'
  - Evidence: Answer contains: '-requestPath=アクションのクラス名/リクエストID' and '`-requestPath`オプションで'
- ✓ Response includes 'コマンドライン引数'
  - Evidence: Answer contains: 'コマンドライン引数でアクションとリクエストIDを指定' and 'コマンドライン引数の指定' section heading
- ✓ Response includes 'アクションのクラス名'
  - Evidence: Answer contains: '-requestPath=アクションのクラス名/リクエストID'
- ✓ Response includes 'リクエストID'
  - Evidence: Answer contains multiple occurrences including 'リクエストIDの役割' section and format specification
- ✓ Response includes '都度起動'
  - Evidence: Answer contains: '都度起動バッチ' section heading and '都度起動バッチ：定期的にプロセスを起動'
- ✓ Response mentions 'request-path' or 'batch-types' sections
  - Evidence: Both sections cited in 参考 section: 'knowledge/features/processing/nablarch-batch.json#request-path' and 'knowledge/features/processing/nablarch-batch.json#batch-types'
- ✓ Token usage is between 5000 and 15000
  - Evidence: Total tokens: 9,480 (within range 5000-15000)
- ✓ Tool calls are between 10 and 20
  - Evidence: Total tool calls: 10 (within range 10-20)

## Metrics
- **Duration**: 62s (executor) + 6s (grader) = 68s total
- **Tool Calls**: 10 (Read: 3, Bash: 7, Grep: 0)
- **Response Length**: 1,626 chars
- **Tokens**: 9,480 tokens (IN: 6,780, OUT: 2,700)

### Token Usage by Step
| Step | Name | IN Tokens | OUT Tokens | Total | Duration |
|------|------|-----------|------------|-------|----------|
| 1 | Extract Keywords | 15 | 50 | 65 | 1s |
| 2 | Match Files | 2,500 | 100 | 2,600 | 1s |
| 3 | Extract Section Hints | 150 | 800 | 950 | 1s |
| 4 | Score Section Relevance | 800 | 100 | 900 | 1s |
| 5 | Sort and Filter | 1,000 | 800 | 1,800 | 1s |
| 6 | Read Section Content | 50 | 1,100 | 1,150 | 2s |
| 7 | Judge Relevance (Final) | 1,100 | 50 | 1,150 | 1s |
| 8 | Generate Answer | 1,150 | 650 | 1,800 | 55s |

## Transcript
See: .tmp/nabledge-test/eval-processing-005-160617/with_skill/outputs/transcript.md

## Grading
See: .tmp/nabledge-test/eval-processing-005-160617/with_skill/grading.json
