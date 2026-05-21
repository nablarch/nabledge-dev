既にJSONファイルから全セクションの内容を取得済みです。Step 5〜8を実行します。

---

**結論**: メッセージの多言語化は、言語ごとのプロパティファイル（`messages_en.properties` 等）を用意し、`PropertiesStringResourceLoader` にサポート言語とデフォルト言語を設定することで実現する。ユーザの言語切り替えには `LanguageAttributeInHttpCookie` と `LanguageAttributeInHttpUtil.keepLanguage()` を組み合わせて使用する。

---

**根拠**:

### 1. プロパティファイルの準備

日本語をデフォルト、英語をサポート対象とする場合のファイル構成:

```
main/resources/messages.properties       # デフォルト（日本語）
               messages_en.properties    # 英語
```

各ファイルの内容例:

```properties
# messages.properties（日本語）
label.user.register.title=ユーザ登録画面
errors.login=ログインに失敗しました。

# messages_en.properties（英語）
label.user.register.title=User Registration
errors.login=Login failed.
```

> UTF-8 で作成すればよく、native2ascii は不要。`messages.properties`（デフォルト）が存在しない場合はエラーになる。

### 2. コンポーネント設定（必須）

`PropertiesStringResourceLoader` にサポート言語とデフォルト言語を設定する。**`defaultLocale` の設定は必須**（未設定だとOSの言語設定に依存し、障害原因になる）。

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

メッセージの取得時に使用される言語は `ThreadContext#getLanguage` が返すロケールで決まる。

### 3. ユーザが言語を選択できる画面を実装する

クッキーで選択言語を保持する場合の設定:

```xml
<!-- コンポーネント名を "languageAttribute" にすること -->
<component name="languageAttribute"
           class="nablarch.common.web.handler.threadcontext.LanguageAttributeInHttpCookie">
  <property name="defaultLanguage" value="ja" />
  <property name="supportedLanguages" value="ja,en" />
</component>
```

JSP（言語切り替えリンク）:

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

言語選択を受け取るハンドラ（複数画面で切り替えを行う場合はハンドラとして実装）:

```java
public class I18nHandler implements HttpRequestHandler {
    public HttpResponse handle(HttpRequest request, ExecutionContext context) {
        String language = request.getParamMap().containsKey("user.language")
            ? request.getParam("user.language")[0] : null;
        if (StringUtil.hasValue(language)) {
            // クッキーとスレッドコンテキストの両方に言語を設定する
            // サポート対象外の言語が指定された場合は何もしない
            LanguageAttributeInHttpUtil.keepLanguage(request, context, language);
        }
        return context.handleNext(request);
    }
}
```

### 4.（オプション）JSPファイルも言語ごとに切り替える

メッセージだけでなく JSP 自体も言語ごとに切り替えたい場合は、`HttpResponseHandler` の `contentPathRule` プロパティを設定する。

```xml
<component name="resourcePathRule"
           class="nablarch.fw.web.i18n.DirectoryBasedResourcePathRule" />

<component class="nablarch.fw.web.handler.HttpResponseHandler">
  <property name="contentPathRule" ref="resourcePathRule" />
</component>
```

ディレクトリ構成例（`DirectoryBasedResourcePathRule` の場合）:

```
コンテキストルート
├─en
│  └─management/user/search.jsp
└─ja
   └─management/user/search.jsp
```

---

**注意点**:
- `defaultLocale` を未設定にすると `Locale.getDefault().getLanguage()` が採用され、実行環境のOSによって動作が変わる。必ず明示的に設定すること。
- `LanguageAttributeInHttpUtil.keepLanguage()` は、指定言語が `supportedLanguages` に含まれない場合、クッキー・スレッドコンテキストへの設定を行わない。

参照: `libraries-message.json:s8`, `handlers-thread-context-handler.json:s7`, `handlers-http-response-handler.json:s7`, `libraries-message.json:s7`

---