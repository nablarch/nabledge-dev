**結論**: `BeanUtil.getProperty(bean, "propertyName")` を呼び出すことで、指定したプロパティの値を getter 経由で `Object` 型として取得できます。型変換が必要な場合は第3引数に変換先の型を指定します。

**根拠**:

```java
final User user = new User();
user.setId(1L);
user.setName("名前");

// プロパティ名を指定して値を取得する(1が取得できる)。
// 値はgetter経由で取得される。
final Long id = (Long) BeanUtil.getProperty(user, "id");
```

型変換して取得したい場合は、第3引数に変換先の型を指定します。

```java
// Object ではなく String 型で取得したい場合
Object value = BeanUtil.getProperty(bean, "propertyName", String.class);
```

メソッドシグネチャ:

```java
// 型変換なし
public static Object getProperty(Object bean, String propertyName)

// 型変換あり
public static Object getProperty(Object bean, String propertyName, Class<?> type)
```

**注意点**:
- `propertyName` にはトップレベルのプロパティ名のみ指定可能です。ネストしたプロパティ（`"nestedBean.nestedStringProp"` のようなドット区切り）は**動作しません**。ネストしたBeanのプロパティを取得する場合は、まずネストしたBeanを取得してからそのプロパティを指定してください。
- 指定したプロパティが存在しない場合は `BeansException` がスローされます。
- レコード（Java 16以降）に対しても使用可能です。ただし、レコードに対して `setProperty` や `copy` で値を変更しようとすると実行時例外が発生します（レコードはイミュータブルなため）。

参照:
- BeanUtil
  .claude/skills/nabledge-6/docs/component/libraries/libraries-bean-util.md
  使用方法
  BeanUtilでレコードを使用する
- class BeanUtil
  .claude/skills/nabledge-6/docs/javadoc/javadoc-nablarch-core-beans-BeanUtil.md
  getProperty