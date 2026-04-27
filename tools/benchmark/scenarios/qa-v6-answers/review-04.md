**質問**: ユーザーが入力する画面項目のチェックをどう書くのが Nablarch 流？ 必須・桁数・形式チェックをなるべく楽に書きたい。

---

**結論**: Nablarch は Jakarta Bean Validation と Nablarch 独自バリデーションの2系統を提供しているが、**Bean Validation の使用を推奨**。ウェブアプリケーションでは `BeanValidationStrategy` をコンポーネント名 `validationStrategy` として登録し、フォームクラスにアノテーション（`@Required`, `@Length`, `@SystemChar`, `@Domain` など）を付けて使う。 — `component/libraries/libraries-validation.json#s1`

**① 推奨機能**
Bean Validation を推奨する理由は、(1) Jakarta EE で仕様が定められており情報が豊富、(2) Nablarch 独自のバリデーションの使い方を覚える必要がない、の2点。 — `component/libraries/libraries-validation.json#s1`

**② ウェブアプリケーションでの有効化**
`BeanValidationStrategy` をコンポーネント名 `validationStrategy` として登録する:

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```
— `component/libraries/libraries-bean_validation.json#s13`

**③ ウェブアプリケーション側の位置づけ**
ウェブアプリケーションの基本的な入力値チェックは、Bean Validation とエラーメッセージの画面表示機能から成る。 — `processing-pattern/web-application/web-application-feature_details.json#s2`

**④ バリデーションルールの書き方**
アノテーションは Field または getter に設定する（setter 不可）。フォームのプロパティは全て `String` で定義する（Bean 変換失敗による予期せぬ例外を避けるため）。個別アノテーションより **ドメインバリデーション** を推奨。

```java
public class SampleForm {
  @Length(max = 10)
  @SystemChar(charsetDef = "全角文字")
  @Required
  private String userName;

  @Length(min = 8, max = 8)
  @SystemChar(charsetDef = "半角数字")
  private String birthday;
}
```
— `component/libraries/libraries-bean_validation.json#s5`

**注意点**
- 相関バリデーション（複数項目の組合せチェック）は `@AssertTrue` を使う。Bean Validation は実行順序が保証されないため、項目単体のバリデーションが未実行でも例外にならないよう実装する。任意項目の未入力時は `true` を返してスキップすること。 — `component/libraries/libraries-bean_validation.json#s1`
