**結論**: `BeanUtil.getProperty(bean, propertyName)` を使用して、Beanの任意のプロパティ値をgetter経由で取得できます。戻り値は `Object` 型なので、必要に応じてキャストします。

**根拠**:

```java
// Bean定義
public class User {
    private Long id;
    private String name;
    private Address address;
    // getter & setter は省略
}

// プロパティ名を指定して値を取得する（値はgetter経由で取得される）
final Long id = (Long) BeanUtil.getProperty(user, "id");
```

型変換が必要な場合は、第3引数に変換先の型を指定できます:

```java
// String型に変換して取得する
String id = (String) BeanUtil.getProperty(user, "id", String.class);
```

シグネチャ（Javadoc より）:

```java
public static Object getProperty(Object bean, String propertyName)
public static Object getProperty(Object bean, String propertyName, Class<?> type)
```

**注意点**:

- `propertyName` にはBeanの**トップレベルのプロパティ名のみ**指定可能です。`"address.postNo"` のようなネストした指定は動作しません。
- ネストしたBeanのプロパティを取得する場合は、対象Beanを直接渡してください:

```java
// NG: ネストしたプロパティ名は指定できない
String postNo = (String) BeanUtil.getProperty(user, "address.postNo"); // 動作しない

// OK: 対象のネストBeanを直接渡す
String postNo = (String) BeanUtil.getProperty(user.getAddress(), "postNo");
```

- 指定した `propertyName` に対応するプロパティが存在しない場合は `BeansException` がスローされます。
- レコードに対しても同様に使用できますが、レコードはイミュータブルなため `setProperty` や `copy` の引数に変更対象として渡すと実行時例外が発生します。

参照:
- BeanUtil
  .claude/skills/nabledge-6/docs/component/libraries/libraries-bean-util.md
  使用方法
  BeanUtilでレコードを使用する
- class BeanUtil
  .claude/skills/nabledge-6/docs/javadoc/javadoc-nablarch-core-beans-BeanUtil.md
  getProperty