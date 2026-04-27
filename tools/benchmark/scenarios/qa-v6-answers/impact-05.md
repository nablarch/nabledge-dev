**質問**: 画面遷移中のフォーム入力を HIDDEN フィールドに持たせたい。Nablarch の機能で楽に書けると聞いた。本番が AP サーバ複数台構成なんだけど、何かハマりどころある？

---

**結論**: Nablarch のセッションストアに `HiddenStore` を登録すれば、HIDDEN フィールドによるセッション保持が楽に書ける。複数 AP サーバ構成では HiddenStore のデフォルト暗号化キーが **サーバごとに自動生成されて異なる** ため、あるサーバで暗号化した HIDDEN 値を別サーバが復号できない問題が発生する。`HiddenStore` の `encryptor` プロパティに明示的な暗号化キー・IV を設定して揃える必要がある。 — `component/libraries/libraries-session_store.json#s8`

**① セッションストアの設定**
`SessionStoreHandler` の設定に加えて、`SessionManager` を `sessionManager` というコンポーネント名で登録する。`availableStores` リストに `HiddenStore`、`DbStore`、`HttpSessionStore` などを並べる。

```xml
<component name="sessionManager" class="nablarch.common.web.session.SessionManager">
  <property name="defaultStoreName" value="db"/>
  <property name="availableStores">
    <list>
      <component class="nablarch.common.web.session.store.HiddenStore"/>
      <component-ref name="dbStore"/>
      <component class="nablarch.common.web.session.store.HttpSessionStore"/>
    </list>
  </property>
</component>
```
— `component/libraries/libraries-session_store.json#s4`

**② HiddenStore のデフォルト暗号化設定**

| 設定項目 | 設定内容 |
|---|---|
| 暗号化アルゴリズム | AES |
| 暗号化キー | アプリケーションサーバ内で共通の自動生成されたキーを使用 |

— `component/libraries/libraries-session_store.json#s8`

**③ 複数 AP サーバ時のハマりどころと対策**
AP サーバが冗長化されている場合、**サーバごとに異なるキーが生成されるため復号に失敗するケース** がある。この場合、明示的に暗号化/復号キーを設定する:

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
- 鍵と IV は base64 エンコードした値を設定する。
- 鍵生成は `KeyGenerator`、IV 生成は `SecureRandom` を使用、base64 は `getEncoder()` の `Encoder` を使う。 — `component/libraries/libraries-session_store.json#s8`

**注意点**
- セッションストアに保存するオブジェクトはシリアライズ可能な Java Beans オブジェクトである必要がある。プロパティは Java 基本型またはシリアライズ可能な Java Beans、配列・コレクションも可。 — `component/libraries/libraries-session_store.json#s3`
