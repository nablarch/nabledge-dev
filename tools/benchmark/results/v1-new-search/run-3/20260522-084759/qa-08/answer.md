セクションの内容は既に読み込み済みです。Step 5〜8の回答生成と検証を行います。

---

**結論**: メッセージの多言語化は「言語別プロパティファイル + `PropertiesStringResourceLoader` の設定」で実現し、ユーザの言語切り替えは `ThreadContextHandler` の `LanguageAttributeInHttpCookie`（またはSession）と `LanguageAttributeInHttpUtil.keepLanguage()` を組み合わせて実装します。

---

**根拠**:

### 1. 言語別プロパティファイルを作成する

デフォルト言語用と各言語用のファイルを用意します。

```none
main/resources/messages.properties       # デフォルト言語（日本語）用
               messages_en.properties    # 英語用
```

### 2. `PropertiesStringResourceLoader` の多言語化設定

コンポーネント設定ファイルに以下を追加します。

```xml
<component class="nablarch.core.cache.BasicStaticDataCache" name="messageCache">
  <property name="loader">
    <component class="nablarch.core.message.PropertiesStringResourceLoader">
      <!-- サポートする言語（デフォルト言語は不要） -->
      <property name="locales">
        <list>
          <value>en</value>
        </list>
      </property>
      <!-- デフォルト言語（必須。未設定だとOS依存になり障害の原因になる） -->
      <property name="defaultLocale" value="ja" />
    </component>
  </property>
</component>

<component name="stringResourceHolder" class="nablarch.core.message.StringResourceHolder">
  <property name="stringResourceCache" ref="messageCache" />
</component>

<component name="initializer"
           class="nablarch.core.repository.initialization.BasicApplicationInitializer">
  <property name="initializeList">
    <list>
      <component-ref name="messageCache" />
    </list>
  </property>
</component>
```

> メッセージ取得時にどの言語が使われるかは `ThreadContext#getLanguage` が返すロケールで決定されます。

### 3. ThreadContextHandler に言語属性を設定する

```xml
<component class="nablarch.common.handler.threadcontext.ThreadContextHandler">
  <property name="attributes">
    <list>
      <!-- クッキーに言語を保持する場合 -->
      <component name="languageAttribute"
                 class="nablarch.common.web.handler.threadcontext.LanguageAttributeInHttpCookie">
        <property name="defaultLanguage" value="ja" />
        <property name="supportedLanguages" value="ja,en" />
      </component>
      <!-- 他の属性は省略 -->
    </list>
  </property>
</component>
```

### 4. 言語切り替えハンドラを実装する

```java
public class I18nHandler implements HttpRequestHandler {

    public HttpResponse handle(HttpRequest request, ExecutionContext context) {
        String language = getLanguage(request, "user.language");
        if (StringUtil.hasValue(language)) {
            // クッキーとスレッドコンテキストに言語を設定する
            LanguageAttributeInHttpUtil.keepLanguage(request, context, language);
        }
        return context.handleNext(request);
    }

    private String getLanguage(HttpRequest request, String paramName) {
        if (!request.getParamMap().containsKey(paramName)) {
            return null;
        }
        return request.getParam(paramName)[0];
    }
}
```

### 5. JSPで言語切り替えリンクを実装する

```jsp
<n:submitLink uri="/action/menu/index" name="switchToEnglish">
  English
  <n:param paramName="user.language" value="en" />
</n:submitLink>
<n:submitLink uri="/action/menu/index" name="switchToJapanese">
  日本語
  <n:param paramName="user.language" value="ja" />
</n:submitLink>
```

### 6. JSPでメッセージを表示する

```jsp
<span><n:message messageId="login.title" /></span>
```

### 7. （オプション）JSPファイル自体を言語ごとに切り替える場合

`HTTPレスポンスハンドラ` の `contentPathRule` に `DirectoryBasedResourcePathRule` または `FilenameBasedResourcePathRule` を設定することで、フォワード先のJSPを言語ごとに切り替えられます。

```xml
<component name="resourcePathRule" class="nablarch.fw.web.i18n.DirectoryBasedResourcePathRule" />

<component class="nablarch.fw.web.handler.HttpResponseHandler">
  <property name="contentPathRule" ref="resourcePathRule" />
</component>
```

---

**注意点**:
- `PropertiesStringResourceLoader.defaultLocale` は必ず設定すること。未設定の場合は `Locale.getDefault().getLanguage()` が使われ、OS設定によって動作が変わり障害の原因になります。
- `messages.properties`（デフォルト言語ファイル）が存在しない場合はエラーになります。

参照: `libraries-message.json:s8`, `libraries-message.json:s7`, `libraries-message.json:s11`, `handlers-thread-context-handler.json:s7`, `handlers-thread-context-handler.json:s4`, `handlers-http-response-handler.json:s7`

---