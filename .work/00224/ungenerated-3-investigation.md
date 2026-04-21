# 未生成3件 調査結果

**対象実行**: 20260324T235810
**調査日**: 2026-03-25

---

## 対象ファイル

| ファイルID | ソースファイル | ライン数 |
|-----------|-------------|--------|
| `about-nablarch-02_I18N--s1` | `document/fw/01_SystemConstitution/02_I18N.rst` | 168行 |
| `libraries-file_upload_utility--s1` | `document/fw/common_library/file_upload_utility.rst` | 392行 |
| `libraries-mail--s6` | `document/fw/core_library/mail.rst` の 305-699行目 | 394行 |

---

## CCログ・エラーログが残らない理由

`common.py` の `run_claude()` 関数は `.in.txt` のみ事前に保存し、`.json` 実行ログは CC の
`subprocess.run()` が returncode=0 で終了した場合にのみ保存する設計になっている。

エラー時は `generate/{file_id}.json` に `"status": "error", "error": ""` を記録するだけで、
CC プロセスのログ（`.json`、`.out.json`、`.ndjson`）は一切保存されない。

**エラーメッセージが空の理由**: Claude CLI が非ゼロの returncode で終了した際、stderr が空だったため。
CLIの内部エラーや無応答終了時はstderrに何も出力されない。

### ファイルの存在状況

```
phase-b/executions/about-nablarch-02_I18N--s1_20260325-025529.in.txt    ← 存在（事前保存）
phase-b/executions/about-nablarch-02_I18N--s1_*.json                    ← 存在しない
generate/about-nablarch-02_I18N--s1.json                                ← {"status": "error", "error": ""}
```

---

## 根本原因：実行時間超過（約31〜34分）

### タイムライン

| ファイル | 開始時刻 | エラー時刻 | 経過時間 |
|---------|---------|-----------|--------|
| `about-nablarch-02_I18N--s1` | 02:55:29 | 03:29:19 | **33.8分（2030秒）** |
| `libraries-file_upload_utility--s1` | 02:58:16 | 03:29:18 | **31.0分（1862秒）** |
| `libraries-mail--s6` | 02:58:58 | 03:29:50 | **30.9分（1852秒）** |

### 成功ファイルとの比較

Phase B で成功した 549 件の最長実行時間（上位5件）：

| ファイルID | 実行時間 |
|-----------|--------|
| `about-nablarch-glossary--s1` | 1503秒（25.1分） |
| `ui-framework-jsp_page_templates--s1` | 1237秒（20.6分） |
| `libraries-05_ServiceAvailability--s1` | 853秒（14.2分） |
| `web-application-07_insert--s1` | 794秒（13.2分） |
| `libraries-07_FormTag--s1` | 746秒（12.4分） |

**成功した最長実行は1503秒（25分）**。この3件はいずれもそれを超えており、
Claude CLI が内部エラーで終了したと判断できる。

`subprocess.run()` にはタイムアウト設定がないため、Python 側は無制限に待機する。
CLIが内部で無応答になった場合、プロセスが終了するまでスレッドはブロックされ続ける。

---

## 3件が同時刻（03:29）にエラーになった理由

3件はいずれも 02:55〜02:58 の3分間に並列起動された。
エラー発生時刻が全て 03:29:xx に集中しているのは、それぞれが独立してタイムアウトに達したためであり、
系全体の障害ではない（エラー直後も他ファイルの生成が継続している）。

```
03:29:13  🤖[GEN] libraries-enterprise_messaging_mom--s10    ← 新規起動（継続）
03:29:18  🤖[GEN] libraries-validation_basic_validators--s1  ← 新規起動（継続）
03:29:18  ERROR: libraries-file_upload_utility--s1           ← タイムアウト終了
03:29:19  ERROR: about-nablarch-02_I18N--s1                  ← タイムアウト終了
03:29:50  ERROR: libraries-mail--s6                          ← タイムアウト終了
03:30:46  🤖[GEN] libraries-enterprise_messaging_http--s1    ← 新規起動（継続）
```

---

## 件ごとの特徴分析

### 1. `libraries-file_upload_utility--s1`（392行、画像4枚）

- プロンプトサイズ: 38,589 bytes
- 画像参照: `FileUploadUtility_abstract.png`、`FileUploadUtility.png`、`FileUploadUtility_class.png`、`FileUploadUtility_sequence.png`（計4枚）
- コードブロック: 14個
- 画像は RST 内に `.. image::` ディレクティブとして記述されており、プロンプト本文に含まれる
- シーケンス図・クラス図が複数あり、内容の理解・整理に時間がかかった可能性がある

