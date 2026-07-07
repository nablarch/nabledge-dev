# impact-06 — run-1

## 質問

APサーバを複数台にスケールアウトするとき、セッション変数の保存先はどれを選ぶべき？各ストアの特徴を知りたい

## 回答

**結論**: APサーバをスケールアウトする場合、HTTPセッションストアは各APサーバのヒープにセッション情報を保持するため工夫が必要です。**DBストアまたはRedisストア**の使用を推奨します。DBストアとRedisストアはAPサーバ外に保存するため、複数台構成でもセッションが共有できます。

**根拠**:

Nablarchは標準で3種類、アダプタ経由でRedisストアを含め計4種類のセッション変数保存先を提供しています。

**各ストアの特徴**:

| ストア | 保存先 | スケールアウト適性 |
|---|---|---|
| DBストア | データベース | ◎ APサーバ外に保存するため複数台構成OK |
| HIDDENストア | クライアントサイド（hiddenタグ） | ◎ APサーバに依存しない。複数タブ操作も許容できる |
| HTTPセッションストア | APサーバのヒープ | △ APサーバ毎に情報を保持するため、スケールアウトに工夫が必要 |
| Redisストア | Redis（Lettuceアダプタ） | ◎ DBストアと同等の特徴。テーブル作成やGCバッチが不要 |

**DBストアの特徴**（セクション s16）:
- ローリングメンテナンス等でAPサーバが停止した場合でもセッション変数の復元が可能
- APサーバのヒープ領域を圧迫しない
- 同一セッションの処理が複数スレッドで実行された場合は後勝ち

**HIDDENストアの特徴**（セクション s16）:
- 複数タブでの画面操作を許容できる
- APサーバのヒープ領域を圧迫しない
- 冗長化環境では暗号化キーを明示的に設定する必要がある（APサーバごとにキーが自動生成されるため復号失敗のリスクあり）

```xml
<!-- 冗長化時のHIDDENストア暗号化キー設定例 -->
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

**HTTPセッションストアの特徴**（セクション s16）:
- APサーバ毎に情報を保持するため、スケールアウトを行う際に工夫が必要（スティッキーセッションやセッションレプリケーション等）
- 画面の入力内容のような大量データを保存するとヒープ領域を圧迫する恐れがある

**Redisストアの追加メリット**（adapters-redisstore-lettuce-adaptor.json intro）:
- セッション情報を保存するためのテーブルを事前に用意する必要がない
- 有効期限が切れたセッション情報を削除するためのバッチを作る必要がない（Redisの有効期限機能を使用）

**HTTPセッション依存からの脱却**（セクション s1）:

サーブレットAPIのHTTPセッションはAPサーバで状態を持つため、そのままではスケールアウトができません。通常の対処法として①スティッキーセッション、②セッションレプリケーション、③NoSQL保存がありますが、これらはTwelve-Factor Appの廃棄容易性の点で劣ったり、APサーバ依存となります。セッションストアの有効期間保存先もデフォルトではHTTPセッションに保存されるため、完全なスケールアウト対応にはデータベース保存への切り替えが必要です。

**注意点**:
- DBストアを使用した場合、期限切れのセッション情報が定期的にテーブルに残るため、削除バッチが必要です（Redisストアでは不要）
- HTTPセッションストアは認証情報等の保持に向いていますが、スケールアウト環境では追加設計が必要です
- セッションストアの有効期間はデフォルトでHTTPセッションに保存されます。完全なステートレス化には `DbManagedExpiration` へ切り替えが必要です

参照: libraries-session-store.json:s16, libraries-stateless-web-app.json:s1, libraries-session-store.json:s2, adapters-redisstore-lettuce-adaptor.json:s6, libraries-session-store.json:s12

## 参照ナレッジ

- [セッションストアの特長と選択基準](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-session-store.md#セッションストアの特長と選択基準) (s16)
- [基本的な考え方](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-stateless-web-app.md#基本的な考え方) (s1)
- [セッション変数の保存先を選択できる](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-session-store.md#セッション変数の保存先を選択できる) (s2)
- [構成ごとに用意されたクライアントクラス](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/adapters/adapters-redisstore-lettuce-adaptor.md#構成ごとに用意されたクライアントクラス) (s6)
- [HIDDENストアの暗号化設定をカスタマイズする](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-session-store.md#hiddenストアの暗号化設定をカスタマイズする) (s12)
- [有効期間の管理方法](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-session-store.md#有効期間の管理方法) (s17)
- [有効期間をデータベースに保存する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-SessionStoreHandler.md#有効期間をデータベースに保存する) (s9)
- [HTTPセッションに依存している機能](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-stateless-web-app.md#httpセッションに依存している機能) (s2)
- [Redis の構成に合わせて設定する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/adapters/adapters-redisstore-lettuce-adaptor.md#redis-の構成に合わせて設定する) (s5)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output covers both expected facts clearly. It explicitly states that the DBストア saves to a database table and that sessions can be restored even when an AP server stops ('ローリングメンテナンス等でAPサーバが停止した場合でもセッション変数の復元が可能'). It also explicitly describes the HIDDENストア as storing on the client side via hidden tags ('クライアントサイド（hiddenタグ）'). Both expected facts are present and accurately represented without contradiction. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is fully relevant, directly addressing the question about session variable storage options when scaling out AP servers horizontally. All content stays on topic with no irrelevant statements! |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「DBストアはデータベース上のテーブルに保存し、APサーバ停止時もセッション変数の復元が可能」は回答テーブルの「データベース」とDBストア特徴の「ローリングメンテナンス等でAPサーバが停止した場合でもセッション変数の復元が可能」に含まれている。参照事実「HIDDENストアはクライアントサイドにhiddenタグで引き回して実現する」は回答テーブルの「クライアントサイド（hiddenタグ）」に含まれている |
| answer_relevancy | — | —
| faithfulness | — | —

### 参照事実（expected_facts）

- DBストアはデータベース上のテーブルに保存し、APサーバ停止時もセッション変数の復元が可能
- HIDDENストアはクライアントサイドにhiddenタグで引き回して実現する
