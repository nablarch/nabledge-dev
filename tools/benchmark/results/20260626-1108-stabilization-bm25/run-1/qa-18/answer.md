**結論**: `BeanUtil.getProperty(bean, "propertyName")` を呼び出すことで、Bean またはレコードのトップレベルプロパティ値を `Object` 型で取得できます。型変換が必要な場合は、第3引数に変換先の型クラスを指定する `getProperty(bean, propertyName, type)` を使用します。

**根拠**:

```java
// 基本的な使い方（Object型で取得）
String stringProp = BeanUtil.getProperty(sampleBean, "stringProp");

// 型を指定して取得する場合
String value = (String) BeanUtil.getProperty(sampleBean, "intProp", String.class);
```

ネストしたBeanのプロパティを取得する場合は、ネストしたBeanオブジェクト自体を直接 `bean` 引数に渡します:

```java
// 正しい方法
String nestedValue = BeanUtil.getProperty(sampleBean.nestedBean, "nestedStringProp");

// 以下のコードは動作しない（ドット区切りは使用不可）
// String nestedValue = BeanUtil.getProperty(sampleBean, "nestedBean.nestedStringProp");
```

`getProperty` のシグネチャ（2種類）:

```java
public static Object getProperty(Object bean, String propertyName)
public static Object getProperty(Object bean, String propertyName, Class<?> type)
```

**注意点**:
- `propertyName` にはトップレベル要素のみ指定可能。ドット区切り（例: `"nestedBean.nestedStringProp"`）は動作しない。ネストされたプロパティにアクセスするには、ネストされたBeanオブジェクト自体を `bean` 引数に渡す必要がある。
- 指定したプロパティが存在しない場合は `BeansException` がスローされる。

参照: javadoc-nablarch-core-beans-BeanUtil.json:s14, javadoc-nablarch-core-beans-BeanUtil.json:s15