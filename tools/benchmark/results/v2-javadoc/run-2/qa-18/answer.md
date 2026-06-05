全情報が揃いました。Step 5〜8の回答を生成します。

---

**結論**: `BeanUtil.getProperty(bean, "propertyName")` を呼び出すことで、BeanのプロパティをgettER経由で取得できます。戻り値は `Object` 型なので、必要に応じてキャストします。

**根拠**:

```java
final User user = new User();
user.setId(1L);
user.setName("名前");

// プロパティ名を指定して値を取得する(1が取得できる)。
// 値はgetter経由で取得される。
final Long id = (Long) BeanUtil.getProperty(user, "id");
```

型変換して取得したい場合は、第3引数に変換先の型を指定するオーバーロードが使えます。

```java
// 型変換して取得する
String idStr = (String) BeanUtil.getProperty(user, "id", String.class);
```

シグネチャ：

```java
// 型変換なし
public static Object getProperty(Object bean, String propertyName)

// 型変換あり
public static Object getProperty(Object bean, String propertyName, Class<?> type)
```

**注意点**:
- `propertyName` には **トップレベルのプロパティ名のみ** 指定可能です。ネストしたプロパティ（例: `"nestedBean.nestedStringProp"`）は動作しません。ネストしたBeanのプロパティにアクセスするには、`BeanUtil.getProperty(sampleBean.getNestedBean(), "nestedStringProp")` のように、先にネストしたBeanを取得してから呼び出してください。
- 指定したプロパティ名が存在しない場合は `BeansException` がスローされます。
- レコード（Java 16+）も JavaBeans と同様に扱えますが、レコードは不変なので `setProperty` や `copy` での変更対象としては使えません。

参照: `component/libraries/libraries-bean-util.json:s2`, `javadoc/javadoc-nablarch-core-beans-BeanUtil.json:s14`, `javadoc/javadoc-nablarch-core-beans-BeanUtil.json:s15`

---