**結論**: Nablarchの多言語化は、言語ごとのプロパティファイル（`messages.properties` / `messages_en.properties`）と `PropertiesStringResourceLoader` の設定、さらにリクエストごとの言語をスレッドコンテキストに保持する `LanguageAttribute` の設定によって実現します。

**根拠**:

### 1. 言語ごとのプロパティファイルを作成する

`messages.properties`（デフォルト言語）と、サポートする言語ごとのファイルを用意します。

```
src/main/resources/
  messages.properties        # デフォルトの言語（例：日本語）
  messages_en.properties     # 英語用
```

### 2. PropertiesStringResourceLoader を設定する

コンポーネント設定ファイルにサポート言語とデフォルト言語を設定します。

```xml
<component class="nablarch.core.cache.BasicStaticDataCache" name="messageCache">
  <property name="loader">
    <component class="nablarch.core.message.PropertiesStringResourceLoader">
      <!-- サポートする言語 -->
      <property name="locales">
        <list>
          <value>en</value>
        </list>
      </property>
      <!-- デフォルトの言語（必ず設定すること） -->
      <property name="defaultLocale" value="ja" />
    </component>
  </property>
</component>
```

> デフォルト言語を設定しない場合、OS環境依存の `Locale.getDefault()` が使用され、環境によって動作が変わるため必ず設定してください。

### 3. ThreadContextHandler でリクエストごとの言語を管理する

`LanguageAttribute`（固定言語）または `LanguageAttributeInHttpCookie`（ユーザが選択した言語をクッキーに保持）を設定します。

```xml
<component class="nablarch.common.handler.threadcontext.ThreadContextHandler">
  <property name="attributes">
    <list>
      <!-- 言語（固定の場合） -->
      <component class="nablarch.common.handler.threadcontext.LanguageAttribute">
        <property name="defaultLanguage" value="ja" />
      </component>
    </list>
  </property>
</component>
```

### 4. ユーザに言語を選択させる場合

`LanguageAttributeInHttpCookie` と `LanguageAttributeInHttpUtil` を組み合わせます。

**設定例**:
```xml
<component name="languageAttribute"
           class="nablarch.common.web.handler.threadcontext.LanguageAttributeInHttpCookie">
  <property name="defaultLanguage" value="ja" />
  <property name="supportedLanguages" value="ja,en" />
</component>
```

**JSP例**（言語切り替えリンク）:
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

**ハンドラ例**（言語を保持）:
```java
public class I18nHandler implements HttpRequestHandler {
    public HttpResponse handle(HttpRequest request, ExecutionContext context) {
        String language = request.getParamMap().containsKey("user.language")
            ? request.getParam("user.language")[0] : null;
        if (StringUtil.hasValue(language)) {
            LanguageAttributeInHttpUtil.keepLanguage(request, context, language);
        }
        return context.handleNext(request);
    }
}
```

**注意点**: メッセージ取得時に使用される言語は `ThreadContext#getLanguage` が返すロケールで決まります。`ThreadContext` に言語が設定されていない場合は `Locale.getDefault()` が使用されます。

参照: component/libraries/libraries-message.json:s8, component/handlers/handlers-thread-context-handler.json:s4, component/handlers/handlers-thread-context-handler.json:s7