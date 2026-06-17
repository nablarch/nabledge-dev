**結論**: Nablarchの多言語化は、①言語別プロパティファイル + `PropertiesStringResourceLoader` の設定、②`ThreadContextHandler` への `LanguageAttribute` 設定、③（ウェブの場合）ユーザの言語選択ハンドラの3つで実現します。

**根拠**:

**1. メッセージの多言語化（プロパティファイル）**

言語ごとにプロパティファイルを作成します。ファイル名は `messages_言語.properties` とします。デフォルト言語のファイル（`messages.properties`）は必須です。

```none
main/resources/messages.properties       # デフォルト言語（例: ja）
               messages_en.properties    # 英語
               messages_zh.properties    # 中国語
```

コンポーネント設定で `PropertiesStringResourceLoader` にサポート言語とデフォルト言語を設定します：

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
      <!-- デフォルト言語（必ず明示設定すること） -->
      <property name="defaultLocale" value="ja" />
    </component>
  </property>
</component>

<component name="stringResourceHolder" class="nablarch.core.message.StringResourceHolder">
  <property name="stringResourceCache" ref="messageCache" />
</component>
```

**2. 言語の決定（ThreadContext）**

メッセージ取得時に使用される言語は `ThreadContext#getLanguage` が返すロケールで決まります。`ThreadContextHandler` の `attributes` に `LanguageAttribute`（または Web 用の `LanguageAttributeInHttpCookie` / `LanguageAttributeInHttpSession`）を設定します：

```xml
<component class="nablarch.common.handler.threadcontext.ThreadContextHandler">
  <property name="attributes">
    <list>
      <!-- 言語（固定のデフォルト言語を使う場合） -->
      <component class="nablarch.common.handler.threadcontext.LanguageAttribute">
        <property name="defaultLanguage" value="ja" />
      </component>
    </list>
  </property>
</component>
```

**3. ユーザが言語を切り替えられる画面（ウェブアプリ）**

クッキーに言語を保持し、リンクで切り替えさせる実装例です。

コンポーネント設定（コンポーネント名を `"languageAttribute"` にする必要があります）：

```xml
<component name="languageAttribute"
           class="nablarch.common.web.handler.threadcontext.LanguageAttributeInHttpCookie">
  <property name="defaultLanguage" value="ja" />
  <property name="supportedLanguages" value="ja,en" />
</component>
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

ハンドラ（言語を保持・ThreadContextに設定）：

```java
public class I18nHandler implements HttpRequestHandler {
    public HttpResponse handle(HttpRequest request, ExecutionContext context) {
        String language = getLanguage(request, "user.language");
        if (StringUtil.hasValue(language)) {
            // クッキーとスレッドコンテキストに言語を設定する
            // サポート対象外の言語が指定された場合は何もしない
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

**4. JSP自体も言語で切り替える場合**

`HttpResponseHandler` の `contentPathRule` プロパティに `DirectoryBasedResourcePathRule`（言語別ディレクトリ）または `FilenameBasedResourcePathRule`（`search_en.jsp` のようにファイル名サフィックス）を設定します：

```xml
<component name="resourcePathRule" class="nablarch.fw.web.i18n.DirectoryBasedResourcePathRule" />

<component class="nablarch.fw.web.handler.HttpResponseHandler">
  <property name="contentPathRule" ref="resourcePathRule" />
</component>
```

**注意点**:
- `PropertiesStringResourceLoader.defaultLocale` は必ず明示的に設定してください。未設定だと OS の設定に依存し、環境によって動作が変わります。
- `LanguageAttributeInHttpUtil` を使う場合、コンポーネント名は必ず `"languageAttribute"` にしてください。
- JSP のコンテンツパス切り替えは、カスタムレスポンスライター（テンプレートエンジン等）を使用している場合は利用できません。

参照: component/libraries/libraries-message.json:s8, component/handlers/handlers-thread-context-handler.json:s4, component/handlers/handlers-thread-context-handler.json:s7, component/handlers/handlers-http-response-handler.json:s7