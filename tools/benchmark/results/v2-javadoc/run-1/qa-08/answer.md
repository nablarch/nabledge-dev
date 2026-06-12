必要なセクションの内容が揃いました。回答を生成します。

---

**結論**: Nablarchの多言語化は、①言語ごとのメッセージプロパティファイルを用意、②`PropertiesStringResourceLoader`でサポート言語を設定、③`LanguageAttributeInHttpCookie`/`LanguageAttributeInHttpSession`でユーザの言語選択を保持、の3ステップで実現できる。JSPでは`<n:message>`タグが現在の言語に対応するメッセージを自動的に出力する。

---

**根拠**:

### 1. 言語ごとのプロパティファイルを準備する

`messages_言語.properties` の形式でファイルを作成する。デフォルト言語は `messages.properties`。

```
main/resources/messages.properties       # デフォルト言語（例: 日本語）
               messages_en.properties    # 英語
               messages_zh.properties    # 中国語
```

各ファイルに同じメッセージIDで言語ごとの文言を定義する:

```properties
# messages.properties（日本語）
login.title=ログイン
label.name=名前

# messages_en.properties（英語）
login.title=Login
label.name=Name
```

### 2. PropertiesStringResourceLoader にサポート言語を設定する

```xml
<component class="nablarch.core.cache.BasicStaticDataCache" name="messageCache">
  <property name="loader">
    <component class="nablarch.core.message.PropertiesStringResourceLoader">
      <!-- サポートする言語（デフォルト言語以外を列挙） -->
      <property name="locales">
        <list>
          <value>en</value>
          <value>zh</value>
        </list>
      </property>
      <!-- デフォルト言語は必ず明示設定すること -->
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

### 3. ユーザの言語選択を保持するコンポーネントを設定する

クッキーで言語を保持する場合:

```xml
<!-- コンポーネント名は "languageAttribute" にすること -->
<component name="languageAttribute"
           class="nablarch.common.web.handler.threadcontext.LanguageAttributeInHttpCookie">
  <property name="defaultLanguage" value="ja" />
  <property name="supportedLanguages" value="ja,en" />
</component>
```

セッションで保持する場合は `LanguageAttributeInHttpSession` を使用する。

### 4. 言語切り替えハンドラを実装する

```java
public class I18nHandler implements HttpRequestHandler {
    public HttpResponse handle(HttpRequest request, ExecutionContext context) {
        String language = getLanguage(request, "user.language");
        if (StringUtil.hasValue(language)) {
            // クッキーとスレッドコンテキストに選択された言語を設定する
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

言語切り替えリンク（JSP）:

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

```jsp
<!-- 現在の言語設定に応じてメッセージが切り替わる -->
<n:message messageId="login.title" />

<!-- 特定の言語を指定したい場合 -->
<n:message messageId="login.title" language="ja" />
```

### 6. （オプション）JSP自体を言語ごとに切り替える場合

`DirectoryBasedResourcePathRule`（言語ごとにディレクトリを分ける）か `FilenameBasedResourcePathRule`（ファイル名にサフィックスを付ける）を使い、HTTPレスポンスハンドラの `contentPathRule` に設定する:

```xml
<component name="resourcePathRule"
           class="nablarch.fw.web.i18n.DirectoryBasedResourcePathRule" />

<component class="nablarch.fw.web.handler.HttpResponseHandler">
  <property name="contentPathRule" ref="resourcePathRule" />
</component>
```

---

**注意点**:
- `defaultLocale` は必ず明示設定すること。未設定の場合 `Locale.getDefault().getLanguage()` が使われ、OS設定に依存して環境ごとに動作が変わり障害の原因になる。
- `messages.properties`（デフォルト言語ファイル）が存在しない場合はエラーとして処理が終了する。

参照: libraries-message.json:s8, handlers-thread-context-handler.json:s7, handlers-http-response-handler.json:s7, libraries-tag.json:s31

---