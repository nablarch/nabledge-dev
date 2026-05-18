**結論**: Nablarch 6 でメッセージ・ラベルを多言語化するには、(1) 言語別プロパティファイルと `PropertiesStringResourceLoader`、(2) `ThreadContextHandler` による言語のスレッドコンテキスト管理、の 2 つを組み合わせて実装します。ユーザーによる言語切り替えには `LanguageAttributeInHttpCookie` / `LanguageAttributeInHttpSession` と `LanguageAttributeInHttpUtil` を使います。

**根拠**:

### 1. 言語別プロパティファイルの準備

`messages.properties`（デフォルト言語）と、各言語用の `messages_<言語コード>.properties` を作成します。

```
src/main/resources/messages.properties        # デフォルト（例: 日本語）
                   messages_en.properties     # 英語
                   messages_zh.properties     # 中国語
```

### 2. `PropertiesStringResourceLoader` の設定

コンポーネント設定ファイルで、サポート言語とデフォルト言語を指定します。

```xml
<component class="nablarch.core.cache.BasicStaticDataCache" name="messageCache">
  <property name="loader">
    <component class="nablarch.core.message.PropertiesStringResourceLoader">
      <property name="locales">
        <list>
          <value>en</value>
          <value>zh</value>
        </list>
      </property>
      <property name="defaultLocale" value="ja" />
    </component>
  </property>
</component>

<component name="stringResourceHolder" class="nablarch.core.message.StringResourceHolder">
  <property name="stringResourceCache" ref="messageCache" />
</component>
```

重要: `defaultLocale` を必ず設定すること。未設定の場合は `Locale.getDefault().getLanguage()` が使用され、実行環境の OS 設定によって値が変わるため障害の原因になります。

メッセージ取得時に使われる言語は `ThreadContext#getLanguage` が返すロケールで決まります（取得できない場合は `Locale.getDefault()` が使われます）。

### 3. `ThreadContextHandler` で言語属性を初期化

```xml
<component class="nablarch.common.handler.threadcontext.ThreadContextHandler">
  <property name="attributes">
    <list>
      <component class="nablarch.common.handler.threadcontext.LanguageAttribute">
        <property name="defaultLanguage" value="ja" />
      </component>
    </list>
  </property>
</component>
```

### 4. ユーザーによる言語切り替え（Web アプリ）

設定:
```xml
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

ハンドラ（言語選択を保持）:
```java
public class I18nHandler implements HttpRequestHandler {
    public HttpResponse handle(HttpRequest request, ExecutionContext context) {
        String language = request.getParamMap().containsKey("user.language")
            ? request.getParam("user.language")[0] : null;
        if (StringUtil.hasValue(language)) {
            LanguageAttributeInHttpUtil.keepLanguage(request, context, language);
        }
        return context.handleNext(request);
    }
}
```

セッションに保持したい場合は `LanguageAttributeInHttpCookie` の代わりに `LanguageAttributeInHttpSession` を使います。

### 5. JSP コンテンツパスの言語切り替え

```xml
<component name="resourcePathRule"
           class="nablarch.fw.web.i18n.DirectoryBasedResourcePathRule" />

<component class="nablarch.fw.web.handler.HttpResponseHandler">
  <property name="contentPathRule" ref="resourcePathRule" />
</component>
```

**注意点**:
- `defaultLocale` を未設定にしないこと（OS 依存になり障害の原因になる）
- `messages.properties`（デフォルトのロケール用ファイル）が存在しない場合はエラーで終了する
- サポート言語一覧に指定していない言語が渡された場合、クッキー・スレッドコンテキストへの設定は行われない
- Thymeleaf 等カスタムレスポンスライターを使用している場合、`HttpResponseHandler` のコンテンツパス切り替え機能は使用できないため、テンプレートエンジン側の多言語対応機能を使うこと

参照: component/libraries/libraries-message.json#s8 / component/handlers/handlers-thread-context-handler.json#s4 / component/handlers/handlers-thread-context-handler.json#s7 / component/handlers/handlers-http-response-handler.json#s7 / component/libraries/libraries-tag.json#s32