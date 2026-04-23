**結論**: 画面遷移間のフォーム入力を HIDDEN に持たせるには、Nablarch の **セッションストア（HIDDENストア）** を使うのが標準的なやり方です。ただし AP サーバ複数台構成では **暗号化キーをサーバ間で共通化しないとリクエストが別サーバに届いた際に復号失敗する** というハマりどころがあります。

---

**根拠**:

1. **HIDDENストアの仕組み**  
   `component/libraries/libraries-session_store.json:s1` によると、セッションストアには DBストア・HIDDENストア・HTTPセッションストアの 3 種類があります。HIDDENストアは「クライアントサイド（`hidden` タグ）を使って画面間でセッション変数を引き回す」方式で、入力→確認→完了画面間で入力情報を保持しかつ **複数タブでの画面操作を許容したい** 場合に使います。

2. **JSP への組み込み方法**  
   `component/libraries/libraries-session_store.json:s5` によると、入力・確認画面の JSP に `<n:hiddenStore name="nablarch_hiddenStore" />` を `<n:form>` 内に置くだけで対応できます。Entityをセッションストアに格納することが推奨されており、Formを格納すると密結合・セキュリティリスクが高まると記載されています。

3. **複数台構成でのハマりどころ（重要）**  
   `component/libraries/libraries-session_store.json:s8` に明記されています：  
   > 「アプリケーションサーバが冗長化されている場合、サーバごとに異なる（自動生成された）AESキーが生成されるため、別サーバで復号に失敗するケースがある。この場合、**明示的に暗号化/復号のキーを設定**する必要がある。」  
   
   対処法は `HiddenStore` の `encryptor` プロパティに `AesEncryptor` を設定し、`key` と `iv` を全サーバ共通の固定値（base64エンコード）にすることです：
   ```xml
   <component class="nablarch.common.web.session.store.HiddenStore">
     <property name="encryptor">
       <component class="nablarch.common.encryption.AesEncryptor">
         <property name="base64Key">
           <component class="nablarch.common.encryption.Base64Key">
             <property name="key" value="（全サーバ共通のbase64エンコードAESキー）" />
             <property name="iv" value="（全サーバ共通のbase64エンコードIV）" />
           </component>
         </property>
       </component>
     </property>
   </component>
   ```

4. **改竄検知の動作**  
   `component/handlers/handlers-SessionStoreHandler.json:s7` によると、HIDDENストアの改竄を検知した場合はステータスコード 400 の `HttpErrorResponse` が送出されます。これはユーザーが hidden の内容を書き換えた場合だけでなく、キーが不一致の場合も同様に発生するため、複数台構成で設定漏れがあると本番で突然 400 エラーが多発します。

5. **ウィンドウスコープ（旧来のhidden暗号化機能）は非推奨**  
   `component/libraries/libraries-tag.json:s3` に「画面間での入力データ保持には `:ref:session_store` を使うこと。ウィンドウスコープは非推奨」と明記されています。また `component/libraries/libraries-tag.json:s4` でも hidden 暗号化機能自体が非推奨とされており、「特に理由がない限り `useHiddenEncryption` には `false` を設定すること」と記載されています。

6. **セッション有効期間の保存先にも注意**  
   `component/handlers/handlers-SessionStoreHandler.json:s9` によると、セッションの有効期間はデフォルトで HTTPセッションに保存されます。複数台構成でスティッキーセッションなしの場合は `DbManagedExpiration` を設定してデータベースに保存先を変更することが推奨されます（`component/handlers/handlers-SessionStoreHandler.json:s10`）。

---

**注意点**:
- HIDDENストアを使う場合は `SessionStoreHandler` を `multipart_handler` より後ろ、`forwarding_handler` より前に配置する必要があります（`component/handlers/handlers-SessionStoreHandler.json:s4`）。
- セッション変数には Form ではなく Entity を格納すること（`component/libraries/libraries-session_store.json:s5`）。
- 鍵は `KeyGenerator` と `SecureRandom` で生成し、base64 エンコードした値を設定します（`component/libraries/libraries-session_store.json:s8`）。

参照: component/libraries/libraries-session_store.json:s1, component/libraries/libraries-session_store.json:s5, component/libraries/libraries-session_store.json:s8, component/handlers/handlers-SessionStoreHandler.json:s4, component/handlers/handlers-SessionStoreHandler.json:s7, component/handlers/handlers-SessionStoreHandler.json:s9, component/handlers/handlers-SessionStoreHandler.json:s10, component/libraries/libraries-tag.json:s3, component/libraries/libraries-tag.json:s4