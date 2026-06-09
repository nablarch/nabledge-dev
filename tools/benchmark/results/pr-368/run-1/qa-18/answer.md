**結論**: `BeanUtil.getProperty(bean, "propertyName")` を呼び出すことで、指定したBeanのプロパティ値をgetter経由で取得できる。型変換が必要な場合は第3引数に変換先の型を指定する。

**根拠**:

```java
// Bean定義例
public class User {
    private Long id;
    private String name;
    private Address address;
    // getter & setter は省略
}

// プロパティ名を指定して値を取得する（getter経由で取得される）
final Long id = (Long) BeanUtil.getProperty(user, "id");
```

型変換が必要な場合は以下のオーバーロードを使用する:

```java
// 型を指定して取得（ConversionUtilで型変換される）
Object value = BeanUtil.getProperty(user, "id", String.class);
```

**注意点**:

- `propertyName` には **トップレベルのプロパティ名のみ** 指定可能。ネストしたプロパティ（例: `"address.postNo"`）は動作しない。ネストしたプロパティにアクセスする場合は `BeanUtil.getProperty(user.getAddress(), "postNo")` のように呼び出しを分けること。
- 指定したプロパティが存在しない場合は `BeansException` がスローされる。
- 戻り値は `Object` 型のため、適切にキャストが必要。

参照: libraries-bean-util.json:s2, javadoc-nablarch-core-beans-BeanUtil.json:s14, javadoc-nablarch-core-beans-BeanUtil.json:s15