**結論**: スケールアウト環境では **DBストア** または **Redisストア（Lettuceアダプタ）** を選択する。HTTPセッションストアはAPサーバ毎に状態を持つためスケールアウトに工夫が必要で、HIDDENストアはクライアントサイドに保存するため原理的にはAPサーバ非依存だが後述の制約がある。

---

**根拠**:

#### 各ストアの特徴まとめ

| ストア | 保存先 | スケールアウト | 複数タブ対応 | ヒープへの影響 |
|-------|--------|--------------|------------|--------------|
| **HTTPセッションストア** | APサーバのヒープ領域 | ❌ APサーバ毎に状態を持つため工夫が必要 | ❌ 後勝ち | ❌ 大量データでヒープ圧迫の恐れ |
| **DBストア** | データベーステーブル | ✅ APサーバに依存しない | ❌ 後勝ち | ✅ 圧迫しない |
| **HIDDENストア** | クライアントサイド（hiddenタグ） | ✅ APサーバに依存しない | ✅ タブごとに独立して保存 | ✅ 圧迫しない |
| **Redisストア** | Redis（外部ストア） | ✅ APサーバに依存しない | ❌ 後勝ち（DBストアと同じ特徴） | ✅ 圧迫しない |

#### スケールアウト時の推奨選択

**1. DBストア（推奨）**

- データベースに保存するためAPサーバ非依存
- APサーバ停止後もセッション変数を復元可能
- ただし、**有効期間のデフォルト保存先もHTTPセッション**なので、スケールアウト時は `expiration` を `DbManagedExpiration` に変更する必要がある

```xml
<!-- SessionStoreHandlerのexpiration設定をDBに変更 -->
<component name="sessionStoreHandler" class="nablarch.common.web.session.SessionStoreHandler">
  <property name="expiration" ref="expiration" />
</component>

<component name="expiration" class="nablarch.common.web.session.DbManagedExpiration">
  <property name="dbManager">
    <component class="nablarch.core.db.transaction.SimpleDbTransactionManager">
      <property name="dbTransactionName" value="expirationTransaction"/>
    </component>
  </property>
</component>
```

**2. Redisストア（Lettuceアダプタ）**

- DBストアと同様の特徴を持ちつつ、以下のメリットがある：
  - テーブルの事前作成が不要
  - 期限切れセッションを削除するバッチが不要（Redisの有効期限機能を活用）
- 構成に応じてクライアントクラスを選択：`LettuceSimpleRedisClient`（単一）/ `LettuceMasterReplicaRedisClient`（Master-Replica + Sentinel）/ `LettuceClusterRedisClient`（Cluster）

**3. HIDDENストアを使う場合の注意**

APサーバが冗長化されている場合、暗号化キーは各サーバで自動生成されるため、**復号に失敗する**。明示的に共通の暗号化キーを設定しなければならない：

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

#### スケールアウト設計の背景

HTTPセッションに依存したままスケールアウトするには「スティッキーセッション」「セッションレプリケーション」「NoSQLへの移行」といった対処が必要だが、これらはTwelve-Factor Appの廃棄容易性の観点で劣るかAPサーバ依存になる。DBストアまたはRedisストアを使うことで、APサーバをステートレスにできる。

**注意点**:
- HTTPセッションストアの有効期間も含め、**有効期間の保存先**を必ずDB（`DbManagedExpiration`）またはRedisに変更すること。デフォルトのまま（`HttpSessionManagedExpiration`）ではHTTPセッションに依存するため、スケールアウト時にセッションが失われる
- 認証情報にHTTPセッションストアを使う場合、スケールアウト時は上記の工夫が必要

参照: libraries-session-store.json:s16, libraries-session-store.json:s2, libraries-session-store.json:s17, libraries-session-store.json:s12, libraries-stateless-web-app.json:s1, adapters-redisstore-lettuce-adaptor.json:s6, adapters-redisstore-lettuce-adaptor.json:s15, handlers-SessionStoreHandler.json:s9

---