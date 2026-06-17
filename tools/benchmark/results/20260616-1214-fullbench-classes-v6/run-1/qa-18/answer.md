**結論**: `BeanUtil.getProperty(bean, propertyName)` を呼び出すことで、Beanのプロパティ値をgetter経由で取得できます。戻り値は `Object` 型なので、必要に応じてキャストして使用します。

**根拠**:

```java
final User user = new User();
user.setId(1L);
user.setName("名前");

// プロパティ名を指定して値を取得する(1が取得できる)
// 値はgetter経由で取得される
final Long id = (Long) BeanUtil.getProperty(user, "id");
```

型変換が必要な場合は、第3引数に変換先の型を指定する3引数バージョンも使用できます:

```java
public static Object getProperty(Object bean, String propertyName, Class<?> type)
```

**注意点**:
- `propertyName` にはBeanの**トップレベル要素のみ**指定可能です。ネストしたプロパティを `"nestedBean.nestedStringProp"` 形式で指定しても動作しません。ネストしたBeanのプロパティを取得する場合は、まずネストしたBeanオブジェクトを取得してから `getProperty` を呼び出してください。
- 指定した `propertyName` に対応するプロパティが存在しない場合は `BeansException` がスローされます。

参照: component/libraries/libraries-bean-util.json:s2, javadoc/javadoc-nablarch-core-beans-BeanUtil.json:s14, javadoc/javadoc-nablarch-core-beans-BeanUtil.json:s15