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