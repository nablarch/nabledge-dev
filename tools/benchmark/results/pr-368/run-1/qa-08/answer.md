**結論**: Nablarchの多言語化は、①メッセージ管理（`PropertiesStringResourceLoader`の言語設定＋言語別プロパティファイル）と、②スレッドコンテキストへの言語設定（`LanguageAttribute`系クラス）を組み合わせて実現します。JSPの文言切り替えには `<n:message>` タグ、またはHTTPレスポンスハンドラによるリソースパス切り替えの2通りの方法があります。

---

**根拠**:

#### 1. メッセージの多言語化設定

`PropertiesStringResourceLoader` にサポートする言語と `defaultLocale` を設定します。

```xml
<component class="nablarch.core.cache.BasicStaticDataCache" name="messageCache">
  <property name="loader">
    <component class="nablarch.core.message.PropertiesStringResourceLoader">
      <!-- サポートする言語 -->
      <property name="locales">
        <list>
          <value>en</value>
          <value>zh</value>
        </list>
      </property>
      <!-- デフォルト言語（必ず明示すること） -->
      <property name="defaultLocale" value="ja" />
    </component>
  </property>
</component>
```

言語別のプロパティファイルを `messages_言語.properties` という名前で作成します。

```
main/resources/messages.properties       # デフォルト言語用（必須）
               messages_en.properties    # 英語用
               messages_zh.properties    # 中国語用
```

> `defaultLocale` を設定しないと `Locale.getDefault()` が使われ、OS依存で障害の原因になるため必ず設定すること。

#### 2. スレッドコンテキストへの言語設定

`ThreadContextHandler` の `attributes` に言語属性クラスを設定します。

```xml
<component class="nablarch.common.handler.threadcontext.ThreadContextHandler">
  <property name="attributes">
    <list>
      <!-- 固定の言語を使用する場合 -->
      <component class="nablarch.common.handler.threadcontext.LanguageAttribute">
        <property name="defaultLanguage" value="ja" />
      </component>
    </list>
  </property>
</component>
```

ユーザが言語を選択できるようにする場合は、`LanguageAttributeInHttpCookie` や `LanguageAttributeInHttpSession` を使います。

```xml
<!-- クッキーに言語を保持する場合 -->
<component name="languageAttribute"
           class="nablarch.common.web.handler.threadcontext.LanguageAttributeInHttpCookie">
  <property name="defaultLanguage" value="ja" />
  <property name="supportedLanguages" value="ja,en" />
</component>
```

言語切り替えリンクの実装（JSP）:

```jsp
<n:submitLink uri="/action/menu/index" name="switchToEnglish">
  英語
  <n:param paramName="user.language" value="en" />
</n:submitLink>
<n:submitLink uri="/action/menu/index" name="switchToJapanese">
  日本語
  <n:param paramName="user.language" value="ja" />
</n:submitLink>
```

ハンドラでの言語保持:

```java
public class I18nHandler implements HttpRequestHandler {
    public HttpResponse handle(HttpRequest request, ExecutionContext context) {
        String language = request.getParam("user.language")[0];
        if (StringUtil.hasValue(language)) {
            LanguageAttributeInHttpUtil.keepLanguage(request, context, language);
        }
        return context.handleNext(request);
    }
}
```

#### 3. JSP文言の切り替え（2通りの方法）

**方法A: `<n:message>` タグ**（1つのJSPで多言語対応するが、レイアウト崩れの可能性あり）

```jsp
<n:message messageId="label.user.register.title" />
```

**方法B: HTTPレスポンスハンドラによるリソースパス切り替え**（レイアウト崩れを防ぎたい場合に推奨）

```xml
<component name="resourcePathRule"
           class="nablarch.fw.web.i18n.DirectoryBasedResourcePathRule" />

<component class="nablarch.fw.web.handler.HttpResponseHandler">
  <property name="contentPathRule" ref="resourcePathRule" />
</component>
```

ディレクトリ構成例（`DirectoryBasedResourcePathRule` 使用時）:

```
コンテキストルート
├─en
│  └─management/user/search.jsp
└─ja
   └─management/user/search.jsp
```

#### 4. コード名称の多言語化

コード名称テーブルに言語ごとのデータを登録します。

| ID | VALUE | LANG | NAME |
|---|---|---|---|
| GENDER | MALE | ja | 男性 |
| GENDER | MALE | en | Male |

`CodeUtil` で言語を指定して取得:

```java
CodeUtil.getName("GENDER", "MALE", Locale.JAPANESE);  // -> 男性
CodeUtil.getName("GENDER", "MALE", Locale.ENGLISH);   // -> Male
```

---

**注意点**:
- `messages.properties`（デフォルト言語用）が存在しない場合はエラーになります
- JSP切り替えで `<n:message>` タグを使うとレイアウト崩れの可能性があるため、崩れが許容できない場合はリソースパス切り替えを使用してください
- JSPカスタムタグライブラリでは `CodeUtil` のような言語指定によるコード値取得はできません

参照: component/libraries/libraries-message.json:s8, component/handlers/handlers-thread-context-handler.json:s7, component/handlers/handlers-thread-context-handler.json:s4, component/handlers/handlers-http-response-handler.json:s7, component/libraries/libraries-tag.json:s31, component/libraries/libraries-tag.json:s32, component/libraries/libraries-code.json:s8, processing-pattern/web-application/web-application-feature-details.json:s12