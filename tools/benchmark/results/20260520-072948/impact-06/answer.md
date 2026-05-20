**結論**: APサーバを3台にスケールアウトする場合、**HTTPセッションストアは使用を避ける**。DBストアまたはRedisストアを選ぶのが基本方針で、確認画面フローかつ複数タブ不要ならHIDDENストアも選択肢に入る。

**根拠**:

各ストアのスケールアウト適性は以下の通り。

| ストア | 保存先 | スケールアウト適性 | 備考 |
|--------|--------|-------------------|------|
| **DBストア** | DBテーブル | ◎ 全APで共有できる | ヒープを圧迫しない。有効期限切れセッションを定期削除するバッチが必要 |
| **Redisストア** | Redis | ◎ 全APで共有できる | DBストアと同等の特徴。テーブル・削除バッチ不要でDBストアより運用が軽い |
| **HIDDENストア** | クライアントサイド（hiddenタグ） | ◎ APサーバを経由しない | 複数タブ操作を許容できる。**APサーバ冗長化時は暗号化キーを全APで同一に揃える必要あり**（設定漏れで復号失敗） |
| **HTTPセッションストア** | APサーバのヒープ | ✗ そのままでは不可 | APサーバごとに状態を持つため、スティッキーセッション・セッションレプリケーション・NoSQL移行などの追加対処が必要。廃棄容易性の点でも劣る |

**Redisストア（推奨）の設定ポイント**:

本番のRedis構成に合わせて `nablarch.lettuce.clientType` を設定する。

```properties
# Sentinel (Master-Replica) 構成の場合
nablarch.lettuce.clientType=masterReplica

# Cluster 構成の場合
nablarch.lettuce.clientType=cluster
```

使用するクライアントクラスは構成ごとに用意されている。
- `LettuceSimpleRedisClient` — 単一インスタンス
- `LettuceMasterReplicaRedisClient` — Sentinel を介した Master-Replica 構成
- `LettuceClusterRedisClient` — Cluster 構成

**HIDDENストアを冗長構成で使う場合の注意**:

デフォルトの暗号化キーはAPサーバ起動時に自動生成されるため、サーバごとに異なるキーが生成されて復号に失敗する。全APで共通キーを明示設定すること。

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

**注意点**:
- セッションストアの有効期間はデフォルトでHTTPセッションに保存されるため、ステートレス化を徹底するには有効期間の保存先をDBに変更する必要がある（`handlers-SessionStoreHandler` の設定）。
- HTTPセッションストアへの依存を完全になくすには、セッションストア以外にも二重サブミット防止・スレッドコンテキスト変数管理ハンドラ等の設定変更が必要。

参照: libraries-session-store.json:s16, libraries-session-store.json:s12, libraries-stateless-web-app.json:s1, adapters-redisstore-lettuce-adaptor.json:s5, adapters-redisstore-lettuce-adaptor.json:s6