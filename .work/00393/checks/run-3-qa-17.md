# qa-17 — run-3

## 質問

SystemRepository から登録済みコンポーネントを取得する方法を教えてください

## 回答

**結論**: `SystemRepository.get("コンポーネント名")` を呼び出すことで、コンポーネント設定ファイル(xml)に登録済みのコンポーネントを取得できます。コンポーネントが見つからない場合は `null` が返ります。

**根拠**:

コンポーネント設定ファイルでの定義例:

```xml
<component name="sampleComponent" class="sample.SampleComponent" />

<component name="component" class="sample.Component" >
  <property name="component2">
    <component name="component2" class="sample.Component2" />
  </property>
</component>
```

取得例:

```java
// SystemRepository#get を使用して取得する
SampleComponent sample = SystemRepository.get("sampleComponent");

// ネストしたコンポーネントは、親の名前と自身の名前を "." で連結して取得する
Component2 component2 = SystemRepository.get("component.component2");
```

`SystemRepository.get` のシグネチャ:

```java
public static <T> T get(String name) throws ClassCastException
```

- 引数: コンポーネント名（xml の `name` 属性に設定した値）
- 戻り値: 登録されたコンポーネント。見つからない場合は `null`
- 例外: 型引数 `<T>` と登録されたコンポーネントの型が一致しない場合に `ClassCastException`

**注意点**:
- `SystemRepository.get` を呼び出す前に、DIコンテナの情報がシステムリポジトリに設定されている必要があります。この設定はNablarchが提供する `ServletContextListener` の実装クラスや独立型アプリケーションの起動クラスによって自動的に行われるため、通常は個別に実装する必要はありません。
- 取得されるインスタンスはシングルトンです（リクエストごとに新しいインスタンスが生成されるわけではありません）。

参照: libraries-repository.json:s25, libraries-repository.json:s24, javadoc-nablarch-core-repository-SystemRepository.json:s11

## 参照ナレッジ

- [システムリポジトリからオブジェクトを取得する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-repository.md#システムリポジトリからオブジェクトを取得する) (s25)
- [DIコンテナの情報をシステムリポジトリに設定する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-repository.md#diコンテナの情報をシステムリポジトリに設定する) (s24)
- [get](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/javadoc/javadoc-nablarch-core-repository-SystemRepository.md#get) (s11)
- [getObject](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/javadoc/javadoc-nablarch-core-repository-SystemRepository.md#getobject) (s8)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 0.50 | NG | The Expected Output focuses on one specific fact: that get(String name) uses a type parameter to retrieve components from the repository in a type-safe manner. The Actual Output does mention the get(String name) signature with a generic type parameter <T> and mentions ClassCastException when types don't match, which implicitly covers type safety. However, the Actual Output does not explicitly state that the method is 'type-safe' or emphasize the type parameter as the mechanism for type-safe retrieval as the Expected Output specifically highlights. The core fact about type-safe retrieval via type parameter is partially conveyed but not explicitly stated as the main point. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is perfectly relevant to the question about how to retrieve registered components from SystemRepository, with no irrelevant statements found. Great job staying right on topic! |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | NG | 参照事実「get(String name)で型パラメータを利用してリポジトリからコンポーネントを型安全に取得する」について、回答はシグネチャ `public static <T> T get(String name)` を示し ClassCastException の説明も記述しているが、「型パラメータを利用した型安全な取得」という核心の事実が明示的に述べられていない（シグネチャのメタ情報として掲示されているにとどまり、これが型安全取得の主要な仕組みであるとは記述されていない） |
| answer_relevancy | — | —
| faithfulness | — | —

### 参照事実（expected_facts）

- get(String name)で型パラメータを利用してリポジトリからコンポーネントを型安全に取得する
