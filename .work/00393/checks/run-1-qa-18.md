# qa-18 — run-1

## 質問

BeanUtil の getProperty で Bean のプロパティ値を取得する方法を教えてください

## 回答

**結論**: `BeanUtil.getProperty(bean, propertyName)` を呼び出すことで、Beanのプロパティ値をgetter経由で取得できます。戻り値は `Object` 型なので、必要に応じてキャストして使用します。

**根拠**:

```java
final User user = new User();
user.setId(1L);
user.setName("名前");

// プロパティ名を指定して値を取得する(1が取得できる)
// 値はgetter経由で取得される
final Long id = (Long) BeanUtil.getProperty(user, "id");
```

型変換が必要な場合は、第3引数に変換先の型を指定する3引数バージョンも使用できます:

```java
public static Object getProperty(Object bean, String propertyName, Class<?> type)
```

**注意点**:
- `propertyName` にはBeanの**トップレベル要素のみ**指定可能です。ネストしたプロパティを `"nestedBean.nestedStringProp"` 形式で指定しても動作しません。ネストしたBeanのプロパティを取得する場合は、まずネストしたBeanオブジェクトを取得してから `getProperty` を呼び出してください。
- 指定した `propertyName` に対応するプロパティが存在しない場合は `BeansException` がスローされます。

参照: component/libraries/libraries-bean-util.json:s2, javadoc/javadoc-nablarch-core-beans-BeanUtil.json:s14, javadoc/javadoc-nablarch-core-beans-BeanUtil.json:s15

## 参照ナレッジ

- [使用方法](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-util.md#使用方法) (s2)
- [getProperty](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/javadoc/javadoc-nablarch-core-beans-BeanUtil.md#getproperty) (s14)
- [getProperty](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/javadoc/javadoc-nablarch-core-beans-BeanUtil.md#getproperty) (s15)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 0.80 | NG | The Actual Output clearly covers the expected fact: it explains that `BeanUtil.getProperty(bean, propertyName)` is used to retrieve the value of a specified property from a JavaBeans object, which aligns with the Expected Output's claim. The actual output provides the method signature, code examples, and additional details about usage and limitations, all of which support or extend the core expected fact. The only minor gap is that the Expected Output explicitly mentions 'records' (レコード) as a supported type alongside JavaBeans objects, which is not mentioned in the Actual Output. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is perfectly relevant to the question about how to retrieve Bean property values using BeanUtil's getProperty. No irrelevant statements were found - great job staying focused and on topic! |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | NG | 参照事実「getProperty(Object bean, String propertyName)でJavaBeansオブジェクトまたはレコードから指定したプロパティの値を取得する」のうち「レコード」への対応が回答に含まれていない。回答は「Beanのプロパティ値をgetter経由で取得」とのみ記述しており、レコードのサポートについて言及がない |
| answer_relevancy | — | —
| faithfulness | — | —

### 参照事実（expected_facts）

- getProperty(Object bean, String propertyName)でJavaBeansオブジェクトまたはレコードから指定したプロパティの値を取得する
