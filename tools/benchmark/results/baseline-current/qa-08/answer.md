**結論**: Nablarch 6 の多言語化は、①メッセージの多言語化、②言語選択 UI の実装、③コード名称の多言語化の3つを組み合わせることで実現できます。

## 1. メッセージの多言語化

言語ごとのプロパティファイルを用意し、`PropertiesStringResourceLoader` にサポート言語を設定します。

**コンポーネント設定 (component-config.xml)**:
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
      <!-- デフォルトの言語（必ず明示設定） -->
      <property name="defaultLocale" value="ja" />
    </component>
  </property>
</component>
```

**プロパティファイル構成**:
```
main/resources/messages.properties       # デフォルト（日本語）
               messages_en.properties    # 英語
```

**JSP での使用**（`n:message` タグ）:
```jsp
<n:message messageId="label.submit" />

<!-- 特定のメッセージだけ言語を指定したい場合 -->
<n:message messageId="label.submit" language="ja" />
```

## 2. 言語選択 UI の実装（ユーザが切り替えるボタン/リンク）

`LanguageAttributeInHttpCookie` または `LanguageAttributeInHttpSession` と `LanguageAttributeInHttpUtil` を組み合わせます。

**コンポーネント設定**:
```xml
<!-- コンポーネント名は "languageAttribute" 固定 -->
<component name="languageAttribute"
           class="nablarch.common.web.handler.threadcontext.LanguageAttributeInHttpCookie">
  <property name="defaultLanguage" value="ja" />
  <property name="supportedLanguages" value="ja,en" />
</component>
```

**JSP**（言語切り替えリンク）:
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

**ハンドラ（言語をクッキー＋スレッドコンテキストに保存）**:
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

## 3. JSP ファイル自体を言語で切り替える

`HttpResponseHandler` の `contentPathRule` にディレクトリまたはファイル名ベースのルールを設定します。

```xml
<component name="resourcePathRule"
           class="nablarch.fw.web.i18n.DirectoryBasedResourcePathRule" />

<component class="nablarch.fw.web.handler.HttpResponseHandler">
  <property name="contentPathRule" ref="resourcePathRule" />
</component>
```

## 4. コード名称の多言語化

コード名称テーブルに `LANG` カラムで言語別データを登録し、`CodeUtil` で取得します。

```java
CodeUtil.getName("GENDER", "MALE", Locale.JAPANESE);  // -> 男性
CodeUtil.getName("GENDER", "MALE", Locale.ENGLISH);   // -> Male
```

**注意点**:
- `defaultLocale` は必ず明示設定すること。未設定の場合 `Locale.getDefault().getLanguage()` が使われ、実行環境の OS 設定に依存するため障害の原因になる
- `messages.properties`（デフォルト言語用）が存在しない場合、起動時にエラーとなる
- JSP カスタムタグライブラリ（コード値表示タグ）は言語指定による値取得ができないため、Javaコードで `CodeUtil` を使うこと
- カスタムレスポンスライターを使用する場合、`contentPathRule` による JSP 切り替え機能は使用不可

参照: `component/libraries/libraries-message.json#s8`, `component/handlers/handlers-thread-context-handler.json#s7`, `component/libraries/libraries-code.json#s8`, `component/handlers/handlers-http-response-handler.json#s7`, `component/libraries/libraries-tag.json#s31`