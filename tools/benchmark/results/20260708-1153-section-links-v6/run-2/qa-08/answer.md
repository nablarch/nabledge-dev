**結論**: Nablarchでのメッセージ・ラベルの多言語化は、言語ごとのプロパティファイルを用意し、`PropertiesStringResourceLoader`にサポート言語を設定することで実現します。ユーザーが言語を切り替えられるよう、`スレッドコンテキスト変数管理ハンドラ`で`LanguageAttributeInHttpCookie`等を使った言語選択機能を組み合わせます。

**根拠**:

**1. メッセージの多言語化（メッセージ管理）**

言語ごとのプロパティファイルを作成し、コンポーネント定義で`PropertiesStringResourceLoader`にサポート言語を設定します。

プロパティファイルの配置（`messages.properties`はデフォルト言語）:
```
main/resources/messages.properties       # デフォルト（例: 日本語）
               messages_en.properties    # 英語
               messages_zh.properties    # 中国語
```

コンポーネント定義例:
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

<component name="stringResourceHolder" class="nablarch.core.message.StringResourceHolder">
  <property name="stringResourceCache" ref="messageCache" />
</component>
```

> **注意**: `defaultLocale`を設定しないと`Locale.getDefault().getLanguage()`がOS依存の値を返し、環境によって動作が変わるため必ず設定すること。

メッセージ取得時にどの言語が使われるかは`ThreadContext#getLanguage()`が返すロケールで決まります。

**2. ユーザーが言語を切り替えられる画面（スレッドコンテキスト変数管理ハンドラ）**

クッキーに言語を保持する場合の設定例:
```xml
<!-- コンポーネント名を"languageAttribute"にすること -->
<component name="languageAttribute"
           class="nablarch.common.web.handler.threadcontext.LanguageAttributeInHttpCookie">
  <property name="defaultLanguage" value="ja" />
  <property name="supportedLanguages" value="ja,en" />
</component>
```

JSPでの言語選択リンク例:
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

ハンドラでの言語保持処理:
```java
public class I18nHandler implements HttpRequestHandler {
    public HttpResponse handle(HttpRequest request, ExecutionContext context) {
        String language = request.getParamMap().containsKey("user.language")
            ? request.getParam("user.language")[0] : null;
        if (StringUtil.hasValue(language)) {
            // クッキーとスレッドコンテキストに選択された言語を設定
            LanguageAttributeInHttpUtil.keepLanguage(request, context, language);
        }
        return context.handleNext(request);
    }
}
```

**3. JSPでのコンテンツ（JSPファイル自体）の言語切り替え**

JSPファイルごと切り替えたい場合は、`HTTPレスポンスハンドラ`の`contentPathRule`プロパティに`DirectoryBasedResourcePathRule`または`FilenameBasedResourcePathRule`を設定します:

```xml
<component name="resourcePathRule"
           class="nablarch.fw.web.i18n.DirectoryBasedResourcePathRule" />

<component class="nablarch.fw.web.handler.HttpResponseHandler">
  <property name="contentPathRule" ref="resourcePathRule" />
</component>
```

**注意点**:
- `messages.properties`（デフォルト言語ファイル）が存在しない場合はエラーで処理が終了する
- カスタムレスポンスライター（Thymeleafなど）を使用する場合、`contentPathRule`の言語切り替え機能は使用できない（テンプレートエンジン側の多言語機能を使用すること）
- コード管理機能のコード名称を多言語化する場合は、コード名称テーブルに言語別データを登録し、`CodeUtil.getName("GENDER", "MALE", Locale.ENGLISH)`のように言語を指定して取得する

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