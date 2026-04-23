**結論**: Nablarch は標準機能として多言語対応をサポートしており、メッセージ・ラベル・コード名称をすべて日本語/英語で切り替えることができる。

**根拠**:

1. **メッセージの多言語化**: `PropertiesStringResourceLoader` を使い、言語ごとのプロパティファイル（`messages.properties` / `messages_en.properties` など）を用意し、`locales` プロパティにサポート言語を列挙する。メッセージ取得時の言語は `ThreadContext#getLanguage` が返すロケールで決まる。(`component/libraries/libraries-message.json:s5`)

2. **コード名称の多言語化**: コード名称テーブルに言語ごとのデータ（LANGカラム）を準備することで、`CodeUtil.getName("GENDER", "MALE", Locale.ENGLISH)` のように言語を指定して名称を取得できる。(`component/libraries/libraries-code.json:s3`)

3. **ユーザによる言語切り替え**: `LanguageAttributeInHttpCookie`（または `LanguageAttributeInHttpSession`）と `LanguageAttributeInHttpUtil` を組み合わせることで、リンクやフォームで言語を選択させる画面を実装できる。ハンドラで `LanguageAttributeInHttpUtil.keepLanguage()` を呼ぶと、クッキーとスレッドコンテキストの両方に言語が保存される。(`component/handlers/handlers-thread_context_handler.json:s7`)

4. **画面への適用方法は2通り**: ① メッセージタグで国際化対応、② 言語ごとにリソースのパスを切り替える、の2種類がある。(`processing-pattern/web-application/web-application-feature_details.json:s12`)

**注意点**:
- `PropertiesStringResourceLoader.defaultLocale` は **必ず明示設定**すること。未設定だと OS の `Locale.getDefault()` が使われ、環境依存の障害になる。(`component/libraries/libraries-message.json:s5`)
- `messages.properties`（デフォルトロケール用）が存在しない場合はエラーになる。(`component/libraries/libraries-message.json:s5`)
- メッセージタグでの国際化対応を使うと**画面レイアウトが崩れる可能性**がある。許容できる場合のみ使用すること。(`processing-pattern/web-application/web-application-feature_details.json:s12`)
- JSP用カスタムタグライブラリではコード名称の言語指定取得はできない。(`component/libraries/libraries-code.json:s3`)

参照: component/libraries/libraries-message.json:s5, component/libraries/libraries-code.json:s3, component/handlers/handlers-thread_context_handler.json:s7, processing-pattern/web-application/web-application-feature_details.json:s12