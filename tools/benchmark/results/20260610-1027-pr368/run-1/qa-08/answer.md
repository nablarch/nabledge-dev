**結論**: Nablarchでの多言語化は、言語ごとのプロパティファイルを用意して `PropertiesStringResourceLoader` にサポート言語を設定し、`ThreadContextHandler` の言語属性（`LanguageAttributeInHttpCookie` や `LanguageAttributeInHttpSession`）でリクエストごとの言語を管理する2段構えの仕組みで実現します。

**根拠**:

### 1. 言語ごとのプロパティファイルを用意する

ファイル名は `messages_言語.properties` とします。デフォルト言語は言語なしの `messages.properties`（必須）とします。

```
main/resources/messages.properties       # デフォルト言語（例: ja）
               messages_en.properties    # 英語
               messages_zh.properties    # 中国語
               messages_de.properties    # ドイツ語
```

### 2. PropertiesStringResourceLoader にサポート言語を設定する

コンポーネント設定ファイル（XML）に以下を追加します。`defaultLocale` は **必ず明示設定**してください（設定しない場合、OSの設定に依存して障害の原因になります）。

```xml
<component class="nablarch.core.cache.BasicStaticDataCache" name="messageCache">
  <property name="loader">
    <component class="nablarch.core.message.PropertiesStringResourceLoader">
      <!-- サポートする言語 -->
      <property name="locales">
        <list>
          <value>en</value>
          <value>zh</value>
          <value>de</value>
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

### 3. ThreadContextHandler で言語を管理する

メッセージ取得時の言語は `ThreadContext#getLanguage` が返すロケールで決まります。ユーザが言語を選択できるようにするには、`LanguageAttributeInHttpCookie`（Cookie保持）または `LanguageAttributeInHttpSession`（セッション保持）を使います。

**コンポーネント設定（Cookie使用の例）**:

```xml
<!-- コンポーネント名を"languageAttribute"にする（LanguageAttributeInHttpUtil使用のため） -->
<component name="languageAttribute"
           class="nablarch.common.web.handler.threadcontext.LanguageAttributeInHttpCookie">
  <property name="defaultLanguage" value="ja" />
  <property name="supportedLanguages" value="ja,en" />
</component>
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

**言語を保持するハンドラの実装例**:

```java
public class I18nHandler implements HttpRequestHandler {

    public HttpResponse handle(HttpRequest request, ExecutionContext context) {
        String language = getLanguage(request, "user.language");
        if (StringUtil.hasValue(language)) {
            // CookieとスレッドコンテキストへのLanguageを設定する
            // 指定言語がサポート対象外の場合は設定しない
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

**注意点**:
- `defaultLocale` は必ず明示的に設定すること。未設定の場合は `Locale.getDefault().getLanguage()` が使われ、実行環境のOS設定によって変化するため障害の原因になる。
- `messages.properties`（デフォルト言語用）が存在しない場合はエラーになる。
- `LanguageAttributeInHttpUtil.keepLanguage` は、指定した言語が `supportedLanguages` に含まれない場合は Cookie・スレッドコンテキストへの設定を行わない。
- ステートレスWebアプリ構成の場合は `LanguageAttributeInHttpSession` ではなく `LanguageAttributeInHttpCookie` を使うこと（`LanguageAttributeInHttpSession` は HTTP セッション依存のため）。

参照: libraries-message.json:s8, handlers-thread-context-handler.json:s7, handlers-thread-context-handler.json:s4