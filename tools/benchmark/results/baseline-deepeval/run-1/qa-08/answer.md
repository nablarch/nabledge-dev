必要なセクションを確認しました。回答を生成します。

---

**結論**: Nablarchでは、言語ごとのプロパティファイルを用意し、`PropertiesStringResourceLoader` にサポート言語を設定することで多言語化を実現します。JSPでは `<n:message>` タグを使用して、`ThreadContext` の言語設定に応じたメッセージを表示します。

---

**根拠**:

### 1. 言語ごとのプロパティファイルを作成する

`messages.properties`（デフォルト言語）と `messages_言語.properties`（各言語）を作成します。

```
main/resources/messages.properties       # デフォルト（例：日本語）
               messages_en.properties    # 英語
```

### 2. コンポーネント設定ファイルで多言語化を設定する

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

### 3. スレッドコンテキストハンドラで言語を設定する

メッセージ取得時に使用される言語は `ThreadContext#getLanguage` の値で決まります。`ThreadContextHandler` に `LanguageAttribute` を設定します。

```xml
<component class="nablarch.common.handler.threadcontext.ThreadContextHandler">
  <property name="attributes">
    <list>
      <component class="nablarch.common.handler.threadcontext.LanguageAttribute">
        <property name="defaultLanguage" value="ja" />
      </component>
      <!-- その他の属性は省略 -->
    </list>
  </property>
</component>
```

### 4. ユーザが言語を切り替えられるようにする（クッキーで保持する場合）

```xml
<!-- コンポーネント名を"languageAttribute"にする -->
<component name="languageAttribute"
           class="nablarch.common.web.handler.threadcontext.LanguageAttributeInHttpCookie">
  <property name="defaultLanguage" value="ja" />
  <property name="supportedLanguages" value="ja,en" />
</component>
```

ハンドラで言語の保持を行います。

```java
public class I18nHandler implements HttpRequestHandler {
    public HttpResponse handle(HttpRequest request, ExecutionContext context) {
        String language = request.getParam("user.language")[0]; // 例
        if (StringUtil.hasValue(language)) {
            // クッキーとスレッドコンテキストに言語を設定する
            LanguageAttributeInHttpUtil.keepLanguage(request, context, language);
        }
        return context.handleNext(request);
    }
}
```

### 5. JSPでメッセージを出力する

```jsp
<!-- messageId属性にメッセージIDを指定する -->
<n:message messageId="label.user.name" />
```

プロパティファイルに各言語のメッセージを定義します。

```properties
# messages.properties（日本語）
label.user.name=ユーザー名

# messages_en.properties（英語）
label.user.name=User Name
```

**注意点**:
- `defaultLocale` は必ず設定すること。設定しないと `Locale.getDefault()` が使用され、実行環境に依存した値になり障害の原因になります。
- `messages.properties`（デフォルト言語のファイル）が存在しない場合はエラーになります。
- `LanguageAttributeInHttpCookie` や `LanguageAttributeInHttpSession` を使う場合、コンポーネント名を `languageAttribute` にする必要があります。

参照: libraries-message.json:s8, handlers-thread-context-handler.json:s4, handlers-thread-context-handler.json:s7, libraries-tag.json:s31

---