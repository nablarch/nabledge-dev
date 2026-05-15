**結論**: APサーバ3台のスケールアウト構成では、**DBストア**または**Redisストア**を選択するのが基本方針です。HTTPセッションストアはそのままでは使えず、HIDDENストアは暗号化キーの共有が必要です。

**根拠**:

各ストアの特徴と、スケールアウト時の対応状況は以下の通りです。

| ストア | 保存先 | スケールアウト | 備考 |
|--------|--------|---------------|------|
| **DBストア** | データベース | ✅ そのまま使える | APサーバ停止後もセッション復元可能、ヒープ非圧迫 |
| **HIDDENストア** | クライアント（hiddenタグ） | ✅ ただし要設定 | サーバごとに異なる暗号化キーが生成されるため、明示的なキー共有が必要 |
| **HTTPセッションストア** | APサーバのヒープ | ❌ 工夫が必要 | スティッキーセッション・セッションレプリケーション・NoSQL化のいずれかが必要 |
| **Redisストア** (Lettuceアダプタ) | Redis | ✅ そのまま使える | DBストアと同じ特徴、本番ではSentinel/Cluster構成を使用 |

**HTTPセッションストアをスケールアウトするには**（知識ファイルより）：
1. ロードバランサーでスティッキーセッションを有効にする
2. APサーバのセッションレプリケーション機能を使用する
3. APサーバのHTTPセッション保存先をNoSQLにする

ただし 1・2 は「廃棄容易性（Twelve-Factor App）」の観点で劣り、2・3 はAPサーバ依存になります。NablarchではHTTPセッション依存機能をDBストアや他のストアに切り替えることで、APサーバをステートレスにできます。

**HIDDENストア使用時の冗長化対応**（設定例）:
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
全APサーバで同一の key/iv を設定する必要があります。

**用途別の選択基準**:

| 用途 | 推奨ストア |
|------|-----------|
| 入力〜確認〜完了画面の情報保持（複数タブ不可） | **DBストア** |
| 入力〜確認〜完了画面の情報保持（複数タブ許容） | **HIDDENストア**（暗号化キー共有要） |
| 認証情報の保持 | **DBストア** または HTTPセッションストア（スケールアウト対応要） |
| 大量データ（検索結果一覧など） | **使用しない** |

**Redisストアの本番構成クラス**:
- `LettuceSimpleRedisClient` — 単一インスタンス
- `LettuceMasterReplicaRedisClient` — Master-Replica構成（Sentinel経由含む）
- `LettuceClusterRedisClient` — Cluster構成

**注意点**:
- DBストアは同一セッションの処理が複数スレッドで実行された場合、**後勝ち**になります（先に保存されたデータは消失）
- HIDDENストアは暗号化キーを全APサーバで同一にしないと復号に失敗します
- セッションストアにはFormではなくEntityを格納することが推奨されています（セキュリティ・凝集性の観点）
- セッションの有効期間もデフォルトではHTTPセッションに保存されるため、スケールアウト時は`DbManagedExpiration`への切り替えを検討してください

参照: `component/libraries/libraries-session-store.json#s16`, `component/libraries/libraries-session-store.json#s2`, `component/libraries/libraries-stateless-web-app.json#s1`, `component/adapters/adapters-redisstore-lettuce-adaptor.json#s5`, `component/adapters/adapters-redisstore-lettuce-adaptor.json#s6`, `component/libraries/libraries-session-store.json#s12`, `component/handlers/handlers-SessionStoreHandler.json#s9`