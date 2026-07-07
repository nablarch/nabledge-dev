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
| answer_relevancy | NG | 「参照: `libraries-bean-util.json:s2`, `javadoc-nablarch-core-beans-BeanUtil.json:s14`」など内部参照記法がユーザー向け回答に含まれており不適切 |
| faithfulness | OK | ナレッジ内容と矛盾なし（getter経由取得・ネスト指定不可・BeansException・レコード対応はすべてjavadoc s14およびlibraries-bean-util.md s2の記述と一致） |

### 参照事実（expected_facts）

- getProperty(Object bean, String propertyName)でJavaBeansオブジェクトまたはレコードから指定したプロパティの値を取得する
