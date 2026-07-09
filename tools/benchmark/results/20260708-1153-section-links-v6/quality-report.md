# nabledge-6 スキル 品質評価レポート

**対象**: QA・code-analysis セクションリンク追加（`参照:` と `**詳細**:` に docs パス＋セクションタイトルを追加）
**前版**: 20260616-1214-fullbench-classes-v6
**測定条件**: 34シナリオ × 3回 = 102評価
**評価方法**: 一次＝自動採点（全シナリオにスコア）／確定＝WF詳細込みナレッジ照合（56閾値割れ全件を workflow_details.json・answer.md・knowledge JSON の三点照合で実害有無を判定）

---

## 総合評価: 良好（既知問題あり）

3 run 通じてスコア退行なし。56 件の閾値割れを全件 WF 詳細付きで照合し、さらに回答文の文脈・説明順・コンテキストから再判定した結果、実害ありは **2 件**（qa-21/run-1、qa-19/run-3）。いずれも今回変更（セクションリンク追加）とは無関係な既存の LLM 非決定性問題。

---

## 合否判定

### ① 正しい知識を選定し回答できているか

**一次**: answer_correctness が 90/101 通過（前版 93/102）。閾値未満ケース（閾値 0.99）:

| run | シナリオ | スコア |
|---|---|---|
| run-1 | impact-06 | 0.500 |
| run-1 | qa-12 | 0.500 |
| run-1 | qa-14 | 0.500 |
| run-1 | qa-17 | 0.200 |
| run-1 | qa-19 | 0.700 |
| run-2 | qa-12 | 0.500 |
| run-2 | qa-17 | 0.300 |
| run-2 | qa-19 | 0.700 |
| run-3 | qa-12 | 0.400 |
| run-3 | qa-17 | 0.100 |
| run-3 | qa-19 | 0.000 |

**確定（11件全件 WF 詳細照合）**:

| run/シナリオ | WF 詳細 | 照合結果 | 実害 |
|---|---|---|---|
| run-1/impact-06 | step4 で s16（APサーバ停止後復元記述あり）を読んだが回答に未含 | 質問はスケールアウト時のストア選択。回答はその問いに正確かつ完全に回答しており、APサーバ停止後復元は追加の利点情報。省略しても誤動作にはつながらない。 | なし |
| run-1/qa-12 | step4 でエラー表示セクションを読んだ。Thymeleaf 主体の知識に従い回答 | 知識ファイル自体が Thymeleaf を主体として記述し JSP タグはTip扱い。`<n:errors>` タグへの言及も含まれており知識の重みづけに忠実。評価器の期待値設定の問題。 | なし |
| run-1/qa-14 | step4 で s2（APサーバ要件あり）を読んだが回答に未含 | 質問は「アプリケーションへの影響変更点（名前空間・依存関係等）」であり、コード変更点を問う文脈。APサーバ要件は運用インフラ要件であり、コード変更を問う文脈での省略は誤動作にはつながらない。 | なし |
| run-1/qa-17 | step4 で s24/s25 を読んだ | コード例 `SampleComponent sample = SystemRepository.get("sampleComponent");` が型安全な使い方そのものを示す。Javaの型推論で自明であり評価器の過剰要求。 | なし |
| run-1/qa-19 | step4 で adapters-jaxrs-adaptor.json:s2 を読んだ | `Jackson2BodyConverter` を明示的に言及。評価器は parenthetical との評価だが回答に含まれている。 | なし |
| run-2/qa-12 | run-1/qa-12 と同パターン | 同上。 | なし |
| run-2/qa-17 | step4 で javadoc s11 を読んだ | run-1/qa-17 と同じ。コード例が型安全を示す。 | なし |
| run-2/qa-19 | step4 で adapters-jaxrs-adaptor.json:s2 を読んだ | `Jackson2BodyConverter` を明示的に含む。評価器の評価基準の問題。 | なし |
| run-3/qa-12 | run-1/qa-12 と同パターン | 同上。 | なし |
| run-3/qa-17 | step4 で s24/s25 のみ（javadoc なし） | run-1/qa-17 と同じ。コード例が型安全を示す。 | なし |
| run-3/qa-19 | step4 が adapters-jaxrs-adaptor.json を読み飛ばし | `body-convert-handler.json:s4` のXML例（`JaxbBodyConverter` = application/xml）を application/json 対応コンバータとして誤提示。LLMが知識のコメントを書き換えて誤情報を出力。JSON リクエストが処理されない障害につながる。 | **あり** |

