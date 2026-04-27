**質問**: ファイルアップロード機能を作るが、巨大なファイルを送りつけてサーバを落とす攻撃を防ぎたい。アップロードサイズに上限を設ける仕組みは Nablarch にある？

---

**結論**: Nablarch は `MultipartHandler` に **アップロードサイズ上限** と **アップロードファイル数上限** の両方を設ける仕組みを提供している。サイズ上限は `contentLengthLimit` プロパティで設定し、超過時は **413 (Payload Too Large)** を返す。DoS 攻撃防止のため設定省略（= 無制限）ではなく **常に設定する** ことが推奨されている。 — `component/handlers/handlers-multipart_handler.json#s6`

**① アップロードサイズの上限**
アップロードサイズの上限を超えると 413(Payload Too Large) を返す。設定省略時は **無制限**。DoS 攻撃防止のため常に設定すること。

| プロパティ名 | 必須 | デフォルト値 | 説明 |
|---|---|---|---|
| contentLengthLimit | — | 無制限 | アップロードサイズ(Content-Length)の上限(バイト数) |

```xml
<component class="nablarch.fw.web.upload.MultipartHandler" name="multipartHandler">
  <property name="uploadSettings">
    <component class="nablarch.fw.web.upload.UploadSettings">
      <property name="contentLengthLimit" value="1000000" />
    </component>
  </property>
</component>
```

> **補足**: 上限はファイル単位ではなく 1 リクエスト全体の上限。複数ファイルの場合はファイルサイズ合計値（Content-Length）でチェックされる。ファイル単位でのサイズチェックが必要な場合はアクション側で実装する。 — `component/handlers/handlers-multipart_handler.json#s6`

**② アップロードファイル数の上限**
上限を超えるファイル数がアップロードされた場合は 400(Bad Request) を返す。

| プロパティ名 | 必須 | デフォルト値 | 説明 |
|---|---|---|---|
| maxFileCount | — | -1 | 一度にアップロードできるファイル数の上限。0 以上: 上限値、負数: 無制限 |

```xml
<component class="nablarch.fw.web.upload.MultipartHandler" name="multipartHandler">
  <property name="uploadSettings">
    <component class="nablarch.fw.web.upload.UploadSettings">
      <property name="maxFileCount" value="100" />
    </component>
  </property>
</component>
```
— `component/handlers/handlers-multipart_handler.json#s7`
