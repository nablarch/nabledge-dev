**結論**: `BeanUtil.getProperty(bean, "プロパティ名")` を呼び出すことで、指定したBeanのプロパティ値をgetter経由で取得できます。プロパティ名にはトップレベル要素のみ指定可能で、ドット区切りのネスト指定（例: `"nestedBean.nestedProp"`）は動作しません。

**根拠**:

基本的な使い方：

```java
public class User {
    private Long id;
    private String name;
    private Address address;
    // getter & setterは省略
}

final User user = new User();
user.setId(1L);
user.setName("名前");

// プロパティ名を指定して値を取得する（1が取得できる）
// 値はgetter経由で取得される
final Long id = (Long) BeanUtil.getProperty(user, "id");
```

型変換して取得したい場合は第3引数に型を指定：

```java
// 指定した型に変換して取得する
Object value = BeanUtil.getProperty(user, "id", String.class);
```

ネストしたBeanのプロパティを取得する場合は、ネストしたBeanのオブジェクトを直接渡す：

```java
public class Address {
    private String postNo;
    // getter & setterは省略
}

// 問題のないコード: ネストBeanを直接渡す
String postNo = (String) BeanUtil.getProperty(user.getAddress(), "postNo");

// 以下のコードは動作しない（ドット区切り指定は不可）
// String postNo = (String) BeanUtil.getProperty(user, "address.postNo");
```

レコード（Java 16+）も同様に `getProperty` で取得できます。ただし、レコードは不変であるため `setProperty` や `copy` でレコードを変更対象に渡すと実行時例外が発生します。

**注意点**:
- `propertyName` に対応するプロパティが存在しない場合は `BeansException` がスローされます
- ドット区切りのネストプロパティ指定（例: `"nestedBean.nestedProp"`）は `getProperty` では動作しません。ネストBeanのプロパティを取得するには、そのネストBeanオブジェクトを直接 `bean` 引数に渡してください

参照: component/libraries/libraries-bean-util.json:s2, javadoc/javadoc-nablarch-core-beans-BeanUtil.json:s14, javadoc/javadoc-nablarch-core-beans-BeanUtil.json:s15