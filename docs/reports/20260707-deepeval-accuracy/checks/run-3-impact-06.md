# impact-06 — run-3

## 質問

APサーバを複数台にスケールアウトするとき、セッション変数の保存先はどれを選ぶべき？各ストアの特徴を知りたい

## 回答

**結論**: スケールアウト環境では **DBストア** または **Redisストア** を選択してください。HTTPセッションストアはAPサーバ毎に状態を持つためスケールアウトには不向きです。HIDDENストアはサーバ側に状態を持たないため、スケールアウトの文脈では別の意味で有効です。

**根拠**:

#### 各ストアの特徴

| ストア | 保存先 | スケールアウト適性 | 特記事項 |
|---|---|---|---|
| **DBストア** | データベース上のテーブル | ✅ 適する | APサーバ停止時もセッション復元可能。有効期限切れレコードは定期削除バッチが必要 |
| **HIDDENストア** | クライアントサイド（hiddenタグで画面間引き回し） | ✅ 適する | APサーバが状態を持たない。複数タブ操作を許容できる。ただし冗長化時は暗号化キーを明示設定する必要あり |
| **HTTPセッションストア** | APサーバのヒープ領域 | ❌ 不向き | APサーバ毎に情報を保持するため「スケールアウトを行う際に工夫が必要」 |
| **Redisストア** | Redis（外部ストア） | ✅ 適する | DBストアと特徴は同じ。有効期限はRedisの仕組みで自動削除（バッチ不要） |

**重要な追加考慮点**:

HTTPセッションストアのまま複数台APサーバを構成する場合、以下の3択となりますが、いずれも欠点があります:

1. ロードバランサーで**スティッキーセッション**を有効にする → 廃棄容易性（Twelve-Factor App）の点で劣る
2. APサーバの**セッションレプリケーション**機能を使用する → APサーバ依存
3. APサーバのHTTPセッション保存先をNoSQLにする → APサーバ依存

#### HIDDENストアを使う場合の冗長化注意点

デフォルトでは暗号化キーがAPサーバ起動ごとに自動生成されるため、複数台構成では別サーバで復号失敗します。明示的にキーを統一する必要があります:

```xml
<component class="nablarch.common.web.session.store.HiddenStore">
  <property name="encryptor">
    <component class="nablarch.common.encryption.AesEncryptor">
      <property name="base64Key">
        <component class="nablarch.common.encryption.Base64Key">
          <property name="key" value="OwYMOWbnLyYy93P8oIayeg==" />
          <property name="iv" value="NOj5OUN+GlyGYTc6FM0+nw==" />
        </component>
      </property>
    </component>
  </property>
</component>
```

#### 完全なステートレス化のために

セッションストアだけでなく、以下の機能もデフォルトでHTTPセッションに依存しているため、併せて切り替えが必要です:

- **セッションストアの有効期間**: デフォルトはHTTPセッション保存 → `DbManagedExpiration` でDB保存に変更
- **2重サブミット防止**: DBベースの実装に変更
- **スレッドコンテキスト変数管理ハンドラ**: `LanguageAttributeInHttpSession` → `LanguageAttributeInHttpCookie` 等に変更

#### 選択基準まとめ

| 用途 | 推奨ストア |
|---|---|
| 入力〜確認〜完了画面間の入力情報保持（複数タブ不可） | DBストア |
| 入力〜確認〜完了画面間の入力情報保持（複数タブ可） | HIDDENストア |
| 認証情報の保持（スケールアウト環境） | DBストアまたはRedisストア |

**注意点**: HTTPセッションストアを認証情報の保持に使う場合、スケールアウト時は上記の工夫が必要です。スケールアウトを前提とするならDBストアまたはRedisストアを最初から選ぶのが推奨です。