### 2. `libraries-mail--s6`（mail.rst 305-699行目、394行、画像2枚）

- プロンプトサイズ: 41,583 bytes
- 画像参照: `mail_overview.jpg`、`09_Mail.jpg`（計2枚）
- mail.rst 全体（699行）の後半セクション
- **同じファイルの前半** `libraries-mail--s1`（02:58:28 開始）は正常完了している
  → 後半セクションに何か処理を重くする内容があった可能性

### 3. `about-nablarch-02_I18N--s1`（168行、画像なし）

- プロンプトサイズ: 29,479 bytes（3件中最小）
- 画像なし、コードブロック2個のみ
- ファイル内容的な特徴は見当たらず、内容の難度による遅延ではない可能性が高い
- 最初に起動（02:55:29）しており、他の2件より長い33.8分経過してからエラー
- 並列実行中の API レート制限や系全体の負荷変動による不規則な遅延と考えられる

---

## 結論

| 観点 | 内容 |
|-----|------|
| 根本原因 | Claude CLI の内部タイムアウト（約30〜34分） |
| CCログがない理由 | returncode≠0 のとき `.json` を保存しない設計 |
| エラーメッセージが空の理由 | CLI の stderr が空で終了するため |
| ファイル内容の傾向 | 画像が多い・セクションが多い傾向はあるが、最小ファイルも失敗しており一貫した傾向は弱い |
| 再現性 | 並列実行中の負荷・API 状況依存のため、再実行すれば成功する可能性が高い |

---

## 再生成コマンド

```bash
cd tools/knowledge-creator
python run.py --version 1.4 --target libraries-file_upload_utility--s1,about-nablarch-02_I18N--s1,libraries-mail--s6
```

内容的な問題ではなく実行環境の問題のため、再実行で正常に生成されると想定される。

---

## 関連調査：分割バグ疑いファイル（Issue #230）

未生成3件の調査中に、`libraries-01_FailureLog--s1` の part=1 がソース3行しかない原因を追跡した結果、
分割ロジックのバグを発見した。

### バグの内容

`analyze_rst_sections()` は「直後の行が `------` であれば、その行をh2セクションタイトルとして検出」する。
RST の「オーバーライン付きタイトル」形式（`---` + タイトル + `---`）では、
オーバーラインの直前行（空行やラベル行）が phantom セクションとして誤検出される。

```
行0: .. _FailureLog:
行1: （空行）          ← i=1 で lines[2]="---" にマッチ → 空タイトルの phantom セクション
行2: -----------
行3: 障害ログの出力
行4: -----------       ← i=3 で lines[4]="---" にマッチ → 正しいセクション
```

2セクション検出 → `SPLIT_SECTION_THRESHOLD=2` を満たし分割発生 → part=1 が 0〜3行（実質空）になる。

### 生成済みバージョン全体での影響ファイル

`catalog.json` で `split_info.part=1` かつ行数20行以下のファイルを全バージョンで確認した結果：

| バージョン | ファイルID | part=1の行数 | 先頭パターン |
|-----------|----------|------------|------------|
| v1.4 | `libraries-01_FailureLog--s1` | **3行** | RST label + 空行 + オーバーライン |
| v1.4 | `about-nablarch-top-nablarch--s1` | 11行 | 画像ディレクティブ + `===` オーバーライン |
| v1.4 | `web-application-02_flow--s1` | 13行 | 空行 + `---` オーバーライン |
| v1.4 | `web-application-09_confirm_operation--s1` | 16行 | 空行 + `---` オーバーライン |
| v6 | `blank-project-FirstStepContainer--s1` | 13行 | RST label + 空行 + `---` オーバーライン |
| v5 | `blank-project-FirstStepContainer--s1` | 13行 | RST label + 空行 + `---` オーバーライン |

全件「オーバーライン付きタイトル形式」が共通パターン。Issue #230 として登録済み。

---

## 改善提案

### subprocess.run() にタイムアウトを設定する

現状は無制限待機のため、CLIが無応答になった場合に永久ブロックするリスクがある。

```python
result = subprocess.run(
    cmd, input=prompt, capture_output=True, text=True, env=env,
    timeout=2400  # 40分（成功最長25分の約1.6倍）
)
```

タイムアウト発生時は `subprocess.TimeoutExpired` が raise されるため、
適切にハンドリングしてエラーメッセージに「timeout after Xs」を記録できるようにする。

### エラー時にも CC プロセスの出力を保存する

現状は成功時のみ `.json` を保存。エラー時も `returncode`、`stderr` の内容を
`generate/{file_id}.json` に含めることで、次回の調査が容易になる。
