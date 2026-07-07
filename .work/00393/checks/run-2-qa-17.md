# qa-17 — run-2

## 質問

SystemRepository から登録済みコンポーネントを取得する方法を教えてください

## 回答

**結論**: `SystemRepository.get("コンポーネント名")` を使用して、コンポーネント設定ファイル（XML）に登録されたコンポーネントを取得できます。

**根拠**:

コンポーネント設定ファイルで `name` 属性を付けて定義したコンポーネントを、`SystemRepository.get()` で名前を指定して取得します。

コンポーネント定義（XML）:
```xml
<component name="sampleComponent" class="sample.SampleComponent" />

<component name="component" class="sample.Component" >
  <property name="component2">
    <component name="component2" class="sample.Component2" />
  </property>
</component>
```

取得例（Java）:
```java
// SystemRepository#getを使用して取得する。
SampleComponent sample = SystemRepository.get("sampleComponent");

// ネストしたcomponentは、親の名前と自身の名前を"."で連結し取得する。
Component2 component2 = SystemRepository.get("component.component2");
```

`SystemRepository.get(String name)` の仕様：
- 型パラメータ `<T>` で返却型を指定する
- コンポーネントが見つからなかった場合は `null` を返す
- 型引数 `<T>` がリポジトリに登録されたコンポーネントの型と一致しない場合は `ClassCastException` がスローされる

文字列設定値を取得する場合は `SystemRepository.getString(String name)`、真偽値は `SystemRepository.getBoolean(String name)` も使用できます。

**注意点**:
- システムリポジトリには事前にDIコンテナの情報が設定されている必要があります（通常はNablarchが提供するServletContextListenerや起動クラスが実施するため、個別実装は不要）。
- DIコンテナで管理されるインスタンスはシングルトンです。プロトタイプと勘違いしてリクエスト固有のデータをコンポーネントに保持すると、複数ユーザー間でデータが混在する重大な不具合が発生します。スレッドセーフな設計が必要です。

参照: `libraries-repository.json:s25`, `javadoc-nablarch-core-repository-SystemRepository.json:s11`

## 参照ナレッジ

- [システムリポジトリからオブジェクトを取得する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-repository.md#システムリポジトリからオブジェクトを取得する) (s25)
- [DIコンテナの情報をシステムリポジトリに設定する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-repository.md#diコンテナの情報をシステムリポジトリに設定する) (s24)
- [Java Beansオブジェクトを設定する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-repository.md#java-beansオブジェクトを設定する) (s7)
- [get](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/javadoc/javadoc-nablarch-core-repository-SystemRepository.md#get) (s11)
- [getString](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/javadoc/javadoc-nablarch-core-repository-SystemRepository.md#getstring) (s9)
- [getBoolean](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/javadoc/javadoc-nablarch-core-repository-SystemRepository.md#getboolean) (s10)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 0.70 | NG | The Expected Output focuses on a single fact: that `get(String name)` uses type parameters to retrieve components from the repository in a type-safe manner. The Actual Output does cover this fact, mentioning that the type parameter `<T>` specifies the return type and that a `ClassCastException` is thrown if the type argument doesn't match. However, the Actual Output goes far beyond this single fact with extensive additional information about XML configuration, nested components, and other methods. The core fact about type-safe retrieval via type parameters is present but somewhat buried in the broader response. |
| answer_relevancy | 0.95 | 0.77 | NG | The score is 0.77 because the actual output contains some irrelevant information: mentions of SystemRepository being a singleton, cautions about request-specific data retention, and the necessity of thread-safe design — none of which directly address the question of how to retrieve registered components from SystemRepository. These tangential details lower the score, though the response still covers the core retrieval method sufficiently to warrant a reasonable score. |
| faithfulness | 0.99 | 0.92 | NG | The score is 0.92 because the actual output overgeneralizes thread-safety requirements, claiming that ALL instances managed by the DI container must be thread-safe by design, when the retrieval context specifically states that only components whose state is intentionally changed or shared across the entire application need to be thread-safe. |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「get(String name)で型パラメータを利用してリポジトリからコンポーネントを型安全に取得する」は回答の「型パラメータ `<T>` で返却型を指定する」「型引数 `<T>` がリポジトリに登録されたコンポーネントの型と一致しない場合は `ClassCastException` がスローされる」に含まれている |
| answer_relevancy | NG | 回答末尾に「参照: `libraries-repository.json:s25`, `javadoc-nablarch-core-repository-SystemRepository.json:s11`」という内部参照記法がユーザー向け回答に含まれており不適切 |
| faithfulness | NG | 回答の「スレッドセーフな設計が必要です」はナレッジ（libraries-repository.md s7）の記述「意図的にアプリケーション全体でコンポーネントの状態を変更、共有する場合は、そのコンポーネントはスレッドセーフでなければならない」と矛盾する（ナレッジは条件付きだが、回答は無条件の要件として述べている） |

### 参照事実（expected_facts）

- get(String name)で型パラメータを利用してリポジトリからコンポーネントを型安全に取得する
