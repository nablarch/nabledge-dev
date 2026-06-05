セクション内容を読み込みました。Step 5〜8の回答生成と検証を行います。

---

**結論**: `BeanUtil.getProperty(bean, "プロパティ名")` を呼び出すことで、getter 経由でプロパティ値を取得できます。戻り値は `Object` 型なので、必要に応じてキャストします。

**根拠**:

```java
public class User {
    private Long id;
    private String name;
    private Address address;
    // getter & setter は省略
}

public class Address {
    private String postNo;
    // getter & setter は省略
}
```

```java
final User user = new User();
user.setId(1L);
user.setName("名前");

// プロパティ名を指定して値を取得する（1 が取得できる）。
// 値は getter 経由で取得される。
final Long id = (Long) BeanUtil.getProperty(user, "id");
```

ネストした Bean のプロパティは「.」区切りで指定できます：

```java
final Address address = new Address();
address.setPostNo("1234");
user.setAddress(address);

// address.postNo のように「.」で区切ってネストプロパティを指定する
final String postNo = (String) BeanUtil.getProperty(user, "address.postNo");
```

**注意点**:
- 戻り値は `Object` 型のため、利用する型へのキャストが必要です。
- Java 16 以降のレコード型も対象として使用できます。ただし、レコードに対して `BeanUtil.setProperty` や `BeanUtil.copy` を呼び出すと実行時例外が発生します（`getProperty` によるレコードからの読み取りは問題ありません）。
- `BeanUtil` は `List` 型の型パラメータに対応していません。`List<D>` のような総称型を持つ場合は、具象クラスで getter をオーバーライドする必要があります。

参照: `libraries-bean-util.json:s2`, `libraries-bean-util.json:s9`

---