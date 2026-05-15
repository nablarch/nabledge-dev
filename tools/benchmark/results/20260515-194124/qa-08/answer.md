**結論**: Nablarch 6でメッセージ・ラベルを日本語/英語で切り替えるには、言語ごとのプロパティファイルを用意し、`PropertiesStringResourceLoader` に多言語設定を行い、`ThreadContextHandler` でリクエストごとの言語を管理します。

**根拠**:

**1. プロパティファイルの作成**

言語ごとにプロパティファイルを用意します。

```
main/resources/messages.properties       # デフォルト言語（例：ja）用
               messages_en.properties    # 英語用
```

`messages.properties` が存在しない場合はエラーになるため、必ず作成してください。

**2. PropertiesStringResourceLoader の多言語設定**

```xml
<component class="nablarch.core.cache.BasicStaticDataCache" name="messageCache">
  <property name="loader">
    <component class="nablarch.core.message.PropertiesStringResourceLoader">
      <property name="locales">
        <list>
          <value>en</value>
        </list>
      </property>
      <!-- デフォルトの言語（必須設定） -->
      <property name="defaultLocale" value="ja" />
    </component>
  </property>
</component>

<component name="stringResourceHolder" class="nablarch.core.message.StringResourceHolder">
  <property name="stringResourceCache" ref="messageCache" />
</component>
```

**重要**: `defaultLocale` は必ず明示的に設定してください。設定しないと `Locale.getDefault().getLanguage()`（OSの設定に依存）が使われ、環境によって動作が変わります。

**3. リクエストごとの言語設定（ThreadContextHandler）**

```xml
<component class="nablarch.common.handler.threadcontext.ThreadContextHandler">
  <property name="attributes">
    <list>
      <component class="nablarch.common.handler.threadcontext.LanguageAttribute">
        <property name="defaultLanguage" value="ja" />
      </component>
    </list>
  </property>
</component>
```

メッセージ取得時の言語は `ThreadContext#getLanguage` の戻り値で決まります。

**4. ユーザが言語を切り替える画面の実装（Webアプリの場合）**

クッキーやセッションに言語を保持するには `LanguageAttributeInHttpCookie` または `LanguageAttributeInHttpSession` を使います。

コンポーネント設定:
```xml
<component name="languageAttribute"
           class="nablarch.common.web.handler.threadcontext.LanguageAttributeInHttpCookie">
  <property name="defaultLanguage" value="ja" />
  <property name="supportedLanguages" value="ja,en" />
</component>
```

JSP（言語切り替えリンク）:
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

ハンドラ実装（言語選択の保持）:
```java
public class I18nHandler implements HttpRequestHandler {
    public HttpResponse handle(HttpRequest request, ExecutionContext context) {
        String language = request.getParamMap().containsKey("user.language")
            ? request.getParam("user.language")[0] : null;
        if (StringUtil.hasValue(language)) {
            LanguageAttributeInHttpUtil.keepLanguage(request, context, language);
        }
        return context.handleNext(request);
    }
}
```

**5. 画面での固定文言表示**

JSPでは `<n:message>` タグを使ってプロパティファイルからメッセージを取得します。リクエストの言語に応じて自動的に対応するプロパティファイルが選択されます。

```jsp
<span><n:message messageId="label.user.register.title" /></span>
```

**注意点**:

- `messages.properties`（デフォルト言語用ファイル）は必須。存在しないとエラーになります。
- `defaultLocale` は必ず明示設定してください（OS依存を避けるため）。
- メッセージの更新（プロパティファイルの変更）はアプリケーションの再起動が必要です。実行中のメッセージ更新機能は提供されていません。
- `nablarch-fw-web` モジュールは、言語・タイムゾーンを選択できる画面を作る場合のみ必要です。

参照: `libraries-message.json#s8`, `handlers-thread-context-handler.json#s7`, `handlers-thread-context-handler.json#s4`