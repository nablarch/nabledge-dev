**質問**: 画面で選択する性別や種別が、マスタ上で定義されている有効な値かチェックしたい。マスタ管理の仕組みと入力チェックを連携できる？

---

**結論**: Nablarch のコード管理機能と Bean Validation を `@CodeValue` アノテーションで連携できる。`@CodeValue(codeId = "GENDER")` を入力フィールドに付与すれば、コード管理に登録された有効なコード値かどうかを入力チェックで自動検証できる。パターンを使って選択肢を絞る場合は `pattern` 属性でパターン名を指定する。 — `component/libraries/libraries-code.json#s6`

**① アノテーションの使い方（Bean Validation）**
`nablarch.common.code.validator.ee.CodeValue` をフィールドに付与する。

```java
@CodeValue(codeId = "GENDER")
private String gender;
```

Nablarch Validation を使う場合は `nablarch.common.code.validator.CodeValue` を setter に付与する。 — `component/libraries/libraries-code.json#s6`

**② パターンによる有効値制限**
パターン（コード値を絞り込む分類）を使っている場合、バリデーションでも同じパターン内の有効値かをチェックする必要がある。`pattern` 属性にパターン名を指定する:

```java
@CodeValue(codeId = "GENDER", pattern = "PATTERN2")
private String gender;
```
— `component/libraries/libraries-code.json#s6`

**③ ドメインバリデーションとの関係**
ドメインバリデーションを使う場合、1つのドメインに対して1つのパターンしか指定できない。複数パターンに対応するにはパターンごとにドメインを定義する必要がある（バリデーションで必要なドメインのみ定義すればよい）:

```java
public class SampleDomainBean {
  @CodeValue(codeId = "FLOW_STATUS", pattern = "PATTERN1")
  String flowStatusGeneral;

  @CodeValue(codeId = "FLOW_STATUS", pattern = "PATTERN2")
  String flowStatusGuest;
}
```
— `component/libraries/libraries-code.json#s6`

**注意点**
- Bean Validation のフォームプロパティはすべて `String` で定義する（Bean 変換失敗による予期せぬ例外を避けるため）。 — `component/libraries/libraries-bean_validation.json#s5`
