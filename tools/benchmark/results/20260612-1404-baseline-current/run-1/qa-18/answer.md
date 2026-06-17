**結論**: `BeanUtil.getProperty(bean, "propertyName")` を呼び出すと、指定したプロパティの値を getter 経由で `Object` 型として取得できます。型変換が必要な場合は第3引数に型を渡す `getProperty(bean, "propertyName", SomeClass.class)` を使います。

**根拠**:

```java
User user = new User();
user.setId(1L);
user.setName("名前");

// プロパティ名を指定して値を取得する（getter経由）
Long id = (Long) BeanUtil.getProperty(user, "id");

// 型変換しながら取得する場合（ConversionUtilが変換を行う）
String idAsString = (String) BeanUtil.getProperty(user, "id", String.class);
```

**ネストしたBeanのプロパティを取得する場合:**

```java
// NG: "nestedBean.nestedStringProp" は動作しない
BeanUtil.getProperty(sampleBean, "nestedBean.nestedStringProp");  // 動作しない

// OK: ネストオブジェクトを先に取り出してから呼び出す
BeanUtil.getProperty(sampleBean.getNestedBean(), "nestedStringProp");
```

`propertyName` には、対象 Bean の **トップレベルのプロパティ名のみ** 指定できます。「.」でつないだネストパスは非対応です。

**注意点**:
- 指定した `propertyName` に対応するプロパティが存在しない場合は `BeansException` がスローされます。
- レコードの場合も `getProperty` は利用できます。ただし、`setProperty` や `copy` でレコードを変更対象に渡すと実行時例外が発生します（レコードはイミュータブルなため）。

参照: libraries-bean-util.json:s2, javadoc-nablarch-core-beans-BeanUtil.json:s14, javadoc-nablarch-core-beans-BeanUtil.json:s15