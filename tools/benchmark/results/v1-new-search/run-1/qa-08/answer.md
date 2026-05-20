**結論**: Nablarchで多言語化（日本語/英語切り替え）を実現するには、「メッセージ管理の多言語化」と「言語選択のしくみ」の2つを組み合わせて実装します。

**根拠**:

## 1. メッセージプロパティファイルの準備

言語ごとにプロパティファイルを作成します。

```
main/resources/messages.properties       # デフォルト言語（例: 日本語）
               messages_en.properties    # 英語
```

例:
```properties
# messages.properties（日本語）
label.name=名前
msg.required=必須項目です

# messages_en.properties（英語）
label.name=Name
msg.required=This field is required.
```

## 2. `PropertiesStringResourceLoader` の設定（コンポーネント定義）

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
      <!-- デフォルト言語（必須） -->
      <property name="defaultLocale" value="ja" />
    </component>
  </property>
</component>

<component name="stringResourceHolder" class="nablarch.core.message.StringResourceHolder">
  <property name="stringResourceCache" ref="messageCache" />
</component>
```

> `defaultLocale` は必ず明示的に設定してください。未設定だと OS の Locale に依存し、環境差異の障害原因になります。

## 3. ユーザが言語を選択できるしくみ（ウェブアプリケーションの場合）

言語選択をクッキーに保持するハンドラと設定例:

```xml
<component name="languageAttribute"
           class="nablarch.common.web.handler.threadcontext.LanguageAttributeInHttpCookie">
  <property name="defaultLanguage" value="ja" />
  <property name="supportedLanguages" value="ja,en" />
</component>
```

JSP での言語切り替えリンク:

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

ハンドラで選択言語をスレッドコンテキストに保存:

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

## 4. JSP でのメッセージ出力

```jsp
<!-- ThreadContext の言語設定に従ってメッセージを出力 -->
<n:message messageId="label.name" />
```

## 5. JSP ファイル自体を言語で切り替えたい場合

`HttpResponseHandler` の `contentPathRule` を使うと、JSP ファイルをディレクトリまたはファイル名で言語ごとに切り替えられます:

```xml
<component name="resourcePathRule"
           class="nablarch.fw.web.i18n.DirectoryBasedResourcePathRule" />

<component class="nablarch.fw.web.handler.HttpResponseHandler">
  <property name="contentPathRule" ref="resourcePathRule" />
</component>
```

ディレクトリ構成例:
```
コンテキストルート/
  ├─ ja/
  │   └─ management/search.jsp
  └─ en/
      └─ management/search.jsp
```

**注意点**:
- `messages.properties`（デフォルトファイル）が存在しない場合はエラー終了します。必ず作成してください。
- `messageタグ`による1ファイル多言語対応は画面レイアウト崩れが起きる可能性があるため、レイアウト崩れを許容できる場合のみ使用してください。
- コード名称の多言語化（プルダウン等のラベル）は別途コード名称テーブルへの言語ごとのデータ準備が必要です（`CodeUtil.getName("ID", "VALUE", Locale.ENGLISH)` で取得可能）。

参照: component/libraries/libraries-message.json:s8, component/handlers/handlers-thread-context-handler.json:s7, component/handlers/handlers-http-response-handler.json:s7, component/libraries/libraries-tag.json:s31, component/libraries/libraries-tag.json:s32, component/libraries/libraries-code.json:s8, processing-pattern/web-application/web-application-feature-details.json:s12