**結論**: Nablarchで多言語化（メッセージ・ラベルの日本語・英語切り替え）を実装するには、①メッセージの多言語化（言語別プロパティファイルと`PropertiesStringResourceLoader`設定）と、②ユーザーの言語選択を保持する仕組み（`LanguageAttributeInHttpCookie`等＋`LanguageAttributeInHttpUtil`）を組み合わせます。

**根拠**:

### 1. メッセージ・ラベルの多言語化

言語別にプロパティファイルを作成し、`PropertiesStringResourceLoader`でサポート言語を設定します。

**プロパティファイルの配置**:
```none
main/resources/messages.properties       # デフォルト（日本語など）
               messages_en.properties    # 英語
               messages_ja.properties    # 日本語（defaultLocaleと異なる場合）
```

**コンポーネント設定ファイル（XML）**:
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

メッセージ取得時の言語は `ThreadContext#getLanguage` が返すロケールで決定されます。

> **重要**: `defaultLocale`は必ず設定すること。未設定の場合はOSの設定によって値が変わり、障害の原因になります。

---

### 2. ユーザーの言語選択を保持する仕組み

ユーザーが言語を切り替えられるようにするには、`ThreadContextHandler`の属性として`LanguageAttributeInHttpCookie`（またはSession版）を設定します。

**コンポーネント設定（コンポーネント名は`languageAttribute`固定）**:
```xml
<component name="languageAttribute"
           class="nablarch.common.web.handler.threadcontext.LanguageAttributeInHttpCookie">
  <property name="defaultLanguage" value="ja" />
  <property name="supportedLanguages" value="ja,en" />
</component>
```

**言語切り替えハンドラ実装例**:
```java
public class I18nHandler implements HttpRequestHandler {

    public HttpResponse handle(HttpRequest request, ExecutionContext context) {
        String language = getLanguage(request, "user.language");
        if (StringUtil.hasValue(language)) {
            // クッキーとスレッドコンテキストに選択言語を設定する
            // サポート対象外の言語が指定された場合は設定しない
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

**JSP（言語切り替えリンク）**:
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

---

### 3. JSPレイアウト全体を言語ごとに切り替える場合（JSP多言語化）

JSP自体を言語別に用意する場合は、`HTTPレスポンスハンドラ`の`contentPathRule`を設定します。

```xml
<!-- ディレクトリベースでJSPを切り替える場合 -->
<component name="resourcePathRule" class="nablarch.fw.web.i18n.DirectoryBasedResourcePathRule" />

<component class="nablarch.fw.web.handler.HttpResponseHandler">
  <property name="contentPathRule" ref="resourcePathRule" />
</component>
```

ディレクトリ構成例（`ja/`と`en/`配下に同名JSPを配置）:
```
コンテキストルート
├─en/management/user/search.jsp
└─ja/management/user/search.jsp
```

**注意点**: ウェブアプリにおいて、メッセージタグ（`<n:message>`）を使った多言語化はレイアウト崩れの可能性があります。レイアウト崩れを許容できない場合は「言語ごとにリソースのパスを切り替える」方式を使用してください。