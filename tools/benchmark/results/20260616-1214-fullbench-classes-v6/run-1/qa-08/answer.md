**結論**: メッセージ・ラベルの多言語化は、`PropertiesStringResourceLoader` に言語ごとのプロパティファイルを設定し、`ThreadContextHandler` で言語を管理することで実現できます。

**根拠**:

#### 1. 言語ごとのプロパティファイルを用意する

`classpath:messages.properties`（デフォルト言語）と `messages_en.properties`（英語）のように、言語ごとのファイルを作成します（Nablarch 6 は UTF-8 で記述可）。

```
main/resources/messages.properties       # デフォルト言語（例: 日本語）
               messages_en.properties    # 英語
```

#### 2. PropertiesStringResourceLoader にサポート言語を設定する

コンポーネント設定ファイルで `locales`（サポート言語）と `defaultLocale`（デフォルト言語）を指定します。

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

> **重要**: `defaultLocale` を設定しないと OS の言語設定が使われ、環境依存の障害が発生します。必ず設定してください。

#### 3. ThreadContextHandler に LanguageAttribute を設定する

`ThreadContextHandler` の `attributes` に言語属性クラスを追加します。Cookie に保持する場合は `LanguageAttributeInHttpCookie`、セッションに保持する場合は `LanguageAttributeInHttpSession` を使用します。

```xml
<component name="languageAttribute"
           class="nablarch.common.web.handler.threadcontext.LanguageAttributeInHttpCookie">
  <property name="defaultLanguage" value="ja" />
  <property name="supportedLanguages" value="ja,en" />
</component>
```

#### 4. ユーザが言語を選択できる画面を作る

ユーザの言語選択を保持するには、カスタムハンドラで `LanguageAttributeInHttpUtil.keepLanguage()` を呼び出します。

```java
public class I18nHandler implements HttpRequestHandler {
    public HttpResponse handle(HttpRequest request, ExecutionContext context) {
        String language = getLanguage(request, "user.language");
        if (StringUtil.hasValue(language)) {
            LanguageAttributeInHttpUtil.keepLanguage(request, context, language);
        }
        return context.handleNext(request);
    }
    private String getLanguage(HttpRequest request, String paramName) {
        if (!request.getParamMap().containsKey(paramName)) return null;
        return request.getParam(paramName)[0];
    }
}
```

JSP では `n:submitLink` + `n:param` でリンクに言語パラメータを付与します。

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

#### 5. JSP 自体を言語ごとに切り替える場合（オプション）

`HttpResponseHandler` の `contentPathRule` に `DirectoryBasedResourcePathRule`（ディレクトリで切り替え）または `FilenameBasedResourcePathRule`（ファイル名サフィックスで切り替え）を設定することで、フォワード先のJSPを言語ごとに切り替えることができます。

```xml
<component name="resourcePathRule" class="nablarch.fw.web.i18n.DirectoryBasedResourcePathRule" />

<component class="nablarch.fw.web.handler.HttpResponseHandler">
  <property name="contentPathRule" ref="resourcePathRule" />
</component>
```

この場合、JSPを言語別ディレクトリに配置します：
```
コンテキストルート
├─en
│  └─management/user/search.jsp
└─ja
   └─management/user/search.jsp
```

**注意点**:
- `messages.properties`（デフォルト言語ファイル）が存在しない場合はエラーになります。
- JSPコンテンツパスの切り替えは、Thymeleaf等のカスタムレスポンスライターを使用している場合は利用できません（テンプレートエンジン側の多言語機能を使用してください）。
- メッセージタグ（`<n:message>`）での国際化対応は、画面レイアウトが崩れる可能性があるため、許容できる場合のみ使用してください。

参照: libraries-message.json:s8, handlers-thread-context-handler.json:s7, handlers-http-response-handler.json:s7, handlers-thread-context-handler.json:s4

---

Step 6 でベリファイします。

**クレーム抽出**:
1. `PropertiesStringResourceLoader` に `locales` と `defaultLocale` を設定する → s8 に明示されている ✅
2. `defaultLocale` を設定しないと OS の言語設定が使われ障害の原因になる → s8 に明示されている ✅
3. ファイル名は `messages_言語.properties` → s8 に明示されている ✅
4. `LanguageAttributeInHttpCookie` / `LanguageAttributeInHttpSession` を使用 → s4, s7 に明示されている ✅
5. `LanguageAttributeInHttpUtil.keepLanguage()` → s7 に明示されている ✅
6. `DirectoryBasedResourcePathRule` / `FilenameBasedResourcePathRule` → s7（http-response-handler）に明示されている ✅
7. メッセージタグで画面レイアウトが崩れる可能性 → web-application-feature-details.json:s12 に明示されている ✅
8. Thymeleaf 等のカスタムレスポンスライター使用時は JSP コンテンツパス切り替えは使えない → handlers-http-response-handler.json:s7 に明示されている ✅

`verify_result = PASS`

---