**結論**: APサーバを複数台にスケールアウトするときは、**DBストア・HIDDENストア・Redisストア**のいずれかを使用する。HTTPセッションストアはAPサーバごとに状態を持つため、スケールアウト時に追加の工夫（スティッキーセッション、セッションレプリケーション等）が必要になる。

**根拠**:

標準で提供しているストアの特徴と選択基準は以下の通り。

| ストア | 保存先 | スケールアウト | 主な特徴 |
|---|---|---|---|
| **DBストア** | DB上のテーブル | 対応可能 | APサーバ停止後もセッション復元可能。ヒープを圧迫しない。 |
| **HIDDENストア** | クライアントサイド（hiddenタグ） | 対応可能 | 複数タブ操作を許容。**冗長化時は暗号化キーの明示的な共有設定が必要**。 |
| **HTTPセッションストア** | APサーバのヒープ領域 | **工夫が必要** | APサーバ毎に情報を保持するためスケールアウト時に工夫が必要。 |
| **Redisストア**（Lettuce） | Redis | 対応可能 | 保存先が異なるだけで特徴はDBストアと同じ。テーブル作成・バッチ不要。 |

**HIDDENストアの冗長化時の注意点**:

デフォルトでは暗号化キーがAPサーバごとに自動生成されるため、冗長化環境では異なるサーバで復号失敗が発生する。以下のように `AesEncryptor` で明示的にキー/IVを設定する必要がある。

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

鍵とIVはbase64エンコードした値を設定する。

**セッションの有効期間について**:

有効期間はデフォルトでHTTPセッションに保存されている。DBストアやHIDDENストアだけでは有効期間がHTTPセッションに残るため、完全にステートレス化するには `DbManagedExpiration` の設定が別途必要。Redisストアを使用した場合はRedisネイティブのTTL仕組みで有効期限を管理するため、有効期限バッチを用意する必要がない。

**Redisストアの本番構成**:

`nablarch.lettuce.clientType` で以下の3構成に切り替えられる。

| 設定値 | クライアントクラス | 用途 |
|---|---|---|
| `simple` | `LettuceSimpleRedisClient` | 単一インスタンス |
| `masterReplica` | `LettuceMasterReplicaRedisClient` | Master-Replica/Sentinel構成 |
| `cluster` | `LettuceClusterRedisClient` | Cluster構成 |

```properties
# 例: Cluster構成に切り替える
nablarch.lettuce.clientType=cluster
```

**注意点**:
- スケールアウト対応に加え、有効期間もHTTPセッション非依存にしたい場合は `DbManagedExpiration` 設定（またはRedisストア使用）が必要。
- HIDDENストアは `AES` 暗号化キー/IVを全APサーバで共有する設定を忘れると、ロードバランサー越しのリクエストで復号エラーが発生する。

参照: libraries-session-store.json:s16, libraries-session-store.json:s12, libraries-session-store.json:s17, libraries-stateless-web-app.json:s1, adapters-redisstore-lettuce-adaptor.json:s5, adapters-redisstore-lettuce-adaptor.json:s6, adapters-redisstore-lettuce-adaptor.json:s7, adapters-redisstore-lettuce-adaptor.json:s15