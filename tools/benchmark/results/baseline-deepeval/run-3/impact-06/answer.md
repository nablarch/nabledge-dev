Step 5〜7：回答生成・検証を行い、Step 8で出力します。

---

**結論**: スケールアウト構成では **DBストア** または **Redisストア** が適切。HTTPセッションストアはAPサーバごとに状態を保持するためスケールアウトに工夫が必要。HIDDENストアはクライアントサイドに保存するためAPサーバの台数には依存しないが、冗長構成では暗号化キーを全APサーバで明示的に共有する設定が別途必要。

---

**根拠**:

各ストアのスケールアウト時の特徴まとめ：

| ストア | 保存先 | スケールアウト時の挙動 |
|---|---|---|
| **DBストア** | データベース上のテーブル | APサーバが停止しても復元可能。ヒープ圧迫なし。スケールアウトに適する |
| **HIDDENストア** | クライアントサイド（hiddenタグ） | AP台数依存なし。ただし冗長構成では暗号化キーの共有設定が必要（後述） |
| **HTTPセッションストア** | APサーバのヒープ領域 | APサーバ毎に情報を保持するため、スケールアウトを行う際に工夫が必要となる |
| **Redisストア** | Redis | 保存先が異なるだけで特徴はDBストアと同じ。有効期限はRedisが自動管理 |

**HTTPセッションストアを使わずスケールアウトするNablarchの推奨アプローチ**は、HTTPセッション非依存の機能に切り替えること（DBストアまたはHIDDENストアの使用）。一般的なスティッキーセッションやセッションレプリケーションはTwelve-Factor Appの廃棄容易性の観点で劣り、APサーバ依存にもなる。

**重要：有効期間の保存先も変更が必要**

DBストアやHIDDENストアに切り替えただけでは不十分で、セッション有効期間のデフォルト保存先もHTTPセッションのため、`DbManagedExpiration` への差し替えが必要：

```xml
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

**HIDDENストアを冗長構成で使う場合**は、APサーバごとに異なる暗号化キーが自動生成されるため復号に失敗するケースがある。全APサーバ共通のキーを明示設定する：

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

**Redisストアの有効期限管理**は、Redisの組み込み機能を使用しており、有効期限が切れたセッション情報は自動的に削除される。そのため、ゴミとして残ったセッション情報を削除するためのバッチを用意する必要はない。

---

**注意点**:
- 同一セッションが複数スレッドで処理された場合、DBストアとHTTPセッションストアは後勝ちになる（先に保存されたデータが消失する）
- DBストアのテーブルで有効期間をDB管理する場合、`SESSION_OBJECT` カラムはNull許容で定義すること（ログアウト時にNullレコードが登録されるため）

参照: `libraries-session-store.json:s16`, `libraries-session-store.json:s12`, `libraries-stateless-web-app.json:s1`, `handlers-SessionStoreHandler.json:s9`, `adapters-redisstore-lettuce-adaptor.json:s15`

---