**質問**: 画面の文言を日本語と英語で切り替えたい。メッセージやラベルの多言語対応は Nablarch でできる？

---

**結論**: Nablarch は多言語対応をビルトインで提供している。メッセージは言語ごとのプロパティファイルを作り、`PropertiesStringResourceLoader` でサポート言語とデフォルトロケールを設定する。コード名称は `LANG` カラムに言語を設定した名称テーブルを用意し、`CodeUtil.getName(codeId, value, Locale)` でロケール指定取得する。 — `processing-pattern/web-application/web-application-feature_details.json#s12`、`component/libraries/libraries-message.json#s5`、`component/libraries/libraries-code.json#s3`

**① パターン側の位置づけ**
静的リソースの多言語化として、**メッセージの多言語化** と **コード名称の多言語化** の2本立て。言語切り替えは2通り:
- メッセージタグでの国際化対応
- 言語ごとにリソースのパスを切り替える

> **警告**: メッセージタグで国際化対応すると、画面レイアウトが崩れる可能性がある。レイアウト崩れを許容できる場合のみ使用する。 — `processing-pattern/web-application/web-application-feature_details.json#s12`

**② メッセージの多言語化**
言語ごとのプロパティファイルを作成し、`PropertiesStringResourceLoader.locales` にサポート言語を設定する。デフォルトロケールに対応する言語はサポート言語に追加しなくて良い。

> **重要**: デフォルトロケールは `PropertiesStringResourceLoader.defaultLocale` で **必ず設定する**。未設定の場合は `Locale.getDefault().getLanguage()` が使われるが、この値は OS 設定によって変化するため障害の原因になる。

メッセージ取得時の言語は `ThreadContext#getLanguage` が返すロケールで決まる。取得できない場合は `Locale.getDefault()`。

XML 設定例（`en`/`zh`/`de` をサポート、`ja` をデフォルト）:
```xml
<component class="nablarch.core.cache.BasicStaticDataCache" name="messageCache">
  <property name="loader">
    <component class="nablarch.core.message.PropertiesStringResourceLoader">
      <property name="locales">
        <list>
          <value>en</value>
          <value>zh</value>
          <value>de</value>
        </list>
      </property>
      <property name="defaultLocale" value="ja" />
    </component>
  </property>
</component>
```
— `component/libraries/libraries-message.json#s5`

**③ コード名称の多言語化**
コード名称テーブルにサポート言語ごとのデータを準備する（`LANG` カラムに言語を設定）。

```java
// 名称
CodeUtil.getName("GENDER", "MALE", Locale.JAPANESE);    // -> 男性
CodeUtil.getName("GENDER", "MALE", Locale.ENGLISH);     // -> Male

// 略称
CodeUtil.getShortName("GENDER", "MALE", Locale.JAPANESE); // -> 男
CodeUtil.getShortName("GENDER", "MALE", Locale.ENGLISH);  // -> M
```

> **重要**: JSP 用カスタムタグライブラリでは言語指定による値の取得はできない。 — `component/libraries/libraries-code.json#s3`
