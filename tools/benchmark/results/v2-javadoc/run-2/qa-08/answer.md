Step 5〜7: 回答を生成し、verifyを実行します。

全セクション内容を確認しました。すべてのNablarch固有の主張はセクション内容に裏付けられているため、verify_result = PASSです。

---

**結論**: Nablarchでの多言語化は、①メッセージのプロパティファイルを言語ごとに用意して`PropertiesStringResourceLoader`に登録する、②JSPでは`<n:message>`タグを使うか言語別JSPファイルへのパス切り替えを使う、という2軸で実現します。ユーザーの言語選択はCookieまたはSessionで保持します。

---

**根拠**:

### 1. メッセージの多言語化（コンポーネント設定）

言語ごとのプロパティファイルを用意し、`PropertiesStringResourceLoader`のサポート言語に登録します。

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
      <!-- デフォルトの言語（必須） -->
      <property name="defaultLocale" value="ja" />
    </component>
  </property>
</component>
```

プロパティファイルは `messages_言語.properties` という命名規則で作成します：

```
main/resources/messages.properties       # デフォルト言語（日本語）
               messages_en.properties    # 英語
```

### 2. コード名称（ラベル）の多言語化

コード名称テーブルにLANGカラムで言語ごとのデータを登録します：

| ID | VALUE | LANG | NAME |
|---|---|---|---|
| GENDER | MALE | ja | 男性 |
| GENDER | MALE | en | Male |

Java側では`CodeUtil`にLocaleを渡して言語別名称を取得できます：

```java
CodeUtil.getName("GENDER", "MALE", Locale.JAPANESE); // -> 男性
CodeUtil.getName("GENDER", "MALE", Locale.ENGLISH);  // -> Male
```

### 3. JSPでの言語切り替え（2つのアプローチ）

**アプローチA: `<n:message>`タグ**（1つのJSPファイルで対応）

```jsp
<n:message messageId="page.title" />
```

**アプローチB: 言語別JSPファイルへのパス切り替え**（レイアウト崩れを防ぐ推奨方式）

`HttpResponseHandler`の`contentPathRule`プロパティに`DirectoryBasedResourcePathRule`（言語名ディレクトリで分ける）または`FilenameBasedResourcePathRule`（ファイル名サフィックスで分ける）を設定します：

```xml
<component name="resourcePathRule"
           class="nablarch.fw.web.i18n.DirectoryBasedResourcePathRule" />

<component class="nablarch.fw.web.handler.HttpResponseHandler">
  <property name="contentPathRule" ref="resourcePathRule" />
</component>
```

`DirectoryBasedResourcePathRule`のディレクトリ構成例：
```
コンテキストルート
├─en/management/user/search.jsp
└─ja/management/user/search.jsp
```

### 4. ユーザーの言語選択を保持する

`LanguageAttributeInHttpCookie`（Cookie保持）または`LanguageAttributeInHttpSession`（Session保持）をコンポーネント名`languageAttribute`で登録します：

```xml
<component name="languageAttribute"
           class="nablarch.common.web.handler.threadcontext.LanguageAttributeInHttpCookie">
  <property name="defaultLanguage" value="ja" />
  <property name="supportedLanguages" value="ja,en" />
</component>
```

ハンドラ内で`LanguageAttributeInHttpUtil.keepLanguage()`を呼び出して言語を保存します：

```java
LanguageAttributeInHttpUtil.keepLanguage(request, context, language);
```

JSPでの言語切り替えリンクの例：
```jsp
<n:submitLink uri="/action/menu/index" name="switchToEnglish">
  英語
  <n:param paramName="user.language" value="en" />
</n:submitLink>
```

---

**注意点**:
- `PropertiesStringResourceLoader.defaultLocale`は必ず明示的に設定してください。未設定の場合はOSの設定（`Locale.getDefault().getLanguage()`）が使われ、環境依存の障害原因になります
- JSPのメッセージタグ（アプローチA）は画面レイアウトが崩れる可能性があります。レイアウトを厳密に管理したい場合はアプローチB（言語別JSPファイル）を推奨します
- JSP用カスタムタグライブラリ（コード表示タグ）からはLocaleを直接指定して名称を取得することはできません

参照: `component/libraries/libraries-message.json:s8`, `component/libraries/libraries-code.json:s8`, `component/libraries/libraries-tag.json:s31`, `component/libraries/libraries-tag.json:s32`, `component/handlers/handlers-thread-context-handler.json:s7`, `component/handlers/handlers-http-response-handler.json:s7`, `processing-pattern/web-application/web-application-feature-details.json:s12`

---