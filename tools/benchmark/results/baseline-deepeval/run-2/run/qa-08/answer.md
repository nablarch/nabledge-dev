**結論**: Nablarchの多言語化は、**言語別プロパティファイル** + **ThreadContextHandlerでの言語設定** + **JSPのmessageタグ**の3つを組み合わせて実装します。

**根拠**:

#### 1. 言語別プロパティファイルの作成

`PropertiesStringResourceLoader` にサポート言語を設定し、言語ごとのプロパティファイルを用意します。

コンポーネント設定ファイル:

```xml
<component class="nablarch.core.cache.BasicStaticDataCache" name="messageCache">
  <property name="loader">
    <component class="nablarch.core.message.PropertiesStringResourceLoader">
      <!-- サポートする言語 -->
      <property name="locales">
        <list>
          <value>en</value>
          <value>ja</value>
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

<component name="initializer"
           class="nablarch.core.repository.initialization.BasicApplicationInitializer">
  <property name="initializeList">
    <list>
      <component-ref name="messageCache" />
    </list>
  </property>
</component>
```

プロパティファイルの配置:

```
main/resources/messages.properties       # デフォルト言語（ja）用
               messages_en.properties    # 英語用
```

`messages.properties`:
```properties
label.user.register.title=ユーザ登録画面
errors.login=ログインに失敗しました。
```

`messages_en.properties`:
```properties
label.user.register.title=User Registration
errors.login=Login failed.
```

#### 2. ユーザの言語選択を保持する（ウェブアプリケーションの場合）

`LanguageAttributeInHttpCookie`（またはSession）と `LanguageAttributeInHttpUtil` を使って、ユーザが選んだ言語をクッキーに保存します。

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

ハンドラ実装（言語をクッキーに保存）:

```java
public class I18nHandler implements HttpRequestHandler {
    public HttpResponse handle(HttpRequest request, ExecutionContext context) {
        String language = request.getParamMap().containsKey("user.language")
            ? request.getParam("user.language")[0] : null;
        if (StringUtil.hasValue(language)) {
            // クッキーとスレッドコンテキストに言語を設定
            LanguageAttributeInHttpUtil.keepLanguage(request, context, language);
        }
        return context.handleNext(request);
    }
}
```

#### 3. JSPでのメッセージ出力

`<n:message>` タグを使用すると、ThreadContextの言語設定に応じたメッセージが自動的に出力されます。

```jsp
<span><n:message messageId="label.user.register.title" /></span>
```

#### 4. JSPファイル自体を言語別に切り替える（オプション）

JSPファイルを言語別に用意する場合は、`HttpResponseHandler` の `contentPathRule` を設定します。

```xml
<component name="resourcePathRule" class="nablarch.fw.web.i18n.DirectoryBasedResourcePathRule" />

<component class="nablarch.fw.web.handler.HttpResponseHandler">
  <property name="contentPathRule" ref="resourcePathRule" />
</component>
```

この場合、コンテキストルート直下に言語ごとのディレクトリを作成します:

```
コンテキストルート
├─en
│  └─management/user/search.jsp
└─ja
   └─management/user/search.jsp
```

**注意点**:
- `defaultLocale` は必ず明示的に設定すること。未設定の場合 `Locale.getDefault().getLanguage()` が使用されるため、実行環境のOSによって値が変わり障害の原因になる
- `messages.properties`（デフォルト言語のファイル）は必ず存在すること。存在しない場合はエラーになる
- `LanguageAttributeInHttpUtil.keepLanguage()` に指定した言語がサポート対象外の場合、クッキーとスレッドコンテキストへの設定は行われない

参照: `libraries-message.json:s8`, `handlers-thread-context-handler.json:s7`, `handlers-http-response-handler.json:s7`, `libraries-tag.json:s32`

---