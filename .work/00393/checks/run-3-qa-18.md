# qa-18 — run-3

## 質問

BeanUtil の getProperty で Bean のプロパティ値を取得する方法を教えてください

## 回答

**結論**: `BeanUtil.getProperty(bean, "propertyName")` を呼び出すことで、Bean のプロパティ値を getter 経由で取得できます。戻り値は `Object` 型なので、必要に応じてキャストが必要です。

**根拠**:

```java
// サンプルBean定義
public class User {
    private Long id;
    private String name;
    private Date birthDay;
    private Address address;
    // getter & setterは省略
}

// BeanUtil.getPropertyの使用例
final User user = new User();
user.setId(1L);
user.setName("名前");

// プロパティ名を指定して値を取得する（1が取得できる）
// 値はgetter経由で取得される
final Long id = (Long) BeanUtil.getProperty(user, "id");
```

型変換付きで取得したい場合は、第3引数に変換先の型を指定します:

```java
// getProperty(Object bean, String propertyName, Class<?> type)
// 型変換してプロパティ値を取得する
public static Object getProperty(Object bean, String propertyName, Class<?> type)
```

**注意点**:
- `propertyName` にはトップレベル要素のみ指定可能です。ネストプロパティ（例: `"nestedBean.nestedStringProp"`）は動作しません
- 対応するプロパティが定義されていない場合は `BeansException` がスローされます
- `BeanUtil.setProperty` や `BeanUtil.copy` の引数にレコードを渡した場合は実行時例外が発生するため注意してください

参照: libraries-bean-util.json:s2、javadoc-nablarch-core-beans-BeanUtil.json:s14、javadoc-nablarch-core-beans-BeanUtil.json:s15

## 参照ナレッジ

- [使用方法](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-util.md#使用方法) (s2)
- [getProperty](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/javadoc/javadoc-nablarch-core-beans-BeanUtil.md#getproperty) (s14)
- [getProperty](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/javadoc/javadoc-nablarch-core-beans-BeanUtil.md#getproperty) (s15)
- [モジュール一覧](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-util.md#モジュール一覧) (s1)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 0.60 | NG | The Actual Output covers the core fact from the Expected Output: using BeanUtil.getProperty(bean, propertyName) to retrieve a property value from a JavaBeans object. However, the Expected Output specifically mentions that the method works with both 'JavaBeansオブジェクト' and 'レコード（record）', while the Actual Output actually states that passing a record to BeanUtil methods causes a runtime exception — which contradicts the expected fact about record support. The main concept is covered but with a notable discrepancy regarding record support. |
| answer_relevancy | 0.95 | 0.88 | NG | The score is 0.88 because the response mostly addresses how to use BeanUtil.getProperty to retrieve Bean property values as asked, but contains an irrelevant statement about BeanUtil.setProperty and BeanUtil.copy with records, which is unrelated to the input question. Removing that irrelevant portion would bring the score closer to a perfect 1.0. |
| faithfulness | 0.99 | 0.89 | NG | The score is 0.89 because the actual output incorrectly claims that passing a record to BeanUtil.setProperty() or BeanUtil.copy() causes a runtime exception, whereas the retrieval context states that these methods support both JavaBeans objects and records using getter/setter methods, with no mention of any such runtime exception. |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | NG | 参照事実「getProperty(Object bean, String propertyName)でJavaBeansオブジェクトまたはレコードから指定したプロパティの値を取得する」のうち「レコードからも取得可能」という点が回答に含まれていない。回答はBeanのプロパティ取得のみ説明し、getPropertyがレコードにも対応していることを言及していない |
| answer_relevancy | NG | 回答の注意点セクションに「BeanUtil.setProperty や BeanUtil.copy の引数にレコードを渡した場合は実行時例外が発生する」という記述が含まれているが、質問は getProperty の使用方法についてであり、setProperty や copy メソッドの挙動は質問と無関係な情報である。 |
| faithfulness | OK | 回答にある「BeanUtil.setProperty や BeanUtil.copy の引数にレコードを渡した場合は実行時例外が発生する」という記述は、libraries-bean-util.md の「BeanUtilでレコードを使用する」セクションに「BeanUtil.setProperty や BeanUtil.copy といったメソッドの引数に、変更対象のオブジェクトとしてレコードを渡した場合は実行時例外が発生する」と明記されており、ナレッジの内容と一致している。DeepEvalの faithfulness NG 判定は誤りで、ナレッジとの矛盾はない。 |

### 参照事実（expected_facts）

- getProperty(Object bean, String propertyName)でJavaBeansオブジェクトまたはレコードから指定したプロパティの値を取得する
