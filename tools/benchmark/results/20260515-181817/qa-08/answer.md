**結論**: Nablarchでは、メッセージ（バリデーションエラー等）とコード名称（ラベル）の多言語化、およびJSPのリソースパス切り替えという3つのアプローチで多言語対応できます。

**根拠**:

### 1. メッセージの多言語化（`PropertiesStringResourceLoader`）

言語ごとのプロパティファイルを用意し、`PropertiesStringResourceLoader.locales` にサポート言語を設定します。

**プロパティファイル構成**:
```
main/resources/messages.properties       # デフォルト言語（必須）
               messages_en.properties    # 英語
               messages_ja.properties    # 日本語（デフォルト以外の場合）
```

**コンポーネント設定例**:
```xml
<component class="nablarch.core.cache.BasicStaticDataCache" name="messageCache">
  <property name="loader">
    <component class="nablarch.core.message.PropertiesStringResourceLoader">
      <property name="locales">
        <list>
          <value>en</value>
          <value>zh</value>
        </list>
      </property>
      <!-- デフォルト言語は必ず明示すること（OS依存のLocale.getDefault()は使わない） -->
      <property name="defaultLocale" value="ja" />
    </component>
  </property>
</component>
```

使用言語は `ThreadContext#getLanguage` が返すロケールで決定されます。

### 2. コード名称（ラベル）の多言語化

コード名称テーブルに言語ごとのデータを用意します。

テーブルデータ例:

| ID | VALUE | LANG | NAME |
|---|---|---|---|
| GENDER | MALE | ja | 男性 |
| GENDER | MALE | en | Male |

Java での取得:
```java
CodeUtil.getName("GENDER", "MALE", Locale.JAPANESE);  // -> 男性
CodeUtil.getName("GENDER", "MALE", Locale.ENGLISH);   // -> Male
```

### 3. JSPリソースパスの言語切り替え（`HttpResponseHandler`）

`HttpResponseHandler` の `contentPathRule` プロパティに以下のいずれかを設定します。

| クラス名 | 説明 |
|---|---|
| `DirectoryBasedResourcePathRule` | コンテキストルート直下のディレクトリで言語切り替え |
| `FilenameBasedResourcePathRule` | ファイル名で言語切り替え |

```xml
<component name="resourcePathRule"
           class="nablarch.fw.web.i18n.DirectoryBasedResourcePathRule" />
<component class="nablarch.fw.web.handler.HttpResponseHandler">
  <property name="contentPathRule" ref="resourcePathRule" />
</component>
```

**注意点**:
- `PropertiesStringResourceLoader.defaultLocale` は必ず明示してください。未設定の場合 `Locale.getDefault()` （OS設定依存）が使われ、環境によって挙動が変わります。
- `messages.properties`（デフォルト言語用ファイル）が存在しない場合、エラーになります。
- JSPのカスタムタグライブラリ（`<n:code>` 等）では言語指定によるコード値取得はできません。Javaコードで `CodeUtil.getName()` を使う必要があります。
- メッセージタグ（`<n:message>`）での国際化対応は、画面レイアウト崩れのリスクがあるため、崩れを許容できる場合のみ使用してください。

参照: component/libraries/libraries-message.json#s8 / component/libraries/libraries-code.json#s8 / component/handlers/handlers-http-response-handler.json#s7 / processing-pattern/web-application/web-application-feature-details.json#s12