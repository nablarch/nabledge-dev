**結論**: APサーバをスケールアウトする場合、**DBストアまたはRedisストア**を選択してください。HTTPセッションストアはAPサーバ毎に状態を持つためそのままではスケールアウトできず、HIDDENストアはクライアントサイドに保存するためスケールアウト自体には問題ありませんが、セッション量が増えると通信量が増大します。

**根拠**:

### 各ストアの特徴

| ストア | 保存先 | スケールアウト適性 | 主な特徴 |
|--------|--------|-------------------|---------|
| **DBストア** | データベース上のテーブル | ✅ 問題なし | APサーバ停止後もセッション復元可能。ヒープ圧迫なし。同一セッション並行アクセス時は後勝ち |
| **HIDDENストア** | クライアントサイド（hiddenタグ） | ✅ 問題なし | 複数タブ操作を許容できる。ヒープ圧迫なし。ただしAPサーバが冗長化されている場合、**暗号化キーを明示的に統一する必要がある** |
| **HTTPセッションストア** | APサーバのヒープ領域 | ❌ **工夫が必要** | APサーバ毎に情報を保持するため、スケールアウト時はスティッキーセッション・レプリケーション等の対処が必要 |
| **Redisストア** | Redis（Lettuceアダプタ使用） | ✅ 問題なし | DBストアと特徴は同じ。テーブル事前作成不要・期限切れセッション削除バッチ不要というメリットあり |

### HTTPセッションストアをスケールアウトで使う場合の課題

```
通常のAPサーバスケールアウトに必要な対処：
1. ロードバランサーでスティッキーセッションを有効にする
2. APサーバのセッションレプリケーション機能を使用する
3. APサーバのHTTPセッション保存先をNoSQLにする
```

1・2は廃棄容易性の点で劣り、2・3はAPサーバ依存となるため、Nablarchではこれらを推奨しません。

### HIDDENストアをスケールアウト環境で使う場合の注意

APサーバが冗長化されている場合、サーバごとに異なる暗号化キーが自動生成されるため、復号に失敗するケースがあります。明示的にキーを統一する必要があります：

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

### スケールアウト時の推奨構成

APサーバをステートレスにするには、さらにセッションの**有効期間の保存先**もHTTPセッションから変更する必要があります（デフォルトはHTTPセッションに保存）：

- **DBストア使用時**: `SessionStoreHandler`の`expiration`プロパティを`DbManagedExpiration`に変更
- **Redisストア使用時**: Redisのキー有効期限機能を利用するため、追加設定不要

**注意点**:
- DBストアでは、ブラウザを閉じた際などにテーブル上にセッション情報が残ることがある。期限切れセッションを定期削除するバッチが必要
- Redisストアはこの問題がなく（有効期限切れで自動削除）、運用が簡略化できる
- 同一セッションへの並行アクセス（複数タブ同時リクエスト等）はDBストア・HTTPセッションストアでは後勝ちになる点に注意

参照: libraries-session-store.json:s16, libraries-session-store.json:s2, libraries-session-store.json:s12, libraries-session-store.json:s17, libraries-stateless-web-app.json:s1, libraries-stateless-web-app.json:s2, handlers-SessionStoreHandler.json:s9, adapters-redisstore-lettuce-adaptor.json:s15, adapters-redisstore-lettuce-adaptor.json:s6