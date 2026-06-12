**結論**: Nablarchで多言語化を実装するには、①言語別プロパティファイルの作成、②`PropertiesStringResourceLoader`へのロケール設定、③`ThreadContextHandler`で言語属性を初期化する、の3ステップが必要です。ウェブアプリケーションでユーザーに言語選択させる場合は、`LanguageAttributeInHttpCookie`等と`LanguageAttributeInHttpUtil`を組み合わせて使います。

---

**根拠**:

### 1. 言語別プロパティファイルを作成する

デフォルト言語用（例: 日本語）は `messages.properties`、その他の言語は `messages_言語.properties` として配置します。

```none
main/resources/messages.properties       # デフォルト言語（例: 日本語）
               messages_en.properties    # 英語
               messages_zh.properties    # 中国語
```

**重要**: `messages.properties`（デフォルト言語用）が存在しない場合はエラーになります。

### 2. PropertiesStringResourceLoaderにサポート言語を設定する

コンポーネント設定ファイル（XML）に以下を追加します。

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
      <!-- デフォルトの言語（必ず明示的に設定すること） -->
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

### 3. ThreadContextHandlerで言語属性を設定する

`ThreadContext#getLanguage`が返すロケールに基づいてメッセージの言語が決まります。`ThreadContextHandler`にデフォルト言語を設定します。

```xml
<component class="nablarch.common.handler.threadcontext.ThreadContextHandler">
  <property name="attributes">
    <list>
      <!-- 言語 -->
      <component class="nablarch.common.handler.threadcontext.LanguageAttribute">
        <property name="defaultLanguage" value="ja" />
      </component>
      <!-- 他の属性は省略 -->
    </list>
  </property>
</component>
```

### 4. ユーザーに言語を選択させる（ウェブアプリケーションの場合）

クッキーやセッションで言語を保持するには `LanguageAttributeInHttpCookie` または `LanguageAttributeInHttpSession` を使います。

コンポーネント設定：

```xml
<!-- コンポーネント名を"languageAttribute"にすること（LanguageAttributeInHttpUtil使用のため） -->
<component name="languageAttribute"
           class="nablarch.common.web.handler.threadcontext.LanguageAttributeInHttpCookie">
  <property name="defaultLanguage" value="ja" />
  <property name="supportedLanguages" value="ja,en" />
</component>
```

言語選択ハンドラの実装例：

```java
public class I18nHandler implements HttpRequestHandler {
    public HttpResponse handle(HttpRequest request, ExecutionContext context) {
        String language = request.getParam("user.language") != null
            ? request.getParam("user.language")[0] : null;
        if (StringUtil.hasValue(language)) {
            // クッキーとスレッドコンテキストに言語を設定する
            LanguageAttributeInHttpUtil.keepLanguage(request, context, language);
        }
        return context.handleNext(request);
    }
}
```

JSP（言語切り替えリンク）：

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

### 5. JSPでメッセージを出力する

`n:message`タグでプロパティファイルのメッセージを画面に表示します。

```jsp
<n:message messageId="label.user.register.title" />
```

---

**注意点**:
- `PropertiesStringResourceLoader.defaultLocale`を**必ず明示的に設定**すること。未設定の場合、`Locale.getDefault().getLanguage()`が使われ、OS設定によって変化するため障害の原因になります。
- `messages.properties`（デフォルト言語ファイル）が存在しない場合はエラーになります。
- ウェブアプリケーションでメッセージタグを使った国際化は画面レイアウトが崩れる可能性があるため、レイアウト崩れを許容できる場合のみ使用すること。

参照: libraries-message.json:s8, handlers-thread-context-handler.json:s4, handlers-thread-context-handler.json:s7, handlers-http-response-handler.json:s7, web-application-feature-details.json:s12