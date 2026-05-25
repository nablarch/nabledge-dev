回答を生成します（Step 5）。

---

**結論**: メッセージの多言語化は言語別プロパティファイル + `PropertiesStringResourceLoader` の設定で実現し、コード名称（ラベル）はコード名称テーブルのLANGカラムへデータを追加することで対応する。画面の文言切り替えには「メッセージタグ方式」と「リソースパス切り替え方式」の2通りがある。

---

**根拠**:

### 1. メッセージの多言語化

言語別のプロパティファイルを用意し、`PropertiesStringResourceLoader` にサポート言語とデフォルトロケールを設定する。

**コンポーネント設定**:
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
      <!-- デフォルトの言語（必ず明示設定すること） -->
      <property name="defaultLocale" value="ja" />
    </component>
  </property>
</component>
```

**プロパティファイルの配置**:
```
main/resources/messages.properties       # デフォルト（日本語）
               messages_en.properties    # 英語
```

`messages.properties` が存在しない場合はエラーになる。

---

### 2. 言語切り替えUI（ユーザが言語を選択できるようにする）

`LanguageAttributeInHttpCookie` と `LanguageAttributeInHttpUtil.keepLanguage` を使う。

**コンポーネント設定**:
```xml
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

**ハンドラ（言語の保持）**:
```java
public class I18nHandler implements HttpRequestHandler {
    public HttpResponse handle(HttpRequest request, ExecutionContext context) {
        String language = getLanguage(request, "user.language");
        if (StringUtil.hasValue(language)) {
            LanguageAttributeInHttpUtil.keepLanguage(request, context, language);
        }
        return context.handleNext(request);
    }
    // ...
}
```

---

### 3. 画面文言の切り替え方式（2択）

| 方式 | 方法 | 注意 |
|---|---|---|
| **メッセージタグ方式** | JSP内で `<n:message>` タグを使用 | レイアウト崩れの可能性あり |
| **リソースパス切り替え方式** | 言語別にJSPファイルを用意し、ハンドラで切り替え | レイアウト崩れなし（推奨） |

**メッセージタグ方式の例**:
```jsp
<n:message messageId="label.user.name" />
```

**リソースパス切り替え方式**（`DirectoryBasedResourcePathRule` 使用）:
```xml
<component name="resourcePathRule" class="nablarch.fw.web.i18n.DirectoryBasedResourcePathRule" />
<component class="nablarch.fw.web.handler.HttpResponseHandler">
  <property name="contentPathRule" ref="resourcePathRule" />
</component>
```
JSPをディレクトリで分ける:
```
コンテキストルート
├─en/management/user/search.jsp
└─ja/management/user/search.jsp
```

---

### 4. コード名称（ラベル）の多言語化

コード名称テーブルに言語ごとのデータを追加し、`CodeUtil.getName` にロケールを渡す。

**テーブルデータ例**:

| ID | VALUE | LANG | NAME | SHORT_NAME |
|---|---|---|---|---|
| GENDER | MALE | ja | 男性 | 男 |
| GENDER | MALE | en | Male | M |

**Java コード**:
```java
CodeUtil.getName("GENDER", "MALE", Locale.JAPANESE);  // -> 男性
CodeUtil.getName("GENDER", "MALE", Locale.ENGLISH);   // -> Male
```

---

**注意点**:
- `defaultLocale` は必ず明示設定すること。未設定の場合 `Locale.getDefault().getLanguage()` が使われ、OS環境依存になり障害の原因になる。
- メッセージタグ方式はレイアウト崩れが許容できる場合のみ使用すること。
- JSP用カスタムタグライブラリ（コード値表示）では言語指定による値の取得はできない。`CodeUtil` を使うこと。

参照: `libraries-message.json:s8`, `handlers-thread-context-handler.json:s7`, `handlers-http-response-handler.json:s7`, `libraries-code.json:s8`, `libraries-tag.json:s31`, `web-application-feature-details.json:s12`

---