**結論**: メッセージの多言語化は、言語ごとのプロパティファイル（`messages.properties`、`messages_en.properties` 等）を用意し、`PropertiesStringResourceLoader` にサポート言語を設定することで実現する。使用言語は `ThreadContext` の言語情報に基づいて自動切り替えされる。

**根拠**:

**① プロパティファイルの準備**

デフォルト言語（日本語）と英語の2ファイルを作成する：

```none
main/resources/messages.properties       # デフォルト（日本語）
               messages_en.properties    # 英語用
```

```properties
# messages.properties（日本語）
label.user.register.title=ユーザ登録画面
errors.login=ログインに失敗しました。
```

```properties
# messages_en.properties（英語）
label.user.register.title=User Registration
errors.login=Login failed.
```

**② コンポーネント定義**

`PropertiesStringResourceLoader` にサポート言語を設定する：

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

**③ 言語切り替えの設定（ユーザが選択できる場合）**

ユーザが言語を選択できるようにするには、`LanguageAttributeInHttpCookie` を使用する：

```xml
<!-- コンポーネント名を "languageAttribute" にすること -->
<component name="languageAttribute"
           class="nablarch.common.web.handler.threadcontext.LanguageAttributeInHttpCookie">
  <property name="defaultLanguage" value="ja" />
  <property name="supportedLanguages" value="ja,en" />
</component>
```

ハンドラで選択言語をクッキーに保持する：

```java
// LanguageAttributeInHttpUtil.keepLanguage でクッキーとスレッドコンテキストの両方に設定
LanguageAttributeInHttpUtil.keepLanguage(request, context, language);
```

**④ JSP でのメッセージ出力**

`n:message` タグを使うと、現在の `ThreadContext` 言語に対応したメッセージが自動表示される：

```jsp
<n:message messageId="label.user.register.title" />
```

**注意点**:
- `defaultLocale` は必ず明示的に設定すること。未設定の場合 `Locale.getDefault().getLanguage()` が使用され、実行環境依存で障害の原因になる。
- `messages.properties`（デフォルト言語ファイル）が存在しない場合はエラーになる。

参照: libraries-message.json:s8, handlers-thread-context-handler.json:s7, handlers-thread-context-handler.json:s4