Step 5〜7: 回答を生成し、検証します。

すべてのNablarch固有のクレームはセクション内容で裏付けられています（verify_result = PASS）。

---

**結論**: Nablarchの多言語化は、①メッセージの多言語化、②コード名称の多言語化、③言語切り替えハンドラの3つを組み合わせて実装します。

---

**根拠**:

### 1. メッセージの多言語化（`PropertiesStringResourceLoader`）

`PropertiesStringResourceLoader` の `locales` にサポート言語を設定し、言語ごとのプロパティファイルを用意します。

```xml
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
```

プロパティファイルの配置：

```none
main/resources/messages.properties       # デフォルト（日本語）
               messages_en.properties    # 英語
```

### 2. コード名称（ラベル）の多言語化

コード名称テーブルに言語ごとのデータを追加し、`CodeUtil` で `Locale` を指定して取得します。

テーブルデータ（LANG列に `ja` / `en` のデータを追加）：

| ID | VALUE | LANG | NAME |
|---|---|---|---|
| GENDER | MALE | ja | 男性 |
| GENDER | MALE | en | Male |

```java
CodeUtil.getName("GENDER", "MALE", Locale.JAPANESE);  // -> 男性
CodeUtil.getName("GENDER", "MALE", Locale.ENGLISH);   // -> Male
```

### 3. 言語切り替えの実装

クッキーに言語を保持する場合、`LanguageAttributeInHttpCookie` を設定し、`I18nHandler` で切り替えを処理します。

```xml
<component name="languageAttribute"
           class="nablarch.common.web.handler.threadcontext.LanguageAttributeInHttpCookie">
  <property name="defaultLanguage" value="ja" />
  <property name="supportedLanguages" value="ja,en" />
</component>
```

JSP（言語選択リンク）：

```jsp
<n:submitLink uri="/action/menu/index" name="switchToEnglish">
  英語
  <n:param paramName="user.language" value="en" />
</n:submitLink>
```

ハンドラ（`I18nHandler`）：

```java
LanguageAttributeInHttpUtil.keepLanguage(request, context, language);
```

### 4. JSPでのメッセージ表示方法（2種類）

**方法①：messageタグ**（1つのJSPで多言語対応）

```jsp
<n:message messageId="label.user.register.title" />
```

**方法②：言語ごとにJSPのパスを切り替える**（`DirectoryBasedResourcePathRule` または `FilenameBasedResourcePathRule`）

```xml
<component name="resourcePathRule"
           class="nablarch.fw.web.i18n.DirectoryBasedResourcePathRule" />

<component class="nablarch.fw.web.handler.HttpResponseHandler">
  <property name="contentPathRule" ref="resourcePathRule" />
</component>
```

---

**注意点**:
- `defaultLocale` は必ず明示的に設定すること。未設定の場合、OS設定に依存してしまい障害の原因になります（`libraries-message.json:s8`）
- messageタグを使う場合、言語によって文字幅が変わりレイアウトが崩れる可能性があります。崩れを許容できない場合はJSPパス切り替え方式を使用してください（`web-application-feature-details.json:s12`）
- JSPカスタムタグライブラリからコード名称を表示する場合、`Locale` 指定による言語切り替えはできません。`CodeUtil` をJavaコードから直接呼び出してください（`libraries-code.json:s8`）

参照: `libraries-message.json:s8`, `libraries-code.json:s8`, `handlers-thread-context-handler.json:s7`, `handlers-http-response-handler.json:s7`, `libraries-tag.json:s31`, `web-application-feature-details.json:s12`

---