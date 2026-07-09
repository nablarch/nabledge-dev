**結論:** メッセージ・ラベルの多言語化は、言語ごとのプロパティファイル（`messages_ja.properties`、`messages_en.properties` など）を作成し、`PropertiesStringResourceLoader` にサポート言語を設定することで実現できる。ユーザが実行時に言語を切り替える場合は `LanguageAttributeInHttpCookie`（または `InHttpSession`）と `LanguageAttributeInHttpUtil.keepLanguage()` を組み合わせる。

**根拠:**

**1. 言語ごとのプロパティファイルを作成する**

ファイル名は `messages_言語.properties` とする。デフォルト言語は言語なしの `messages.properties`。

```
main/resources/messages.properties       # デフォルト（例：ja）
               messages_en.properties    # 英語用
```

`messages.properties` が存在しない場合はエラーになるため必須。

**2. PropertiesStringResourceLoader にサポート言語を設定する**

```xml
<component class="nablarch.core.cache.BasicStaticDataCache" name="messageCache">
  <property name="loader">
    <component class="nablarch.core.message.PropertiesStringResourceLoader">
      <!-- サポートする言語（デフォルト言語は不要） -->
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

<component name="stringResourceHolder" class="nablarch.core.message.StringResourceHolder">
  <property name="stringResourceCache" ref="messageCache" />
</component>
```

メッセージ取得時の言語は `ThreadContext#getLanguage` の返すロケールで決定される。

**3. ユーザが言語を選択できる画面を作る**

クッキーに言語を保持する場合（コンポーネント名を `languageAttribute` にすること）：

```xml
<component name="languageAttribute"
           class="nablarch.common.web.handler.threadcontext.LanguageAttributeInHttpCookie">
  <property name="defaultLanguage" value="ja" />
  <property name="supportedLanguages" value="ja,en" />
</component>
```

ハンドラで `LanguageAttributeInHttpUtil.keepLanguage()` を呼び出し、選択した言語をクッキーとスレッドコンテキストに保存する：

```java
public class I18nHandler implements HttpRequestHandler {
    public HttpResponse handle(HttpRequest request, ExecutionContext context) {
        String language = request.getParam("user.language")[0];
        if (StringUtil.hasValue(language)) {
            // サポート対象外の言語は無視される
            LanguageAttributeInHttpUtil.keepLanguage(request, context, language);
        }
        return context.handleNext(request);
    }
}
```

**4. JSP（コンテンツパス）を言語ごとに切り替える場合**

`HttpResponseHandler` の `contentPathRule` に `DirectoryBasedResourcePathRule`（ディレクトリ方式）または `FilenameBasedResourcePathRule`（ファイル名サフィックス方式）を設定する：

```xml
<component name="resourcePathRule"
           class="nablarch.fw.web.i18n.DirectoryBasedResourcePathRule" />

<component class="nablarch.fw.web.handler.HttpResponseHandler">
  <property name="contentPathRule" ref="resourcePathRule" />
</component>
```

ディレクトリ方式のJSP配置例：
```
コンテキストルート/en/management/user/search.jsp
コンテキストルート/ja/management/user/search.jsp
```

**5. コード名称（プルダウン等のラベル）を多言語化する場合**

コード名称テーブルに言語ごとのデータを登録する：

| ID | VALUE | LANG | SORT_ORDER | NAME | SHORT_NAME |
|---|---|---|---|---|---|
| GENDER | MALE | ja | 1 | 男性 | 男 |
| GENDER | MALE | en | 1 | Male | M |

`CodeUtil` で言語指定して取得できる：
```java
CodeUtil.getName("GENDER", "MALE", Locale.ENGLISH);  // -> Male
```

**注意点:**
- `defaultLocale` は必ず設定すること。未設定の場合は `Locale.getDefault().getLanguage()` が使われ、OS依存の値となり障害の原因になる。
- `LanguageAttributeInHttpUtil.keepLanguage()` に指定された言語が `supportedLanguages` に含まれない場合は、クッキー・スレッドコンテキストへの設定は行われない。
- カスタムレスポンスライター（Thymeleafなど）使用時はコンテンツパス切り替え機能は使用できない（テンプレートエンジン側の多言語機能を使うこと）。

参照:
- メッセージ管理
  .claude/skills/nabledge-6/docs/component/libraries/libraries-message.md
  多言語化対応
  プロパティファイルにメッセージを定義する
- スレッドコンテキスト変数管理ハンドラ
  .claude/skills/nabledge-6/docs/component/handlers/handlers-thread-context-handler.md
  ユーザが言語を選択する画面を作る
  リクエスト毎にスレッドコンテキストの初期化を行う
- HTTPレスポンスハンドラ
  .claude/skills/nabledge-6/docs/component/handlers/handlers-http-response-handler.md
  言語毎のコンテンツパスの切り替え
- コード管理
  .claude/skills/nabledge-6/docs/component/libraries/libraries-code.md
  名称の多言語化対応