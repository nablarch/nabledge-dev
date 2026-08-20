### Answer

Nablarchで日本語・英語のメッセージ/ラベルを切り替えるには、以下の3つの設定が必要です。

---

## 1. メッセージの多言語化

### プロパティファイルの準備

言語ごとにプロパティファイルを作成します。

```
src/main/resources/messages.properties       # デフォルト言語（例: ja）
                  messages_en.properties     # 英語
```

### コンポーネント設定

`PropertiesStringResourceLoader` にサポート言語とデフォルト言語を設定します。

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
      <!-- デフォルト言語（必須：省略するとOS設定に依存して障害の原因になる） -->
      <property name="defaultLocale" value="ja" />
    </component>
  </property>
</component>
```

> **重要:** `defaultLocale` は必ず明示的に設定してください。省略すると `Locale.getDefault().getLanguage()` が使われ、実行環境によって値が変わり障害の原因になります。

### JSPでの表示（messageタグ）

```jsp
<!-- ユーザの言語設定に応じて自動で切り替わる -->
<n:message messageId="label.user.name" />

<!-- 特定の言語を強制指定したい場合 -->
<n:message messageId="label.user.name" language="ja" />
```

> **注意:** `messageタグ` を使うと画面レイアウトが崩れる可能性があります。レイアウト崩れを許容できる場合のみ使用してください。レイアウトへの影響が懸念される場合は、後述の「言語ごとにリソースパスを切り替える」方式を検討してください。

---

## 2. コード名称（ラベル）の多言語化

コードマスタテーブルに言語ごとのデータを登録します。

| ID | VALUE | LANG | NAME | SHORT_NAME |
|----|-------|------|------|------------|
| GENDER | MALE | ja | 男性 | 男 |
| GENDER | MALE | en | Male | M |

Javaコードで言語を指定して取得します。

```java
CodeUtil.getName("GENDER", "MALE", Locale.JAPANESE);  // -> 男性
CodeUtil.getName("GENDER", "MALE", Locale.ENGLISH);   // -> Male
```

> **注意:** JSP用カスタムタグライブラリでは言語指定による取得はできません。

---

## 3. ユーザによる言語切り替え（クッキー/セッション保持）

ユーザが画面で言語を選択できるようにするには、`LanguageAttributeInHttpCookie` と `LanguageAttributeInHttpUtil` を使います。

### コンポーネント設定

```xml
<component name="languageAttribute"
           class="nablarch.common.web.handler.threadcontext.LanguageAttributeInHttpCookie">
  <property name="defaultLanguage" value="ja" />
  <property name="supportedLanguages" value="ja,en" />
</component>
```

### JSP（言語切り替えリンク）

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

### ハンドラ（言語をクッキーに保存）

```java
public class I18nHandler implements HttpRequestHandler {
    public HttpResponse handle(HttpRequest request, ExecutionContext context) {
        String language = request.getParam("user.language")[0];
        if (StringUtil.hasValue(language)) {
            // クッキーとスレッドコンテキストに言語を設定する
            // サポート対象外の言語の場合は設定しない
            LanguageAttributeInHttpUtil.keepLanguage(request, context, language);
        }
        return context.handleNext(request);
    }
}
```

---

## まとめ

| 対象 | 方法 |
|------|------|
| メッセージ文言 | `messages_en.properties` を追加し `PropertiesStringResourceLoader` に設定 |
| コード名称/ラベル | コードマスタに言語別データを登録し `CodeUtil.getName()` で取得 |
| 言語切り替えUI | `LanguageAttributeInHttpCookie` + `LanguageAttributeInHttpUtil.keepLanguage()` |
| JSP表示 | `<n:message>` タグ（レイアウト崩れ注意）または言語別リソースパス切り替え |