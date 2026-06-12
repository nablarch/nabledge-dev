**結論**: APサーバをスケールアウトする場合、**DBストア**または**Redisストア**を選択してください。HTTPセッションストアはAPサーバ毎に状態を持つため、そのままではスケールアウトできません。

**根拠**:

### 各ストアの特徴とスケールアウト適性

| ストア | 保存先 | スケールアウト適性 | 備考 |
|--------|--------|-------------------|------|
| **DBストア** | データベース上のテーブル | ✅ 問題なし | ヒープ圧迫なし、APサーバ停止時もセッション復元可能 |
| **Redisストア** | Redis | ✅ 問題なし | DBストアと同じ特性。テーブル事前作成不要、有効期限バッチ不要 |
| **HIDDENストア** | クライアントサイド（hiddenタグ） | ✅ 問題なし（要設定） | APサーバに状態を持たないが、**冗長化時は暗号化キーの明示設定が必要** |
| **HTTPセッションストア** | APサーバのヒープ領域 | ❌ 工夫が必要 | APサーバ毎に情報を保持するため、スケールアウト時に対処が必要 |

### HTTPセッションストアでスケールアウトする場合の対処法（非推奨）

知識ファイルでは以下の3つの対処法が示されていますが、いずれも欠点があります：

1. **スティッキーセッション**（ロードバランサーで設定） → 廃棄容易性の観点で劣る
2. **APサーバのセッションレプリケーション** → 廃棄容易性の観点で劣り、APサーバ依存
3. **HTTPセッション保存先をNoSQLに変更** → APサーバ依存

Nablarchでは、HTTPセッション非依存機能（DBストア等）に切り替えることでAPサーバをステートレスにする方法を推奨しています。

### HIDDENストア使用時の注意点

APサーバが冗長化されている場合、暗号化キーがAPサーバごとに自動生成されるため、**復号に失敗するケースが発生します**。以下のように明示的にキーを設定してください：

```xml
<component class="nablarch.common.web.session.store.HiddenStore">
  <property name="encryptor">
    <component class="nablarch.common.encryption.AesEncryptor">
      <property name="base64Key">
        <component class="nablarch.common.encryption.Base64Key">
          <property name="key" value="OwYMOWbnLyYy93P8oIayeg==" />
          <property name="iv"  value="NOj5OUN+GlyGYTc6FM0+nw==" />
        </component>
      </property>
    </component>
  </property>
</component>
```

### Redisストアのメリット（DBストアとの比較）

- セッション情報保存用テーブルの事前作成が不要
- 有効期限切れセッション削除バッチの作成が不要

本番環境ではSentinel（Master-Replica）またはCluster構成のRedisに対応しています。

**注意点**:
- `有効期間`はデフォルトでHTTPセッションに保存されます。完全なステートレス化にはセッション有効期間の保存先もDBに変更する必要があります（`handlers-SessionStoreHandler` の設定）
- DBストアはAPサーバ停止時の復元に強い反面、同一セッションを複数スレッドで処理した場合は**後勝ち**（先のデータが消失）になります
- 同一セッションの複数スレッド処理でデータを独立して保持したい場合はHIDDENストアが有効です

参照: component/libraries/libraries-session-store.json#s16, component/libraries/libraries-stateless-web-app.json#s1, component/libraries/libraries-session-store.json#s12, component/adapters/adapters-redisstore-lettuce-adaptor.json#s5