**結論**: `BeanUtil.getProperty(bean, "propertyName")` を呼び出すことで、Bean のプロパティ値を getter 経由で取得できます。戻り値は `Object` 型なので、必要に応じてキャストが必要です。

**根拠**:

```java
// サンプルBean定義
public class User {
    private Long id;
    private String name;
    private Date birthDay;
    private Address address;
    // getter & setterは省略
}

// BeanUtil.getPropertyの使用例
final User user = new User();
user.setId(1L);
user.setName("名前");

// プロパティ名を指定して値を取得する（1が取得できる）
// 値はgetter経由で取得される
final Long id = (Long) BeanUtil.getProperty(user, "id");
```

型変換付きで取得したい場合は、第3引数に変換先の型を指定します:

```java
// getProperty(Object bean, String propertyName, Class<?> type)
// 型変換してプロパティ値を取得する
public static Object getProperty(Object bean, String propertyName, Class<?> type)
```

**注意点**:
- `propertyName` にはトップレベル要素のみ指定可能です。ネストプロパティ（例: `"nestedBean.nestedStringProp"`）は動作しません
- 対応するプロパティが定義されていない場合は `BeansException` がスローされます
- `BeanUtil.setProperty` や `BeanUtil.copy` の引数にレコードを渡した場合は実行時例外が発生するため注意してください

参照: libraries-bean-util.json:s2、javadoc-nablarch-core-beans-BeanUtil.json:s14、javadoc-nablarch-core-beans-BeanUtil.json:s15