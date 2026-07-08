**結論**: `BeanUtil.getProperty(bean, propertyName)` でプロパティ名を指定してプロパティ値を取得できます。値はgetter経由で取得され、戻り値は `Object` 型にキャストが必要です。

**根拠**:

```java
// Bean定義例
public class User {
    private Long id;
    private String name;
    // getter & setter 省略
}

final User user = new User();
user.setId(1L);
user.setName("名前");

// プロパティ名を指定して値を取得する（1が取得できる）
// 値はgetter経由で取得される
final Long id = (Long) BeanUtil.getProperty(user, "id");
```

型変換が必要な場合は第3引数に変換先の型を指定できます。

```java
// 型変換して取得する場合
Object idAsString = BeanUtil.getProperty(user, "id", String.class);
```

**注意点**:
- `propertyName` にはbeanのトップレベル要素のみ指定可能です。`nestedBean.nestedStringProp` のようなネストしたプロパティ指定は動作しません。ネストしたプロパティにアクセスするには、`BeanUtil.getProperty(user.getAddress(), "postNo")` のように先にネストオブジェクトを取得してから呼び出してください。
- 指定したプロパティが定義されていない場合は `BeansException` がスローされます。
- レコードクラスに対しては `getProperty` での読み取りは可能ですが、`setProperty` や `copy` でレコードを変更対象として渡すと実行時例外が発生します。

参照:
- BeanUtil
  .claude/skills/nabledge-6/docs/component/libraries/libraries-bean-util.md
  使用方法
  BeanUtilでレコードを使用する
- class BeanUtil
  .claude/skills/nabledge-6/docs/javadoc/javadoc-nablarch-core-beans-BeanUtil.md
  getProperty