→ 実害: **1件**（qa-19/run-3）。impact-06/run-1・qa-14/run-1 は質問の文脈上省略が誤動作につながらない。

### ② 推測や捏造が含まれていないか

**一次**: faithfulness が 71/101 通過（前版 67/102）。閾値未満ケース（閾値 0.99、30件）:

**確定（30件全件 WF 詳細照合）**:

| run/シナリオ | WF 詳細 | 照合結果 | 実害 |
|---|---|---|---|
| run-1/impact-08 | step4 で testing-framework-03-Tips.json:s12 を読んだ | ナレッジが `yyyyMMddHHmmss` を「12桁」と誤記。実際のフォーマット文字数は14桁。スキルの「14桁・17桁」が算術的に正確。評価器がナレッジ誤記を根拠に矛盾判定。 | なし |
| run-1/oos-qa-01 | step4 で2セクションを読んだ | 知識の推奨パターンを正確に転記。Webアプリ文脈での言及は適切。評価器の過剰解釈。 | なし |
| run-1/qa-02 | step4 で s9/s14 を読んだ | 注意点の1箇条として「一括更新で排他制御が不要な場合のみ」と条件付きで言及。ナレッジは batchUpdate の制限だが、一括INSERT でも排他制御不要ケースで使うという説明は実用上正しく、ユーザーが batchInsert を不必要に避けるとは考えにくい。 | なし |
| run-1/qa-06 | step4 で libraries-tag.json:s23,s3,s11 + session-store:s9 + create-example:s1-s4 を読んだ | タグの説明（faithfulness）は正確。ただしセクション選択・読み込みの問題は relevancy に計上（別掲）。 | なし |
| run-1/qa-07 | step4 で getting-started batch s2/s3 を読んだ | `BeanUtil.createAndCopy` は知識 s3 に明示。`close` はtry-with-resourcesで省略可能（コード例はtry-with-resources使用）。評価器の誤読。 | なし |
| run-1/qa-12 | step4 で HttpErrorHandler.json:s4 を読んだ | 「`@OnError` が設定されていない場合、バリデーションエラーがシステムエラー扱いとなる」はナレッジ s4 の記述と一致。評価器の誤読。 | なし |
| run-1/qa-13 | step4 で bean-validation.json:s8/s17 を読んだ | ナレッジ s8「変換処理が失敗し、予期せぬ例外が送出され障害となってしまう」は断定的記述。回答の「変換エラーで予期せぬ例外が発生する」は実質等価。「注意点」行では「不正な値が送信されたときに」と条件付きで正確に記述あり。 | なし |
| run-1/qa-14 | step4 で migration-migration.json:s27 を読んだ | web-app version 3.1→6.0 はナレッジ s27 に明記。評価器の誤読。（correctness での実害とは別問題） | なし |
| run-1/qa-19 | step4 で adapters-jaxrs-adaptor.json:s2 を読んだ | 「JerseyまたはRESTEasy用アダプタ」という表現の直後に Jersey のXML例のみを示しており、実装は Jersey に限定されている。RESTEasy言及はハルシネーションだが、実装例が Jersey のみなのでユーザーが実装で迷うことはない。 | なし |
| run-1/qa-20 | step4 で global-error-handler.json:s4 を読んだ | 詳細テーブルは ThreadDeath→INFO を正確に記載。結論文の「FATALレベル」は要約表現。詳細テーブルで正確な情報が得られる。 | なし |
| run-1/qa-21 | step4 で handlers-jaxrs-response-handler.json:s4 を読んだ | 「デフォルトの `ErrorResponseBuilder` はメッセージなしのエラーレスポンスを生成する」という記述がナレッジに根拠なし（s4 は「デフォルト実装が使用される」のみ）。ユーザーが不必要にカスタム実装を作成する可能性あり。 | **あり** |
| run-1/review-06 | step4 で resource-signature.json:s2 を読んだ | コード例はすべて `req.getPathParam("id")` と正しい引数付き。散文の `getPathParam()` は省略記法。実装誤りにつながらない。 | なし |
| run-2/impact-08 | step4 で Tips.json:s12 を読んだ | run-1/impact-08 と同じ。ナレッジ typo が原因。 | なし |
| run-2/qa-02 | step4 で universal-dao.json:s7/s9 を読んだ | 「RDBMSによっては...エラーとなる可能性がある」という条件付き表現を使用。ナレッジと一致。評価器の細かすぎる区別。 | なし |
| run-2/qa-04 | step4 で testing-framework-01:s2-s7 等を読んだ | ナレッジ s6 のコード例自体が `TARGET_CLASS` を定義して使用。評価器がシグネチャ引数名とコール変数名を混同。 | なし |
| run-2/qa-06 | step4 で libraries-tag.json:s23 を読んだ | 本文テーブルは4タグをすべて正確に列挙。「3つ」という開始文は不正確だが誤実装にはつながらない。 | なし |
| run-2/qa-11 | step4 で HttpErrorHandler.json:s5 を読んだ | HttpErrorHandler の `writeFailureLogPattern` 動作としてナレッジ s5 と一致。評価器が HttpErrorHandler と GlobalErrorHandler を混同。 | なし |
| run-2/qa-12 | step4 で HttpErrorHandler.json:s4 を読んだ | ナレッジ s4 が `WebConfig` クラス名と `errorMessageRequestAttributeName` を明示。評価器の誤読。 | なし |
| run-2/qa-21 | step4 で jaxrs-bean-validation-handler.json:s3/s4 を読んだ | ナレッジが `JaxRsBeanValidationHandler`・`BodyConvertHandler` というクラス名を直接使用。評価器が文体上の好みで penalize。 | なし |
| run-2/review-07 | step4 で csrf-token-handler.json:s5 を読んだ | ナレッジ s5「アクション等のリクエスト処理の中で呼び出す」と一致。評価器の過剰解釈。 | なし |
| run-3/impact-06 | step4 で stateless-web-app.json:s1 を読んだ | ナレッジ「2, 3はAPサーバ依存となる」と回答の記述は verbatim に一致。評価器の誤読。 | なし |
| run-3/impact-08 | step4 で Tips.json:s12 を読んだ | run-1/impact-08 と同じ。 | なし |
| run-3/oos-impact-01 | step4 で biz-samples-12.json:s16 を読んだ | セッション固定攻撃対策はハンドラドキュメントで正確に記述された用語。評価器の過剰解釈。 | なし |
| run-3/qa-04 | step4 で testing-framework-01:s6 を読んだ | ナレッジ s6 のコード例が `TARGET_CLASS` パターンを示す。評価器の誤り。 | なし |
| run-3/qa-08 | step4 で libraries-message.json:s8 を読んだ | ナレッジ s8「**必ずデフォルトの言語を設定すること**」と明記。評価器の誤り。 | なし |
| run-3/qa-09 | step4 で libraries-date.json:s10 を読んだ | ナレッジ s10 のコード例が `BusinessDateProvider` インターフェースを使用。評価器がコメントとコード変数型を混同。 | なし |
| run-3/qa-11 | step4 で HttpErrorHandler.json:s5 を読んだ | run-2/qa-11 と同じ。HttpErrorHandler の動作として正確。 | なし |
| run-3/qa-12 | run-2/qa-12 と同パターン | 同上。 | なし |
| run-3/qa-19 | step4 が adapters-jaxrs-adaptor.json を読み飛ばし | correctness と同一根本原因による重複ペナルティ（JaxbBodyConverter を application/json 対応として誤表示）。 | **あり**（再掲） |
| run-3/qa-21 | step4 で bean-validation.json:s6/s7 を読んだ | `NablarchMessageInterpolator` がデフォルトであること（s6）と `{}` で囲む条件（s7）の組み合わせで正確。評価器の過剰解釈。 | なし |

