**結論**: `BeanUtil.getProperty(bean, "プロパティ名")` を呼び出すことで、Bean のプロパティ値を getter 経由で取得できます。戻り値は `Object` 型なので、必要に応じてキャストします。

**根拠**:

`BeanUtil.getProperty` の基本的な使い方：

```java
final User user = new User();
user.setId(1L);
user.setName("名前");

// プロパティ名を指定して値を取得する（1が取得できる）
// 値はgetter経由で取得される。
final Long id = (Long) BeanUtil.getProperty(user, "id");
```

型変換して取得したい場合は、第3引数に型を指定します：

```java
public static Object getProperty(Object bean, String propertyName, Class<?> type)
```

**注意点**:
- `propertyName` にはトップレベルのプロパティ名のみ指定可能です。`"nestedBean.nestedStringProp"` のようなネストした指定は動作しません。ネストしたプロパティを取得する場合は、先に親オブジェクトを取得してから再度 `getProperty` を呼んでください。

  ```java
  // これは動作しない
  BeanUtil.getProperty(sampleBean, "nestedBean.nestedStringProp");
  
  // こう書く
  BeanUtil.getProperty(sampleBean.getNestedBean(), "nestedStringProp");
  ```

- 指定したプロパティが定義されていない場合は `BeansException` がスローされます。
- `BeanUtil.getProperty` はレコードクラスにも対応しています。

参照: `libraries-bean-util.json:s2`, `javadoc-nablarch-core-beans-BeanUtil.json:s14`