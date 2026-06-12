**結論**: `BeanUtil.getProperty(bean, "プロパティ名")` を呼び出すと、指定したプロパティの値を getter 経由で `Object` 型として取得できます。型変換が必要な場合は第3引数に変換先の型を渡す3引数オーバーロードを使います。

**根拠**:

**基本的な使い方**（値を `Object` 型で取得）:

```java
final User user = new User();
user.setId(1L);
user.setName("名前");

// プロパティ名を指定して値を取得する(1が取得できる)。
// 値はgetter経由で取得される。
final Long id = (Long) BeanUtil.getProperty(user, "id");
```

**型変換して取得する場合**（第3引数に変換先の型を指定）:

```java
public static Object getProperty(Object bean, String propertyName, Class<?> type)
```

`ConversionUtil` による型変換が行われ、指定型に変換された値を返します。`type` に `null` を指定すると変換なしでそのまま返します。

**注意点**:
- `propertyName` にはトップレベルのプロパティ名のみ指定可能です。ドット区切りのネストアクセス（例: `"nestedBean.nestedStringProp"`）は**動作しません**。ネストしたプロパティを取得したい場合は、中間オブジェクトを取得してから再度 `getProperty` を呼ぶ必要があります。
  ```java
  // 動作しない
  String nestedStringProp = BeanUtil.getProperty(sampleBean, "nestedBean.nestedStringProp");

  // 正しい方法
  String nestedStringProp = BeanUtil.getProperty(sampleBean.getNestedBean(), "nestedStringProp");
  ```
- 指定したプロパティ名がBean に定義されていない場合は `BeansException` がスローされます。

参照: libraries-bean-util.json:s2, javadoc-nablarch-core-beans-BeanUtil.json:s14, javadoc-nablarch-core-beans-BeanUtil.json:s15