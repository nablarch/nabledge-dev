十分な情報が集まりました。回答を生成します。

---

**結論**: Nablarchの多言語化は、言語ごとのプロパティファイルを用意して `PropertiesStringResourceLoader` に `locales`/`defaultLocale` を設定し、画面では `<n:message>` タグでメッセージを出力することで実現する。ユーザが言語を切り替える場合は `LanguageAttributeInHttpCookie` 等と `LanguageAttributeInHttpUtil.keepLanguage()` を組み合わせる。

---

**根拠**:

### 1. プロパティファイルの準備

デフォルト言語（日本語）と英語用のプロパティファイルを作成する。

```
main/resources/messages.properties       # デフォルト言語（日本語）
               messages_en.properties    # 英語用
```

```properties
# messages.properties（日本語）
label.user.name=氏名
errors.required=入力してください。

# messages_en.properties（英語）
label.user.name=Name
errors.required=This field is required.
```

### 2. PropertiesStringResourceLoader の設定

コンポーネント設定ファイルに以下を追加する。

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
      <!-- デフォルトの言語（必須設定） -->
      <property name="defaultLocale" value="ja" />
    </component>
  </property>
</component>

<component name="stringResourceHolder" class="nablarch.core.message.StringResourceHolder">
  <property name="stringResourceCache" ref="messageCache" />
</component>
```

### 3. スレッドコンテキストへの言語設定

`ThreadContextHandler` に言語属性を追加する。

```xml
<component class="nablarch.common.handler.threadcontext.ThreadContextHandler">
  <property name="attributes">
    <list>
      <!-- 言語：クッキーに保持する場合 -->
      <component name="languageAttribute"
                 class="nablarch.common.web.handler.threadcontext.LanguageAttributeInHttpCookie">
        <property name="defaultLanguage" value="ja" />
        <property name="supportedLanguages" value="ja,en" />
      </component>
    </list>
  </property>
</component>
```

### 4. ユーザが言語を選択する仕組み

JSPにリンクを設置し、ハンドラで `LanguageAttributeInHttpUtil.keepLanguage()` を呼ぶ。

```jsp
<!-- JSP：言語切り替えリンク -->
<n:submitLink uri="/action/menu/index" name="switchToEnglish">
  English
  <n:param paramName="user.language" value="en" />
</n:submitLink>
<n:submitLink uri="/action/menu/index" name="switchToJapanese">
  日本語
  <n:param paramName="user.language" value="ja" />
</n:submitLink>
```

```java
// ハンドラ：選択言語をクッキーとスレッドコンテキストに保持
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

### 5. JSP でのメッセージ出力

```jsp
<!-- messageId を指定して言語に応じたメッセージを出力 -->
<n:message messageId="label.user.name" />
```

---

**注意点**:

- `defaultLocale` の設定を必ず行うこと。未設定だと `Locale.getDefault().getLanguage()` が使われ、OS環境依存となり障害の原因になる。
- `<n:message>` タグを使う方法は画面レイアウトが崩れる可能性がある。レイアウト崩れを許容できない場合は、`DirectoryBasedResourcePathRule` / `FilenameBasedResourcePathRule` を使って言語ごとに JSP ファイルを切り替える方式を選択すること。

参照: `component/libraries/libraries-message.json:s8`, `component/handlers/handlers-thread-context-handler.json:s4`, `component/handlers/handlers-thread-context-handler.json:s7`, `component/handlers/handlers-http-response-handler.json:s7`, `component/libraries/libraries-tag.json:s31`, `processing-pattern/web-application/web-application-feature-details.json:s12`

---