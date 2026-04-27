**結論**: Nablarch には画面の多言語対応（日本語・英語など切り替え）を実現する標準機能が複数用意されている。メッセージ・ラベルを多言語化するには「メッセージ機能の多言語化」と「JSP リソースパスの言語別切り替え」の 2 通りのアプローチがある。コード名称の多言語化も別途サポートされている。

---

**根拠**:

### 1. メッセージの多言語化（プロパティファイル方式）

`PropertiesStringResourceLoader` に `locales` と `defaultLocale` を設定し、言語ごとのプロパティファイル（`messages.properties` / `messages_en.properties` など）を用意することで多言語化できる。メッセージ取得時の言語は `ThreadContext#getLanguage` が返すロケールで決まる。[component/libraries/libraries-message.json:s5]

```xml
<component class="nablarch.core.message.PropertiesStringResourceLoader">
  <property name="locales">
    <list><value>en</value></list>
  </property>
  <property name="defaultLocale" value="ja" />
</component>
```

> 注意: `defaultLocale` を必ず設定すること。未設定の場合は OS 設定に依存し障害の原因になる。[component/libraries/libraries-message.json:s5]

### 2. JSP での言語切り替え方法（2 通り）

**方法 A: `n:message` タグを使った 1 JSP ファイルでの多言語対応**  
`<n:message messageId="...">` タグを使うと、スレッドコンテキストの言語設定に応じたメッセージを 1 つの JSP から出力できる。`language` 属性で特定箇所だけ言語を固定することも可能。ただし、この方法は画面レイアウトが崩れる可能性があるため、レイアウト崩れを許容できる場合のみ使用すること。[processing-pattern/web-application/web-application-feature_details.json:s12] [component/libraries/libraries-tag.json:s2]

**方法 B: 言語ごとにリソースパスを切り替える**  
`HttpResponseHandler` の `contentPathRule` に `DirectoryBasedResourcePathRule`（ディレクトリ名 = 言語名）または `FilenameBasedResourcePathRule`（ファイル名サフィックス `_言語名`）を設定すると、言語ごとに別の JSP ファイルに自動的にフォワードできる。こちらがレイアウトを崩さずに多言語対応する推奨方法。[component/handlers/handlers-http_response_handler.json:s7] [processing-pattern/web-application/web-application-feature_details.json:s12]

### 3. ユーザによる言語選択（Cookie / セッション保持）

`LanguageAttributeInHttpCookie` または `LanguageAttributeInHttpSession` と `LanguageAttributeInHttpUtil.keepLanguage()` を組み合わせることで、ユーザが画面上のリンクで言語を選択・保持できる仕組みを作れる。[component/handlers/handlers-thread_context_handler.json:s7]

`ThreadContextHandler` の `attributes` に `LanguageAttributeInHttpCookie` を設定し、コンポーネント名を `"languageAttribute"` にすることが必須。[component/handlers/handlers-thread_context_handler.json:s7]

### 4. コード名称の多言語化

コード名称テーブルに言語ごとのデータ（`LANG` カラム）を用意し、`CodeUtil.getName("GENDER", "MALE", Locale.ENGLISH)` のように Locale を指定して取得できる。ただし、JSP カスタムタグライブラリでは言語指定による値取得はできない。[component/libraries/libraries-code.json:s3]

---

**注意点**:
- `n:message` タグ（方法 A）はレイアウト崩れのリスクがあるため、安全に多言語対応するには方法 B（リソースパス切り替え）を優先すること [processing-pattern/web-application/web-application-feature_details.json:s12]
- `defaultLocale` の未設定は OS 依存となり本番障害の原因になる [component/libraries/libraries-message.json:s5]
- `messages.properties`（デフォルトロケール用）が存在しない場合はエラーになる [component/libraries/libraries-message.json:s5]
- カスタムレスポンスライターを使用している場合、`contentPathRule` によるリソースパス切り替えは使用不可 [component/handlers/handlers-http_response_handler.json:s7]

参照: component/libraries/libraries-message.json:s5, processing-pattern/web-application/web-application-feature_details.json:s12, component/libraries/libraries-tag.json:s2, component/handlers/handlers-thread_context_handler.json:s7, component/handlers/handlers-thread_context_handler.json:s5, component/handlers/handlers-http_response_handler.json:s7, component/libraries/libraries-code.json:s3