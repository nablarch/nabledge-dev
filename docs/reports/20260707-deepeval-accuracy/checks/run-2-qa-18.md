# qa-18 — run-2

## 質問

BeanUtil の getProperty で Bean のプロパティ値を取得する方法を教えてください

## 回答

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

## 参照ナレッジ

- [使用方法](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-util.md#使用方法) (s2)
- [getProperty](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/javadoc/javadoc-nablarch-core-beans-BeanUtil.md#getproperty) (s14)
- [getProperty](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/javadoc/javadoc-nablarch-core-beans-BeanUtil.md#getproperty) (s15)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The actual output clearly covers the expected fact: it explains that BeanUtil.getProperty can retrieve a property value from a JavaBeans object by specifying the property name, and explicitly mentions that it also supports record classes. The method signature and usage are demonstrated with code examples, and the return mechanism via getter is explained. All key elements from the expected output (getProperty method, JavaBeans/record support, retrieving property values by name) are present in the actual output. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is perfectly relevant to the question about how to retrieve Bean property values using BeanUtil's getProperty. No irrelevant statements were found! |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「getProperty(Object bean, String propertyName)でJavaBeansオブジェクトまたはレコードから指定したプロパティの値を取得する」は回答の「`BeanUtil.getProperty(user, "id")` のコード例」および「BeanUtil.getProperty はレコードクラスにも対応しています」に含まれている |
| answer_relevancy | OK | 回答は「BeanUtilのgetPropertyでBeanのプロパティ値を取得する方法」という質問に直接答えており、基本的な使い方・型変換版・ネスト不可の注意点・例外・レコード対応はすべて質問に関連している。的外れな内容は含まれていない。 |
| faithfulness | OK | 回答の全内容がナレッジと一致している。getter経由での取得・戻り値Object型はlibraries-bean-util.mdのコード例と一致。トップレベルのみ指定可能でネストした指定が動作しない点・BeansExceptionがスローされる点・第3引数で型変換できる点はjavadoc-nablarch-core-beans-BeanUtil.mdのgetPropertyメソッド記述と一致。レコードクラスにも対応している点も「指定したJavaBeansオブジェクトもしくはレコードから」という記述と一致する。矛盾はない。 |

### 参照事実（expected_facts）

- getProperty(Object bean, String propertyName)でJavaBeansオブジェクトまたはレコードから指定したプロパティの値を取得する
