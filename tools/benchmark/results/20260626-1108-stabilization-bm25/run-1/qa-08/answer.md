Nablarchで日本語と英語を切り替える多言語化は、主に「メッセージ管理の多言語化」と「スレッドコンテキストへの言語設定」の2つの柱で実現します。

---

## 1. 言語別プロパティファイルの作成

デフォルトのプロパティファイル（日本語）と、言語別のファイルを用意します。ファイル名は `messages_言語.properties` とします。

```
src/main/resources/messages.properties       # デフォルト（日本語）
                   messages_en.properties    # 英語
```

```properties
# messages.properties（日本語）
label.user.name=ユーザ名
errors.required=入力してください。
```

```properties
# messages_en.properties（英語）
label.user.name=User Name
errors.required=This field is required.
```

> **注意:** `messages.properties` が存在しない場合はエラーになります。必ず作成してください。

---

## 2. PropertiesStringResourceLoader の設定

コンポーネント設定ファイルで `PropertiesStringResourceLoader` にサポートする言語を設定します。**`defaultLocale` は必ず明示的に設定してください**（未設定だとOSの設定に依存し、障害の原因になります）。

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

メッセージ取得時にどの言語を使うかは `ThreadContext#getLanguage` の値で決まります。

---

## 3. スレッドコンテキストへの言語設定

### 基本設定（リクエスト毎に言語を初期化）

`ThreadContextHandler` に `LanguageAttribute` を追加します。

```xml
<component class="nablarch.common.handler.threadcontext.ThreadContextHandler">
  <property name="attributes">
    <list>
      <!-- 言語 -->
      <component class="nablarch.common.handler.threadcontext.LanguageAttribute">
        <property name="defaultLanguage" value="ja" />
      </component>
      <!-- その他の属性（リクエストIDなど） -->
    </list>
  </property>
</component>
```

### ユーザが言語を選択できる場合（クッキーまたはセッションで保持）

言語選択をクッキーで保持する場合は `LanguageAttributeInHttpCookie` を使用します。

```xml
<!-- コンポーネント名は "languageAttribute" にする（LanguageAttributeInHttpUtil が使用） -->
<component name="languageAttribute"
           class="nablarch.common.web.handler.threadcontext.LanguageAttributeInHttpCookie">
  <property name="defaultLanguage" value="ja" />
  <property name="supportedLanguages" value="ja,en" />
</component>
```

言語を切り替えるリンクをJSPで実装します。

```jsp
<n:submitLink uri="/action/menu/index" name="switchToEnglish">
  English
  <n:param paramName="user.language" value="en" />
</n:submitLink>
<n:submitLink uri="/action/menu/index" name="switchToJapanese">
  日本語
  <n:param paramName="user.language" value="ja" />
</n:submitLink>
```

ユーザが選択した言語をクッキーとスレッドコンテキストに保存するハンドラを実装します。

```java
public class I18nHandler implements HttpRequestHandler {
    public HttpResponse handle(HttpRequest request, ExecutionContext context) {
        String language = request.getParamMap().containsKey("user.language")
            ? request.getParam("user.language")[0] : null;
        if (StringUtil.hasValue(language)) {
            // クッキーとスレッドコンテキストに言語を設定
            // （サポート対象外の言語が指定された場合は設定しない）
            LanguageAttributeInHttpUtil.keepLanguage(request, context, language);
        }
        return context.handleNext(request);
    }
}
```

---

## 4. 画面でメッセージ・ラベルを出力する

### JSPで `<n:message>` タグを使用

```jsp
<!-- messageId を指定してメッセージを出力（スレッドコンテキストの言語が適用される） -->
<n:message messageId="label.user.name" />

<!-- 特定の言語を明示的に指定したい場合 -->
<n:message messageId="label.user.name" language="ja" />
```

---

## 5. JSPファイル自体を言語で切り替える場合

メッセージだけでなくJSPファイル全体を言語別にしたい場合は、`HttpResponseHandler` の `contentPathRule` を設定します。

```xml
<!-- ディレクトリで言語を切り替える例 -->
<component name="resourcePathRule"
           class="nablarch.fw.web.i18n.DirectoryBasedResourcePathRule" />

<component class="nablarch.fw.web.handler.HttpResponseHandler">
  <property name="contentPathRule" ref="resourcePathRule" />
</component>
```

ディレクトリ構成例：
```
コンテキストルート/
├── en/
│   └── user/search.jsp
└── ja/
    └── user/search.jsp
```

---

## まとめ

| やりたいこと | 使うもの |
|---|---|
| メッセージ・ラベルを言語別に定義 | `messages.properties` / `messages_en.properties` |
| メッセージの言語切り替え設定 | `PropertiesStringResourceLoader`（`locales`、`defaultLocale`） |
| リクエスト毎の言語初期化 | `ThreadContextHandler` + `LanguageAttribute` |
| ユーザによる言語選択 | `LanguageAttributeInHttpCookie` / `LanguageAttributeInHttpSession` + `LanguageAttributeInHttpUtil` |
| JSPでのメッセージ出力 | `<n:message messageId="...">` タグ |
| JSPファイル自体の切り替え | `HttpResponseHandler` + `DirectoryBasedResourcePathRule` |