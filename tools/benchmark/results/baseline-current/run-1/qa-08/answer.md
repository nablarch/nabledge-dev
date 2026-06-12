**結論**: Nablarch 6 では、メッセージ・ラベルの多言語化に「言語ごとのプロパティファイル」方式と、画面全体の切り替えには「リソースパス切り替え」方式の2通りを提供している。コード名称の多言語化はデータベースのコード名称テーブルで対応する。

**根拠**:

**1. メッセージ（ラベル・エラーメッセージ等）の多言語化**

`PropertiesStringResourceLoader` の `locales` プロパティにサポートする言語を設定し、言語ごとのプロパティファイルを用意する。

コンポーネント設定例：

```xml
<component class="nablarch.core.cache.BasicStaticDataCache" name="messageCache">
  <property name="loader">
    <component class="nablarch.core.message.PropertiesStringResourceLoader">
      <property name="locales">
        <list>
          <value>en</value>
        </list>
      </property>
      <property name="defaultLocale" value="ja" />
    </component>
  </property>
</component>
```

プロパティファイルの配置：

```
main/resources/messages.properties        # デフォルト言語（日本語）
               messages_en.properties     # 英語
```

使用する言語は `ThreadContext#getLanguage` が返すロケールで決定される。JSPでは `<n:message>` タグで出力する：

```jsp
<n:message messageId="label.user.register.title" />
<n:message messageId="label.user.register.title" language="ja" />
```

**2. 画面全体（JSP）のリソースパス切り替え**

`HttpResponseHandler` の `contentPathRule` プロパティに `DirectoryBasedResourcePathRule` または `FilenameBasedResourcePathRule` を設定すると、言語に応じて転送先JSPを動的に切り替えられる。

```xml
<component name="resourcePathRule"
           class="nablarch.fw.web.i18n.DirectoryBasedResourcePathRule" />
<component class="nablarch.fw.web.handler.HttpResponseHandler">
  <property name="contentPathRule" ref="resourcePathRule" />
</component>
```

配置例：

```
コンテキストルート
├─en/management/user/search.jsp
└─ja/management/user/search.jsp
```

**3. コード名称（プルダウン等）の多言語化**

コード名称テーブルに言語ごとのデータ行を登録する。Javaコードからは `CodeUtil` で言語を指定して名称を取得できる：

```java
CodeUtil.getName("GENDER", "MALE", Locale.JAPANESE);  // -> 男性
CodeUtil.getName("GENDER", "MALE", Locale.ENGLISH);   // -> Male
```

**注意点**:

- `defaultLocale` の設定は必須。設定しない場合は `Locale.getDefault().getLanguage()`（OS依存）が使われ、環境によって挙動が変わる障害の原因になる。
- `messages.properties`（デフォルト言語ファイル）が存在しない場合はエラーとなる。
- メッセージタグ（`<n:message>`）での国際化対応は、文言の長さが言語間で異なる場合に画面レイアウトが崩れる可能性がある。レイアウト崩れを許容できない場合は「言語ごとにリソースパスを切り替える」方式を使うこと。
- `HttpResponseHandler` のリソースパス切り替えは、カスタムレスポンスライター（Thymeleaf等）を使用する場合は利用できない。
- JSP用コードタグ（`<n:codeSelect>` 等）が使用する言語情報は `ThreadContext` から取得される。

参照: `libraries-message.json#s8`, `libraries-tag.json#s31`, `libraries-tag.json#s32`, `handlers-http-response-handler.json#s7`, `web-application-feature-details.json#s12`, `libraries-code.json#s8`