参照: libraries-session-store.json:s16, libraries-session-store.json:s2, libraries-stateless-web-app.json:s1, libraries-stateless-web-app.json:s2, handlers-SessionStoreHandler.json:s9, libraries-session-store.json:s17, adapters-redisstore-lettuce-adaptor.json:s15, adapters-redisstore-lettuce-adaptor.json:s6

## 参照ナレッジ

- [セッションストアの特長と選択基準](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-session-store.md#セッションストアの特長と選択基準) (s16)
- [セッション変数の保存先を選択できる](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-session-store.md#セッション変数の保存先を選択できる) (s2)
- [基本的な考え方](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-stateless-web-app.md#基本的な考え方) (s1)
- [HTTPセッションに依存している機能](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-stateless-web-app.md#httpセッションに依存している機能) (s2)
- [有効期間をデータベースに保存する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-SessionStoreHandler.md#有効期間をデータベースに保存する) (s9)
- [有効期間の管理方法](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-session-store.md#有効期間の管理方法) (s17)
- [有効期限の管理方法](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/adapters/adapters-redisstore-lettuce-adaptor.md#有効期限の管理方法) (s15)
- [構成ごとに用意されたクライアントクラス](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/adapters/adapters-redisstore-lettuce-adaptor.md#構成ごとに用意されたクライアントクラス) (s6)
- [セッションストア](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-stateless-web-app.md#セッションストア) (s4)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output fully covers both facts stated in the Expected Output. It explicitly states that DBストア saves data to 'データベース上のテーブル' and that 'APサーバ停止時もセッション復元可能', which matches the first expected fact. It also clearly states that HIDDENストア uses 'クライアントサイド（hiddenタグで画面間引き回し）', which matches the second expected fact. No contradictions or inaccuracies are present relative to the expected facts. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is fully relevant to the question about session variable storage options when scaling out AP servers, with no irrelevant statements detected. The response appropriately addresses the characteristics of each session store in a multi-server scale-out context. |
| faithfulness | 0.99 | 0.96 | NG | The score is 0.96 because the actual output incorrectly attributes the need for a periodic batch process for expired records to the DB store, when the retrieval context actually highlights Redis store (Lettuce) adapter as the one using Redis's built-in expiration mechanism requiring no batch process. This single misattribution slightly misrepresents the storage mechanism details. |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「DBストアはデータベース上のテーブルに保存し、APサーバ停止時もセッション変数の復元が可能」は回答の表「データベース上のテーブル」「APサーバ停止時もセッション復元可能」に含まれている。参照事実「HIDDENストアはクライアントサイドにhiddenタグで引き回して実現する」は回答の表「クライアントサイド（hiddenタグで画面間引き回し）」に含まれている |
| answer_relevancy | OK | 回答はスケールアウト時のセッション変数保存先選択という質問に直接答えており、DBストア・HIDDENストア・HTTPセッションストア・Redisストアの特徴、スケールアウト適性、選択基準をすべてカバーしている。ステートレス化の追加考慮点（2重サブミット防止、スレッドコンテキスト変数管理ハンドラ等）もスケールアウト文脈に直結する内容であり、的外れな情報は含まれていない。 |
| faithfulness | OK | DeepEvalのNG判定（「定期削除バッチの必要性をDBストアに誤帰属」）は誤読。回答はDBストアに「有効期限切れレコードは定期削除バッチが必要」、Redisストアに「有効期限はRedisの仕組みで自動削除（バッチ不要）」と正しく区別して記載している。ナレッジ（libraries-session-store.md）にもDBストアの注意点として「期限切れのセッション情報は定期的に削除する必要がある」と記述されており、回答の内容と一致している。その他の記述（HIDDENストアの暗号化キー設定、HTTPセッションストアのスケールアウト対処法、ステートレス化の各機能切り替え）もナレッジと矛盾しない。 |

### 参照事実（expected_facts）

- DBストアはデータベース上のテーブルに保存し、APサーバ停止時もセッション変数の復元が可能
- HIDDENストアはクライアントサイドにhiddenタグで引き回して実現する
