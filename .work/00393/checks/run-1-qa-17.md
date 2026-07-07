# qa-17 — run-1

## 質問

SystemRepository から登録済みコンポーネントを取得する方法を教えてください

## 回答

**結論**: `SystemRepository.get("コンポーネント名")` を使用して、XMLのコンポーネント設定ファイルに定義したコンポーネントを取得できます。

**根拠**:

コンポーネント定義（XMLファイル）:
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
// SystemRepository#getを使用して取得する。
SampleComponent sample = SystemRepository.get("sampleComponent");

// ネストしたcomponentは、親の名前と自身の名前を"."で連結し取得する。
Component2 component2 = SystemRepository.get("component.component2");
```

`SystemRepository.get()` の引数には、XMLの `component` 要素の `name` 属性に設定した値を指定します。

**注意点**:
- 取得できるのはシングルトンのオブジェクトです。取得するたびに新しいインスタンスが生成されるわけではありません。
- システムリポジトリには事前にDIコンテナの情報が設定されている必要がありますが、Nablarchが提供する `ServletContextListener` 実装クラスや独立型アプリケーションの起動クラスが自動的に行うため、通常は個別実装不要です。
- ネストして定義したコンポーネントも、リポジトリ上はグローバル領域に保持されるため、`"親名.子名"` の形式で取得できます。

参照: libraries-repository.json:s25, libraries-repository.json:s24

## 参照ナレッジ

- [システムリポジトリからオブジェクトを取得する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-repository.md#システムリポジトリからオブジェクトを取得する) (s25)
- [DIコンテナの情報をシステムリポジトリに設定する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-repository.md#diコンテナの情報をシステムリポジトリに設定する) (s24)
- [Java Beansオブジェクトを設定する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-repository.md#java-beansオブジェクトを設定する) (s7)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 0.10 | NG | The Expected Output specifically states that get(String name) uses type parameters to retrieve components from the repository in a type-safe manner. The Actual Output provides extensive information about using SystemRepository.get() with XML configuration, nested components, and usage examples, but does not mention or address the key fact about type parameters being used for type-safe retrieval. The core expected fact about type safety via type parameters is completely absent from the Actual Output. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is perfectly relevant to the question about how to retrieve registered components from SystemRepository, with no irrelevant statements found. Great job staying right on topic! |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | — | — |
| answer_relevancy | — | — |
| faithfulness | — | — |

### 参照事実（expected_facts）

- get(String name)で型パラメータを利用してリポジトリからコンポーネントを型安全に取得する
