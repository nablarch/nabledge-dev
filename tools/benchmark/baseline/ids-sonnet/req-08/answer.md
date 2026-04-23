**結論**: Nablarch には `MultipartHandler` の `UploadSettings` を通じてアップロードサイズに上限を設ける仕組みがある。`contentLengthLimit` プロパティで1リクエスト全体のサイズ上限を設定でき、超過時は 413 (Payload Too Large) を返す。

**根拠**:

`MultipartHandler` の `UploadSettings` に `contentLengthLimit` プロパティを設定することで、アップロードサイズ（Content-Length）の上限をバイト数で指定できる。上限を超えた場合は 413 がクライアントに返却される。設定を省略すると無制限になるため、DoS攻撃防止のために**必ず設定すること**とされている。（`component/handlers/handlers-multipart_handler.json:s6`）

```xml
<component class="nablarch.fw.web.upload.MultipartHandler" name="multipartHandler">
  <property name="uploadSettings">
    <component class="nablarch.fw.web.upload.UploadSettings">
      <property name="contentLengthLimit" value="1000000" />
    </component>
  </property>
</component>
```
（`component/handlers/handlers-multipart_handler.json:s6`）

また、一度にアップロードできるファイル数の上限は `maxFileCount` で制御でき、上限超過時は 400 (Bad Request) を返す。未設定時のデフォルトは -1（無制限）で、0以上の値を設定するとその値が上限となる。（`component/handlers/handlers-multipart_handler.json:s7`）

**注意点**:
- `contentLengthLimit` はファイル単位ではなく **1リクエスト全体** のサイズ上限である。複数ファイルの場合はファイルサイズの合計値（Content-Length）でチェックされる。
- ファイル1件ずつの個別サイズチェックが必要な場合は、アクション側で独自に実装する必要がある。
- `contentLengthLimit` を省略すると無制限になるため、運用上は必ず値を設定すること。

参照: component/handlers/handlers-multipart_handler.json:s6, component/handlers/handlers-multipart_handler.json:s7