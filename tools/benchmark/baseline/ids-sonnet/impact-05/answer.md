**結論**: Nablarch の **HIDDENストア** を使えば、HIDDEN フィールドへの入力情報の保持を簡単に実装できる。ただし AP サーバ複数台構成では **暗号化キーを明示的に統一しないと復号失敗が起きる**ため、必ず共通キーを設定すること。

---

**根拠**:

① **HIDDENストアの使い方**
入力～確認～完了画面でフォーム入力を HIDDEN フィールドに保持したい場合、`HiddenStore` を使う（複数タブを許容したい場合に選択するストア）。JSP には `<n:hiddenStore>` タグを記述するだけでよい。(`component/libraries/libraries-session_store.json:s5`)

```jsp
<n:form>
  <n:hiddenStore name="nablarch_hiddenStore" />
</n:form>
```

② **格納するのは Entity（Form ではない）**
セッションストアには Form でなく Entity を格納すること。Form には未バリデーションの外部入力値が含まれるためセキュリティリスクが高く、業務ロジックとの密結合も生じる。(`component/libraries/libraries-session_store.json:s5`)

③ **AP サーバ複数台構成でのハマりどころ**
HIDDENストアのデフォルト暗号化キーは **サーバ起動時にサーバごとに自動生成** される。AP サーバが冗長化されている場合、あるサーバで暗号化したデータを別サーバが受け取ると復号に失敗する。対策として、全サーバで共通の `key` と `iv` を XML コンポーネント定義に明示的に設定する。(`component/libraries/libraries-session_store.json:s8`)

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

鍵は `KeyGenerator`、IV は `SecureRandom` で生成し、base64 エンコードして設定する。(`component/libraries/libraries-session_store.json:s8`)

④ **改竄チェック**
HIDDENストアの改竄を検知した場合はステータスコード 400 の `HttpErrorResponse` が送出される。(`component/handlers/handlers-SessionStoreHandler.json:s7`)

---

**注意点**:
- 複数タブを**許容しない**場合（タブ間でデータが干渉してはいけない画面フロー）は DBストアを選択すること。(`component/libraries/libraries-session_store.json:s5`)
- `SessionStoreHandler` と `SessionManager`（コンポーネント名は `"sessionManager"` 固定）の設定も必要。(`component/handlers/handlers-SessionStoreHandler.json:s5`, `component/libraries/libraries-session_store.json:s4`)
- 共通キー・IV は機密情報のため、ソースコードやリポジトリへの平文コミットは避け、環境変数や暗号化設定管理の仕組みで注入することを推奨。

参照: component/libraries/libraries-session_store.json:s5, component/libraries/libraries-session_store.json:s8, component/libraries/libraries-session_store.json:s4, component/handlers/handlers-SessionStoreHandler.json:s5, component/handlers/handlers-SessionStoreHandler.json:s7