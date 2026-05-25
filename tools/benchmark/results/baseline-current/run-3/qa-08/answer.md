**結論**: Nablarch 6 の多言語化は、①メッセージの多言語化、②コード名称の多言語化、③JSPリソースパスの切り替え、の3つのアプローチを組み合わせて実現します。ユーザーが言語を動的に切り替えるには `LanguageAttributeInHttpCookie` / `LanguageAttributeInHttpSession` を使用します。

**根拠**:

### 1. メッセージの多言語化（バリデーションエラー文言・ラベル等）

プロパティファイルの準備:
```
main/resources/messages.properties       # デフォルト言語（例：ja）
               messages_en.properties    # 英語
               messages_zh.properties    # 中国語
```

コンポーネント設定:
```xml
<component class="nablarch.core.message.PropertiesStringResourceLoader">
  <property name="locales">
    <list>
      <value>en</value>
      <value>zh</value>
    </list>
  </property>
  <!-- デフォルト言語は必ず明示すること（OS設定依存を防ぐ） -->
  <property name="defaultLocale" value="ja" />
</component>
```

メッセージ取得時の言語は `ThreadContext#getLanguage` が返すロケールで決定されます。

### 2. ユーザーによる言語切り替え（動的切り替え）

コンポーネント設定（クッキーに言語を保持する例）:
```xml
<component name="languageAttribute"
           class="nablarch.common.web.handler.threadcontext.LanguageAttributeInHttpCookie">
  <property name="defaultLanguage" value="ja" />
  <property name="supportedLanguages" value="ja,en" />
</component>
```

JSP実装例（言語切り替えリンク）:
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

ハンドラ実装例:
```java
public class I18nHandler implements HttpRequestHandler {
    public HttpResponse handle(HttpRequest request, ExecutionContext context) {
        String language = getLanguage(request, "user.language");
        if (StringUtil.hasValue(language)) {
            LanguageAttributeInHttpUtil.keepLanguage(request, context, language);
        }
        return context.handleNext(request);
    }
}
```

セッションに保持したい場合は `LanguageAttributeInHttpSession` を使用します。

### 3. コード名称（プルダウン選択肢等）の多言語化

コード名称テーブルに言語ごとのデータを用意します。

```java
CodeUtil.getName("GENDER", "MALE", Locale.JAPANESE);  // -> 男性
CodeUtil.getName("GENDER", "MALE", Locale.ENGLISH);   // -> Male
```

### 4. JSPリソースパスの切り替え（言語別レイアウトファイル）

`a`タグ・`img`タグ・`link`タグ・`script`タグ・`include`タグ等のカスタムタグが、`ResourcePathRule` を使って言語ごとにリソースパスを動的に切り替えます。

注意: メッセージタグ（`<n:message>`）での国際化対応は画面レイアウトが崩れる可能性があるため、レイアウト崩れを許容できる場合のみ使用してください。

**注意点**:
- `PropertiesStringResourceLoader.defaultLocale` は必ず明示設定すること。未設定の場合 `Locale.getDefault().getLanguage()` が使われ、実行環境のOS設定次第で値が変わり障害の原因になります。
- JSPのカスタムタグライブラリでコード値を表示する場合、言語指定による値の取得はできません（`CodeUtil.getName()` を直接使う必要があります）。

参照: `component/libraries/libraries-message.json#s8`, `component/handlers/handlers-thread-context-handler.json#s7`, `component/libraries/libraries-tag.json#s32`, `processing-pattern/web-application/web-application-feature-details.json#s12`, `component/libraries/libraries-code.json#s8`