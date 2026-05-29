Step 4: 対象セクションを `read-sections.sh` で取得しました。セクション選定：

- `s12`: **high** — DBとの相関バリデーションをBean Validationで行うことへの明示的な指針（質問への直接回答）
- `s17`: **partial** — RESTfulウェブサービスでのBean Validation使用方法
- `s24`: **partial** — カスタムバリデータの追加方法の参照先
- `s11`: **partial** — 相関バリデーションの実装パターン（背景理解）

read_sections: `component/libraries/libraries-bean-validation.json:s12`, `component/libraries/libraries-bean-validation.json:s17`, `component/libraries/libraries-bean-validation.json:s24`, `component/libraries/libraries-bean-validation.json:s11`

Step 5 → 7: 回答生成・検証を行います。

---

**結論**: Bean Validationのカスタムバリデータ内でDB検索する実装は**採用しないこと**。データベースとの重複チェックは、Bean Validationによるバリデーション完了後に**業務アクション側で実装**する。

**根拠**:

Nablarchのドキュメント（`libraries-bean-validation.json:s12`）に以下の理由が明記されている：

> Bean Validationを使ってデータベースに対する相関バリデーションを実施した場合、バリデーション実施前の安全ではない値を使ってデータベースアクセスを行うことになる。（Bean Validation実行中のオブジェクトの値は、安全である保証がない。）これは、SQLインジェクションなどの脆弱性の原因となるため、さけるべき実装であるため。

正しい実装フローは以下のとおり：

```
1. JaxRsBeanValidationHandler が Bean Validation を実行（@Valid アノテーション）
   ↓ バリデーションOK（安全な値であることが保証される）
2. 業務アクション側でDB検索による重複チェックを実施
   ↓ バリデーション済みの安全な値を使ってDB照会
3. 重複ありの場合は ApplicationException をスローして業務エラーとする
```

RESTfulウェブサービスでは、リソースクラスのメソッドに `@Valid` アノテーションを設定することでBean Validationを起動する：

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    // ここに到達した時点でBean Validationは完了済み
    // → DBの重複チェックを安全に実施できる
    if (UniversalDao.exists(Person.class, ...)) {
        throw new ApplicationException(...);
    }
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

**注意点**:

- カスタムバリデータ（`ConstraintValidator` の実装）でDB検索することは**技術的には可能**だが、バリデーション前の未検証値でSQLを実行することになりSQLインジェクションのリスクがある
- Nablarchの設計方針として「バリデーションとDBアクセスの実行タイミングを分離する」ことが明確に求められている

参照: `libraries-bean-validation.json:s12`, `libraries-bean-validation.json:s17`

---