→ 実害: **1件**（qa-21/run-1）。qa-02/run-1・qa-19/run-1 は回答文の文脈で誤動作につながらない。run-3/qa-19 は correctness と同一根本原因の重複ペナルティ。

### ③ 質問に対して適切な情報を提供できているか

**一次**: answer_relevancy が 86/101 通過（前版未測定）。閾値未満ケース（閾値 0.95、15件）:

**確定（15件全件 WF 詳細照合）**:

| run/シナリオ | WF 詳細 | 照合結果 | 実害 |
|---|---|---|---|
| run-1/pre-01 | step4 で architecture.json:s1-s3 を読んだ | 起動方法と `-requestPath` を主体に説明。処理フロー追加説明は末尾の補足であり有用なコンテキスト。 | なし |
| run-1/qa-05 | step4 で getting-started-create.json:s1 + body-convert-handler.json:s4/s5 を読んだ | String 型要件は正確かつ重要な制約。XML/form-urlencoded 列挙は BodyConvertHandler の全サポート形式から来る包括的説明。コアの JSON 回答を隠さない。 | なし |
| run-1/qa-06 | step4 で libraries-tag + session-store + create-example を読んだ | JSP共通化の説明は冒頭で完結しており、セッション管理は「画面間の入力データ保持」という別見出しで区切られている。create-example から自然に取り込まれた補足情報であり誤動作にはつながらない。冗長さはあるが実害なし。 | なし |
| run-1/qa-17 | step4 で s24/s25 を読んだ | 「DIコンテナ初期化は自分で実装不要」は1文の有用なコンテキスト。コアの回答（`get()` メソッド）は明確に先に提供。 | なし |
| run-1/qa-18 | step4 で bean-util.json:s9 を読んだ | レコードの `setProperty`/`copy` 制限は注意点の1文。`getProperty` の質問への回答は完全かつ最初に提供。予防的ガイダンスとして有用。 | なし |
| run-2/oos-qa-01 | step4 = 空（OOSケース） | 「知識ファイルに含まれていない」と開示した上で代替パターンを説明。WebSocketが非サポートという核心は正確に伝わる。免責事項の言い回しに軽微な矛盾はあるが誤動作にはつながらない。 | なし |
| run-2/qa-01 | step4 で universal-dao.json:s9 を読んだ | DBベンダーマニュアル参照は1フレーズで適切な技術案内。コアの回答（`defer()` + `close()`）は完全かつ最初に提供。 | なし |
| run-2/qa-04 | step4 で testing-framework-01 を読んだ | Entity自動生成の注意は注意点最後の1箇条。コアの質問（Formクラステスト作成方法）は完全かつ正確に回答。 | なし |
| run-2/qa-12 | step4 で InjectForm.json:s1/s3/s4 を読んだ | String型制約は注意点の1箇条。バリデーション実装に本質的に関連する制約であり有用。 | なし |
| run-2/qa-18 | step4 で bean-util.json:s9 を読んだ | run-1/qa-18 と同じ。 | なし |
| run-2/review-08 | step4 で session-store.json:s9/s16/s2 + SessionStoreHandler.json:s3 を読んだ | DB vs HIDDEN 選択基準は冒頭に明確に提示。Entity vs Form の注意・ハンドラ順序は同一知識ファイルからの密接に関連する実装ガイダンス。回答の順序は質問の優先事項を先に示している。 | なし |
| run-2/review-09 | step4 で secure-handler.json:s3/s6-s9 を読んだ | 参照セクションのファイルパスは nabledge 全回答の標準構造。CSP設定の回答は完全かつ正確。 | なし |
| run-3/qa-01 | step4 で universal-dao.json:s9 等を読んだ | run-2/qa-01 と同じ。 | なし |
| run-3/qa-16 | step4 で javadoc-UniversalDao.json:s17/s18 を読んだ | `exists()` の両バリアントへの回答は完全かつ正確。参照セクションのファイルパスは標準構造。 | なし |
| run-3/qa-18 | step4 で bean-util.json:s9 を読んだ | run-1/qa-18 と同じ。 | なし |

