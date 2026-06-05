Step 5-7: 回答生成と検証を行います。

Javadocセクションは内容が空（メソッド/フィールドヘッダのみ）のため、メインのコンテンツセクションで回答を生成します。

---

**結論**: Nablarchの多言語化は、①言語別メッセージプロパティファイル + `PropertiesStringResourceLoader` の設定、②スレッドコンテキストハンドラによる言語切り替えUI、③必要に応じてコード名称テーブルの言語別データを組み合わせて実装する。

---

**根拠**:

### 1. メッセージの多言語化（言語別プロパティファイル）

言語ごとのプロパティファイルを用意し、`PropertiesStringResourceLoader` にサポート言語を設定する。

**ファイル構成**:
```
main/resources/messages.properties       # デフォルト言語（例: ja）
               messages_en.properties    # 英語
               messages_zh.properties    # 中国語
```

**コンポーネント定義（XML）**:
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

> **注意**: `defaultLocale` を設定しないと `Locale.getDefault().getLanguage()` が使用されOSの設定によって変化するため、必ず明示的に設定すること。

**JSPでの使用**（`n:message` タグ）:
```jsp
<!-- スレッドコンテキストの言語でメッセージを出力 -->
<n:message messageId="label.search" />

<!-- 言語を明示的に指定する場合 -->
<n:message messageId="label.search" language="ja" />
```

---

### 2. 言語切り替えUIの実装

`LanguageAttributeInHttpCookie`（クッキー保持）または `LanguageAttributeInHttpSession`（セッション保持）を使い、ユーザが言語を選択できる仕組みを作る。

**コンポーネント定義**:
```xml
<!-- コンポーネント名を "languageAttribute" にすること -->
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

**ハンドラ実装**:
```java
public class I18nHandler implements HttpRequestHandler {
    public HttpResponse handle(HttpRequest request, ExecutionContext context) {
        String language = ...; // リクエストパラメータ "user.language" を取得
        if (StringUtil.hasValue(language)) {
            // クッキーとスレッドコンテキストに言語を設定する
            // サポート対象外の言語は無視される
            LanguageAttributeInHttpUtil.keepLanguage(request, context, language);
        }
        return context.handleNext(request);
    }
}
```

---

### 3. JSPファイルの言語別切り替え（HTTPレスポンスハンドラ）

言語によってフォワード先のJSPファイルを切り替えたい場合、`HttpResponseHandler` の `contentPathRule` に以下いずれかを設定する。

| クラス | ファイル構成 |
|---|---|
| `DirectoryBasedResourcePathRule` | コンテキストルート直下に `ja/`, `en/` ディレクトリを作成 |
| `FilenameBasedResourcePathRule` | `search_ja.jsp`, `search_en.jsp` のようなサフィックスを付与 |

```xml
<component name="resourcePathRule"
           class="nablarch.fw.web.i18n.DirectoryBasedResourcePathRule" />

<component class="nablarch.fw.web.handler.HttpResponseHandler">
  <property name="contentPathRule" ref="resourcePathRule" />
</component>
```

`a`, `img`, `link`, `script`, `include` などのカスタムタグも同じ `ResourcePathRule` を使って言語別のリソースパスに自動切り替えされる。

---

### 4. コード名称（ラベル）の多言語化

コード名称テーブルに言語別データを登録し、`CodeUtil` で言語を指定して取得する。

**テーブルデータ例**（LANG列で言語を区別）:

| ID | VALUE | LANG | NAME |
|---|---|---|---|
| GENDER | MALE | ja | 男性 |
| GENDER | MALE | en | Male |

**コード取得**:
```java
CodeUtil.getName("GENDER", "MALE", Locale.JAPANESE); // -> 男性
CodeUtil.getName("GENDER", "MALE", Locale.ENGLISH);  // -> Male
```

> **注意**: JSP用カスタムタグライブラリでは言語指定によるコード値取得はできない。`CodeUtil` をJavaコードから呼び出すこと。

---

**注意点**:
- `defaultLocale` は必ず明示的に設定すること（OS依存になると障害の原因になる）
- カスタムレスポンスライターを使用している場合、`contentPathRule` による言語別JSP切り替えは使用できない
- JSPカスタムタグによるコード値表示は言語指定に対応していないため、言語別にコード名称を表示するには `CodeUtil` を直接使用すること

参照: `libraries-message.json:s8`, `libraries-code.json:s8`, `handlers-thread-context-handler.json:s7`, `handlers-http-response-handler.json:s7`, `libraries-tag.json:s31`, `libraries-tag.json:s32`

---