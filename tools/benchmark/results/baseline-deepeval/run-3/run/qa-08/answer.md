**結論**: Nablarchの多言語化は、①メッセージプロパティファイルの言語別定義、②コード名称テーブルへの言語別データ投入、③ThreadContextHandlerによる言語管理の3要素を組み合わせて実装する。

---

**根拠**:

### 1. メッセージの多言語化（固定文言・エラーメッセージ）

言語ごとのプロパティファイルを作成し、`PropertiesStringResourceLoader` にサポート言語を設定する。

**プロパティファイルの配置**:
```none
main/resources/messages.properties       # デフォルト言語（必須）
               messages_en.properties    # 英語
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
        </list>
      </property>
      <!-- デフォルトの言語（必ず設定すること） -->
      <property name="defaultLocale" value="ja" />
    </component>
  </property>
</component>
```

> **注意**: `defaultLocale` を設定しない場合、OSの言語設定が使われ環境依存の障害になる。必ず明示的に設定すること。

**JSPでのメッセージ出力**:
```jsp
<!-- ユーザ選択言語でメッセージを表示 -->
<n:message messageId="label.user.register.title" />

<!-- 特定セクションのみ言語を固定したい場合 -->
<n:message messageId="label.user.register.title" language="ja" />
```

---

### 2. コード名称（選択肢ラベル）の多言語化

コード名称テーブルに言語ごとのデータを追加する。

**テーブルデータ例**:

| ID | VALUE | LANG | SORT_ORDER | NAME | SHORT_NAME |
|---|---|---|---|---|---|
| GENDER | MALE | ja | 1 | 男性 | 男 |
| GENDER | FEMALE | ja | 2 | 女性 | 女 |
| GENDER | MALE | en | 1 | Male | M |
| GENDER | FEMALE | en | 2 | Female | F |

**Javaでの取得**:
```java
CodeUtil.getName("GENDER", "MALE", Locale.JAPANESE);  // -> 男性
CodeUtil.getName("GENDER", "MALE", Locale.ENGLISH);   // -> Male
```

> **注意**: JSP用カスタムタグライブラリでは言語指定による値の取得ができない。`CodeUtil` をJavaコード側で使用すること。

---

### 3. 言語切り替えUIの実装（ウェブアプリケーション）

**ThreadContextHandlerの設定**（`LanguageAttributeInHttpCookie`を使用）:
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

**ハンドラ（選択言語をCookieに保持）**:
```java
public class I18nHandler implements HttpRequestHandler {
    public HttpResponse handle(HttpRequest request, ExecutionContext context) {
        String language = getLanguage(request, "user.language");
        if (StringUtil.hasValue(language)) {
            // Cookieとスレッドコンテキストに言語を設定する
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

---

### 4. JSPファイル自体を言語別に切り替える場合

`HttpResponseHandler` の `contentPathRule` に以下いずれかを設定する:

```xml
<!-- ディレクトリ方式: /ja/management/user/search.jsp, /en/management/user/search.jsp -->
<component name="resourcePathRule" class="nablarch.fw.web.i18n.DirectoryBasedResourcePathRule" />

<!-- ファイル名方式: search_ja.jsp, search_en.jsp -->
<!-- <component name="resourcePathRule" class="nablarch.fw.web.i18n.FilenameBasedResourcePathRule" /> -->

<component class="nablarch.fw.web.handler.HttpResponseHandler">
  <property name="contentPathRule" ref="resourcePathRule" />
</component>
```

**注意点**:
- `messages.properties`（デフォルト言語）が存在しない場合はエラーで終了するため、必ず作成すること
- `defaultLocale` を未設定にするとOS依存となり障害の原因になる
- JSPカスタムタグの `a`, `img`, `link`, `script` タグもリソースパスの言語切り替えに対応している（`ResourcePathRule`と連動）

参照: libraries-message.json:s8, libraries-code.json:s8, handlers-thread-context-handler.json:s7, handlers-http-response-handler.json:s7, libraries-tag.json:s31, libraries-tag.json:s32

---