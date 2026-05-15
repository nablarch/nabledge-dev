**結論**: Nablarchでメッセージ・ラベルを多言語化（日本語/英語など）するには、言語ごとのプロパティファイルを用意し、`PropertiesStringResourceLoader` にサポート言語を設定します。ユーザーが言語を切り替えられるようにするには、`LanguageAttributeInHttpCookie` または `LanguageAttributeInHttpSession` と `LanguageAttributeInHttpUtil` を組み合わせて使います。

**根拠**:

### 1. 言語ごとのプロパティファイルを作成する

デフォルトのロケール用と、サポートする言語ごとのファイルを用意します。

```
src/main/resources/messages.properties       # デフォルト（例: ja）
                  messages_en.properties    # 英語
                  messages_zh.properties    # 中国語
```

各ファイルに対応するメッセージを定義します（UTF-8で記述可。native2ascii不要）:

```properties
# messages.properties（日本語）
label.user.name=ユーザ名
errors.login=ログインに失敗しました。

# messages_en.properties（英語）
label.user.name=User Name
errors.login=Login failed.
```

### 2. PropertiesStringResourceLoader にサポート言語を設定する

コンポーネント設定ファイルに以下を記述します：

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
      <!-- デフォルトの言語（必ず明示すること） -->
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

メッセージ取得時に使用される言語は ThreadContext#getLanguage の返すロケールで決まります。

### 3. ユーザーが言語を選択できる画面を実装する

クッキーで言語を保持する場合：

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

ハンドラ（言語をクッキーとスレッドコンテキストに保持）:
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

**注意点**:
- `defaultLocale` は必ず明示してください。設定しない場合、`Locale.getDefault().getLanguage()` (OS依存) が使われ、環境によって動作が変わり障害の原因になります
- `messages.properties`（デフォルトのロケールファイル）が存在しない場合はエラーになります
- メッセージは実行中に更新できません。変更時はアプリケーションの再起動が必要です
- 言語として `supportedLanguages` に含まれない値が送信されてきた場合、クッキー・スレッドコンテキストへの設定は行われません

参照: component/libraries/libraries-message.json#s8, component/handlers/handlers-thread-context-handler.json#s7