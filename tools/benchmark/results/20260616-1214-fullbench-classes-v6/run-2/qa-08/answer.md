**結論**: Nablarchのメッセージ多言語化は、言語ごとのプロパティファイル（`messages_言語.properties`）を用意し、`PropertiesStringResourceLoader` にサポート言語を設定することで実現します。ユーザが言語を切り替える場合は、`LanguageAttributeInHttpCookie` などと `LanguageAttributeInHttpUtil.keepLanguage` を組み合わせます。

**根拠**:

### 1. メッセージプロパティファイルの多言語化

言語ごとのプロパティファイルを作成します：

```
main/resources/messages.properties       # デフォルト言語（例: 日本語）
               messages_en.properties    # 英語
               messages_zh.properties    # 中国語
```

コンポーネント設定ファイルで `PropertiesStringResourceLoader` にサポート言語を設定します：

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
      <!-- デフォルトの言語（必須） -->
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

> **重要**: `defaultLocale` を必ず設定してください。未設定の場合 `Locale.getDefault().getLanguage()` が使用され、実行環境のOSによって値が変わり障害の原因になります。

### 2. スレッドコンテキストへの言語設定

メッセージ取得時の言語は `ThreadContext#getLanguage` の値に基づきます。`ThreadContextHandler` の設定に言語属性クラスを追加します：

```xml
<component class="nablarch.common.handler.threadcontext.ThreadContextHandler">
  <property name="attributes">
    <list>
      <!-- 言語（固定値の場合） -->
      <component class="nablarch.common.handler.threadcontext.LanguageAttribute">
        <property name="defaultLanguage" value="ja" />
      </component>
    </list>
  </property>
</component>
```

### 3. ユーザが言語を切り替えられるようにする（クッキー利用）

ユーザが言語を選択できる場合は `LanguageAttributeInHttpCookie` を使います：

```xml
<component name="languageAttribute"
           class="nablarch.common.web.handler.threadcontext.LanguageAttributeInHttpCookie">
  <property name="defaultLanguage" value="ja" />
  <property name="supportedLanguages" value="ja,en" />
</component>
```

言語切り替えリンク（JSP例）:

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

ハンドラで `LanguageAttributeInHttpUtil.keepLanguage` を呼び出してクッキーとスレッドコンテキストに言語を保存します：

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

**注意点**:
- `messages.properties`（デフォルト言語ファイル）が存在しない場合はエラーで処理が終了します。必ず作成してください。
- `LanguageAttributeInHttpUtil` を使用するため、コンポーネント名は `languageAttribute` にする必要があります。

参照: libraries-message.json:s8, handlers-thread-context-handler.json:s7, handlers-thread-context-handler.json:s4