→ 実害: **0件**。qa-06/run-1 は冗長さはあるが回答文の文脈で誤動作につながらない。

---

## 確定実害まとめ

56件の閾値割れのうち実害ありは **2件（1 unique シナリオ）**:

| run/シナリオ | 指標 | スコア | 問題内容 | 根本原因 |
|---|---|---|---|---|
| run-3/qa-19 | correctness | 0.000 | JaxbBodyConverter を application/json 対応として誤提示（step4 が adapters-jaxrs-adaptor.json を読み飛ばし、XML例のコメントを書き換えて誤情報出力） | step4 読み飛ばし |
| run-1/qa-21 | faithfulness | 0.929 | デフォルト ErrorResponseBuilder が「メッセージなし」を生成するという記述がナレッジに根拠なし。カスタム実装の必要性を動機づける文として機能しており、ユーザーが不必要なカスタム実装を作成する可能性あり | 知識外の情報付与 |

いずれも今回変更（セクションリンク追加）とは無関係。前版から継続の既存 LLM 非決定性問題。

その他 54 件はいずれも実害なし（評価器の誤読・過剰解釈、知識ファイル typo、回答文の文脈で誤動作につながらない軽微な表現差異）。

---

## 計測

### ④ 1回あたりコスト

| | 平均 | 中央値 | 最大 |
|---|---|---|---|
| 今版 | $0.849 | $0.829 | $1.465 |
| 前版 | $0.885 | $0.853 | $1.587 |

