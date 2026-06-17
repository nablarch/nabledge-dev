**結論**: Nablarchの多言語化は、①メッセージプロパティファイルの言語別作成、②コード名称テーブルへの言語別データ追加、③JSP表示方式の選択（メッセージタグ or リソースパス切り替え）の3つを組み合わせて実現します。言語の切り替えは `ThreadContextHandler` の言語属性設定が起点になります。

---

**根拠**:

### 1. メッセージの多言語化

**プロパティファイルを言語ごとに作成する**:

```
main/resources/messages.properties       # デフォルト言語（日本語）
               messages_en.properties    # 英語
```

**コンポーネント定義ファイルで `PropertiesStringResourceLoader` に言語を設定する**:

```xml
<component class="nablarch.core.cache.BasicStaticDataCache" name="messageCache">
  <property name="loader">
    <component class="nablarch.core.message.PropertiesStringResourceLoader">
      <!-- サポートする言語（デフォルト以外を列挙） -->
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
```

### 2. コード名称の多言語化

コード名称テーブルに言語ごとのデータ行を追加する（`LANG` カラムで区別）:

| ID | VALUE | LANG | NAME |
|---|---|---|---|
| GENDER | MALE | ja | 男性 |
| GENDER | MALE | en | Male |

Javaコードから言語を指定して取得する場合は `CodeUtil` を使用:

```java
CodeUtil.getName("GENDER", "MALE", Locale.JAPANESE);  // -> 男性
CodeUtil.getName("GENDER", "MALE", Locale.ENGLISH);   // -> Male
```

### 3. ThreadContextHandler で言語を設定する

ユーザが言語を切り替えられるようにするには `LanguageAttributeInHttpCookie` または `LanguageAttributeInHttpSession` を使用:

```xml
<!-- コンポーネント名を "languageAttribute" にする（LanguageAttributeInHttpUtil が参照） -->
<component name="languageAttribute"
           class="nablarch.common.web.handler.threadcontext.LanguageAttributeInHttpCookie">
  <property name="defaultLanguage" value="ja" />
  <property name="supportedLanguages" value="ja,en" />
</component>
```

言語選択リンクのJSP実装:

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

言語を保持するハンドラの実装:

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

### 4. JSP の文言切り替え方式（2択）

**方式A: `<n:message>` タグ**（1つのJSPで多言語対応）:

```jsp
<n:message messageId="label.user.name" />
```

**方式B: リソースパス切り替え**（言語ごとに別JSPファイル）:

```xml
<component name="resourcePathRule"
           class="nablarch.fw.web.i18n.DirectoryBasedResourcePathRule" />
<component class="nablarch.fw.web.handler.HttpResponseHandler">
  <property name="contentPathRule" ref="resourcePathRule" />
</component>
```

`DirectoryBasedResourcePathRule` を使うと、コンテキストルート直下にディレクトリ名で言語を切り替える（例: `/ja/management/search.jsp` / `/en/management/search.jsp`）。

---

**注意点**:
- `PropertiesStringResourceLoader.defaultLocale` は**必ず設定する**。未設定の場合、OS設定に依存した `Locale.getDefault()` が使われ、実行環境ごとに値が変化して障害の原因になる。
- JSPカスタムタグライブラリ（`<n:code>` 等）ではコード値の言語指定ができない。Javaコードから `CodeUtil` を使う場合のみ言語指定が可能。
- 方式Aの `<n:message>` タグはレイアウト崩れの可能性があるため、レイアウト崩れが許容できない場合は方式B（リソースパス切り替え）を使用する。

参照: libraries-message.json:s8, libraries-code.json:s8, handlers-thread-context-handler.json:s4, handlers-thread-context-handler.json:s7, handlers-http-response-handler.json:s7, libraries-tag.json:s31, libraries-tag.json:s32, web-application-feature-details.json:s12