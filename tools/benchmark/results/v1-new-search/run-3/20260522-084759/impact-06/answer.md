Step 5で回答を生成します。

**結論**: APサーバをスケールアウトする場合、**DBストア**または**Redisストア**を選ぶべきです。HTTPセッションストアはAPサーバごとに状態を持つためスケールアウトに工夫が必要で、HIDDENストアは画面間のデータ受け渡しに特化した用途です。

---

**根拠**:

### 各ストアの特徴

| ストア | 保存先 | スケールアウト時の特性 |
|--------|--------|----------------------|
| **DBストア** | データベース上のテーブル | APサーバが停止してもセッション変数の復元が可能。ヒープ領域を圧迫しない |
| **HIDDENストア** | クライアントサイド（hiddenタグで画面間を引き回し） | ヒープ領域を圧迫しない。複数タブでの画面操作を許容できる |
| **HTTPセッションストア** | APサーバのヒープ領域 | **APサーバ毎に情報を保持するため、スケールアウトを行う際に工夫が必要となる** |

### スケールアウト時のHTTPセッションの問題

HTTPセッションはAPサーバで状態を持つため、そのままではスケールアウトができません。通常の対処として以下が挙げられますが、いずれも課題があります。

1. ロードバランサーでスティッキーセッションを有効にする
2. APサーバのセッションレプリケーション機能を使用する
3. APサーバのHTTPセッション保存先をNoSQLにする

1, 2はTwelve-Factor Appの廃棄容易性の点で劣り、2, 3はAPサーバ依存となります。

### スケールアウト構成での推奨選択

**DBストア**または**Redisストア**（Lettuceアダプタ）を使用し、APサーバをステートレスにすることが推奨されます。

**DBストアの注意点**:
- セッション有効期間はデフォルトではHTTPセッションに保存されるため、スケールアウト時は有効期間の保存先もデータベースに変更する必要があります（`SessionStoreHandler` の設定で切り替え可能）
- ブラウザが閉じられた場合などにテーブル上にセッション情報が残ることがあるため、期限切れのセッション情報を定期的に削除するバッチが必要です

**Redisストアの利点**（DBストアと同じ特徴を持ちつつ、以下が追加）:
- セッション情報を保存するためのテーブルを事前に用意する必要がない
- 有効期限が切れたセッション情報はRedisが自動的に削除するため、削除バッチが不要

### HIDDENストア使用時の注意

HIDDENストアはクライアントサイドにデータを持つため、APサーバのステートには影響しません。ただし、**APサーバが冗長化されている場合、デフォルトの暗号化キーはAPサーバごとに異なるため復号に失敗します**。この場合、明示的に共通の暗号化キーを設定する必要があります。

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

---

**注意点**:
- DBストアとRedisストアでは「同一セッションの処理が複数スレッドで実行された場合、後勝ちになる」（先に保存されたセッションのデータは消失する）点に注意が必要です
- セッションの有効期間をHTTPセッション非依存にするには、DBストアの場合は `SessionStoreHandler` の設定変更が必要です

参照: libraries-session-store.json:s16, libraries-session-store.json:s2, libraries-session-store.json:s12, libraries-session-store.json:s17, libraries-stateless-web-app.json:s1, adapters-redisstore-lettuce-adaptor.json:s14, adapters-redisstore-lettuce-adaptor.json:s15

---