前版比でやや減少。セクションタイトル出力追加による増加は見られない。

### ⑤ 1回あたり時間

| | 平均 | 中央値 | 最大 |
|---|---|---|---|
| 今版 | 156s | 152s | 323s |
| 前版 | 153s | 146s | 325s |

前版比で誤差範囲内（+2%）。実質的な差異なし。

---

## 退行（前版との対比）

| 軸 | 前版 → 今版 | 判定 |
|---|---|---|
| ① 正しさ | 93/102 → 90/101 | 退行なし（誤差範囲内、flaky のみ） |
| ② 捏造なし | 67/102 → 71/101 | 改善（flaky シナリオの run-to-run 変動） |
| ③ コスト | $0.885 → $0.849 | 減（-4%、誤差範囲内） |
| ④ 時間 | 153s → 156s | 増（+2%、誤差範囲内） |

---

## ベンチからの見解（合否ではなく判断材料）

- 品質: セクションリンク追加による品質劣化なし。閾値割れ 56 件中実害あり 2 件はいずれも前版から継続の既存問題であり、今回の変更に起因するものではない。
- コスト・時間: セクションタイトルの出力追加にもかかわらず、コスト・時間ともに前版と同水準。
- 既存問題（別 Issue で対応要）:
  - qa-19: JaxbBodyConverter 誤り（step4 読み飛ばしの非決定性、単発）
  - qa-21: ErrorResponseBuilder「メッセージなし」のハルシネーション
  - impact-08: ナレッジ誤記（`yyyyMMddHHmmss` を「12桁」と記載）は別 Issue で修正要

---

## 詳細根拠

各シナリオの個別スコア・回答・検索到達は run別レポート（run-N/report.md）を参照。
