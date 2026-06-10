**結論**: `BeanUtil.getProperty(bean, propertyName)` を呼び出すことで、JavaBeansオブジェクトまたはレコードの指定プロパティ値を取得できます。型変換も必要な場合は3引数版 `getProperty(bean, propertyName, type)` を使用します。

**根拠**:

基本的な使い方：

```java
// BeanからStringプロパティを取得
String stringProp = BeanUtil.getProperty(sampleBean, "stringProp");
```

型変換が必要な場合：

```java
// プロパティ値をInteger型に変換して取得
Integer intVal = BeanUtil.getProperty(sampleBean, "numProp", Integer.class);
// typeにnullを渡すと変換なし（Object型で返る）
Object value = BeanUtil.getProperty(sampleBean, "someProp", null);
```

ネストしたBeanのプロパティを取得する場合：

```java
// NG: ドット区切りのネストした指定は動作しない
String nestedStringProp = BeanUtil.getProperty(sampleBean, "nestedBean.nestedStringProp"); // ← 動作しない

// OK: 対象Beanを直接指定する
String nestedStringProp = BeanUtil.getProperty(sampleBean.nestedBean, "nestedStringProp");
```

**注意点**:
- `propertyName` にはトップレベルのプロパティ名のみ指定可能。`"nestedBean.nestedStringProp"` のようなドット区切りのネストした指定は動作しない。
- 指定したプロパティ名が存在しない場合、`BeansException` がスローされる。
- レコードクラスにも対応している。

参照: javadoc/javadoc-nablarch-core-beans-BeanUtil.json:s14, javadoc/javadoc-nablarch-core-beans-BeanUtil.json:s15