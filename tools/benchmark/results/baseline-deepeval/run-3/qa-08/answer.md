十分な情報が取得できました。回答を生成します。

---

**結論**: Nablarchのメッセージ多言語化は、言語ごとの `messages_言語.properties` ファイルを用意し、`PropertiesStringResourceLoader` にサポート言語を設定することで実現できます。ユーザーの言語切り替えは `LanguageAttributeInHttpCookie`（または `LanguageAttributeInHttpSession`）と `LanguageAttributeInHttpUtil` を組み合わせて実装します。

---

**根拠**:

### 1. 言語ごとのプロパティファイルを用意する

デフォルト言語用 `messages.properties` と、追加言語用 `messages_言語.properties` を作成します。

```
main/resources/messages.properties       # デフォルト言語（例: ja）
               messages_en.properties    # 英語
```

### 2. コンポーネント定義に多言語設定を追加する

`PropertiesStringResourceLoader` にサポート言語と **デフォルト言語** を明示的に設定します。

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
      <!-- デフォルトの言語（必ず明示すること） -->
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

### 3. ユーザーが言語を切り替えられるようにする（Webアプリの場合）

`LanguageAttributeInHttpCookie` でクッキーに言語を保持し、`LanguageAttributeInHttpUtil.keepLanguage()` でスレッドコンテキストに反映させます。

**コンポーネント定義**:
```xml
<component name="languageAttribute"
           class="nablarch.common.web.handler.threadcontext.LanguageAttributeInHttpCookie">
  <property name="defaultLanguage" value="ja" />
  <property name="supportedLanguages" value="ja,en" />
</component>
```

**ハンドラ実装例**:
```java
public class I18nHandler implements HttpRequestHandler {

    public HttpResponse handle(HttpRequest request, ExecutionContext context) {
        String language = getLanguage(request, "user.language");
        if (StringUtil.hasValue(language)) {
            // クッキーとスレッドコンテキストに選択言語を設定
            // サポート対象外の言語は無視される
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

**JSPで言語切り替えリンクを出力する例**:
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

### 4. コード名称（プルダウンラベル等）の多言語化

コード管理機能を使っている場合、コード名称テーブルに言語（LANG列）ごとのデータを準備し、`CodeUtil.getName()` で言語指定取得できます。

```java
CodeUtil.getName("GENDER", "MALE", Locale.JAPANESE);  // -> 男性
CodeUtil.getName("GENDER", "MALE", Locale.ENGLISH);   // -> Male
```

---

**注意点**:
- `PropertiesStringResourceLoader.defaultLocale` を**必ず明示設定**すること。未設定の場合は `Locale.getDefault().getLanguage()` が使われ、実行環境のOS設定に依存して障害の原因になる。
- `messages.properties`（デフォルト言語用）が存在しない場合はエラーになる。必ず作成すること。
- メッセージ取得時の言語は `ThreadContext#getLanguage` が返すロケールで決定される。ロケールが取得できない場合は `Locale.getDefault()` が使われる。
- JSP用のカスタムタグライブラリ（コード値表示）では言語指定取得はできない点に注意。

参照: libraries-message.json:s8, handlers-thread-context-handler.json:s7, libraries-code.json:s8

---