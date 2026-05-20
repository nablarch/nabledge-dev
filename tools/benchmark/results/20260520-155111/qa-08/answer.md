**結論**: Nablarchの多言語化は、**メッセージ管理**（`PropertiesStringResourceLoader`）で言語別プロパティファイルを用意し、**スレッドコンテキスト**（`ThreadContextHandler`）で現在の言語を管理することで実現します。JSPのコンテンツ（テンプレート）を言語別に切り替えたい場合は、`HttpResponseHandler`の`contentPathRule`を使用します。

**根拠**:

### 1. メッセージ（エラーメッセージ・ラベル）の多言語化

言語ごとにプロパティファイルを作成します。

```none
main/resources/messages.properties       # デフォルト（日本語等）
               messages_en.properties    # 英語
               messages_zh.properties    # 中国語
```

コンポーネント設定ファイルで `PropertiesStringResourceLoader` にサポート言語を設定します。

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
      <!-- デフォルトの言語（必ず設定すること） -->
      <property name="defaultLocale" value="ja" />
    </component>
  </property>
</component>
```

> **重要**: `defaultLocale` は必ず明示的に設定してください。未設定の場合、`Locale.getDefault()` が使われ、実行環境によって値が変わり障害の原因になります。

メッセージ取得時の言語は `ThreadContext#getLanguage()` の値で決まります。

### 2. スレッドコンテキストへの言語設定

`ThreadContextHandler` で `LanguageAttribute` を設定します。

```xml
<component class="nablarch.common.handler.threadcontext.ThreadContextHandler">
  <property name="attributes">
    <list>
      <!-- 言語 -->
      <component class="nablarch.common.handler.threadcontext.LanguageAttribute">
        <property name="defaultLanguage" value="ja" />
      </component>
    </list>
  </property>
</component>
```

### 3. ユーザが言語を選択する画面の実装

クッキーに言語を保持する場合は `LanguageAttributeInHttpCookie` を使います。

```xml
<component name="languageAttribute"
           class="nablarch.common.web.handler.threadcontext.LanguageAttributeInHttpCookie">
  <property name="defaultLanguage" value="ja" />
  <property name="supportedLanguages" value="ja,en" />
</component>
```

ユーザが選択した言語をクッキーに保存するハンドラ実装例：

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

JSP（言語切り替えリンクの例）：

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

### 4. JSPファイル自体を言語別に切り替える場合

`HttpResponseHandler` の `contentPathRule` に `DirectoryBasedResourcePathRule` または `FilenameBasedResourcePathRule` を設定します。

```xml
<component name="resourcePathRule"
           class="nablarch.fw.web.i18n.DirectoryBasedResourcePathRule" />

<component class="nablarch.fw.web.handler.HttpResponseHandler">
  <property name="contentPathRule" ref="resourcePathRule" />
</component>
```

### 5. コードの名称（プルダウン等）の多言語化

コード名称テーブルに言語ごとのデータを追加します。

| ID | VALUE | LANG | NAME |
|---|---|---|---|
| GENDER | MALE | ja | 男性 |
| GENDER | MALE | en | Male |

**注意点**:
- カスタムタグライブラリ（JSP用）のコード表示では、言語指定による直接的な値の取得はできません。スレッドコンテキストの言語が自動的に使われます。
- テンプレートエンジン（Thymeleaf等）の `customResponseWriter` を使用する場合、`contentPathRule` による JSP の言語別切り替えは利用できません。テンプレートエンジン側の多言語対応機能を使用してください。

参照: `component/libraries/libraries-message.json:s8`, `component/handlers/handlers-thread-context-handler.json:s4`, `component/handlers/handlers-thread-context-handler.json:s7`, `component/handlers/handlers-http-response-handler.json:s7`, `component/libraries/libraries-code.json:s8`