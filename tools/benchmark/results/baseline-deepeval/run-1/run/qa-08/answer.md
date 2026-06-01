**結論**: Nablarchの多言語化は、①メッセージのプロパティファイル多言語化、②コード名称テーブルの多言語化、③ユーザーの言語選択の実装、の3つを組み合わせて実現する。JSP表示には「メッセージタグ方式」と「リソースパス切り替え方式」の2通りがあるが、レイアウト崩れが許容できない場合はリソースパス切り替え方式を使うこと。

---

**根拠**:

### 1. メッセージの多言語化

言語ごとのプロパティファイルを作成し、`PropertiesStringResourceLoader` に設定する。

**プロパティファイルの構成**:
```none
main/resources/messages.properties       # デフォルトの言語に対応したファイル
               messages_en.properties    # enに対応したファイル
               messages_zh.properties    # zhに対応したファイル
```

**コンポーネント定義**:
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
      <!-- デフォルトの言語 -->
      <property name="defaultLocale" value="ja" />
    </component>
  </property>
</component>
```

メッセージ取得時の言語は `ThreadContext#getLanguage` の値で決まる。

**JSPでの表示（メッセージタグ方式）**:
```jsp
<n:message messageId="page.not.found" />

<!-- 特定箇所だけ言語を指定したい場合 -->
<n:message messageId="page.not.found" language="ja" />
```

---

### 2. コード名称の多言語化

コード名称テーブルに言語ごとのデータを追加する。

| ID | VALUE | LANG | NAME | SHORT_NAME |
|----|-------|------|------|------------|
| GENDER | MALE | ja | 男性 | 男 |
| GENDER | MALE | en | Male | M |

Javaコードからは `CodeUtil` で言語を指定して取得できる:
```java
CodeUtil.getName("GENDER", "MALE", Locale.JAPANESE);  // -> 男性
CodeUtil.getName("GENDER", "MALE", Locale.ENGLISH);   // -> Male
```

---

### 3. ユーザーの言語選択

`LanguageAttributeInHttpCookie`（またはSession版）とハンドラで実現する。

**コンポーネント定義**:
```xml
<component name="languageAttribute"
           class="nablarch.common.web.handler.threadcontext.LanguageAttributeInHttpCookie">
  <property name="defaultLanguage" value="ja" />
  <property name="supportedLanguages" value="ja,en" />
</component>
```

**JSPの言語切り替えリンク**:
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

**ハンドラ実装**:
```java
public class I18nHandler implements HttpRequestHandler {
    public HttpResponse handle(HttpRequest request, ExecutionContext context) {
        String language = ...; // user.language パラメータ取得
        if (StringUtil.hasValue(language)) {
            LanguageAttributeInHttpUtil.keepLanguage(request, context, language);
        }
        return context.handleNext(request);
    }
}
```

---

### 4. JSPファイル自体を言語ごとに切り替える場合（リソースパス切り替え方式）

`HttpResponseHandler` の `contentPathRule` に以下いずれかを設定する:

| クラス | 方式 |
|--------|------|
| `DirectoryBasedResourcePathRule` | コンテキストルート直下に `ja/`・`en/` ディレクトリを作成 |
| `FilenameBasedResourcePathRule` | ファイル名に `_ja`・`_en` サフィックスを付ける |

```xml
<component name="resourcePathRule" class="nablarch.fw.web.i18n.DirectoryBasedResourcePathRule" />
<component class="nablarch.fw.web.handler.HttpResponseHandler">
  <property name="contentPathRule" ref="resourcePathRule" />
</component>
```

---

**注意点**:
- `PropertiesStringResourceLoader.defaultLocale` は**必ず明示設定**すること。未設定の場合は `Locale.getDefault().getLanguage()` が使われ、実行環境のOSによって値が変わり障害の原因になる
- JSPカスタムタグ（コード名称の表示用）では言語指定による値取得ができない。ThreadContextに設定された言語が使われる
- メッセージタグ方式（`<n:message>`）は画面レイアウトが崩れる可能性があるため、崩れが許容できない場合はリソースパス切り替え方式を使うこと

参照: `libraries-message.json:s8`, `libraries-message.json:s7`, `libraries-code.json:s8`, `handlers-thread-context-handler.json:s7`, `handlers-http-response-handler.json:s7`, `web-application-feature-details.json:s12`, `libraries-tag.json:s31`

---