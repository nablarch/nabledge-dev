# qa-09 — run-3

## 質問

OS日時ではなく業務上の日付を取得する方法はあるか？締め処理でシステム日時と業務日付を分けて管理したい

## 回答

**結論**: Nablarchの「日付管理」機能を使用することで、OS日時とは独立した業務日付をデータベースで管理し、`BusinessDateUtil`で取得できます。締め処理など用途別に区分を分けて複数の業務日付を管理することも可能です。

**根拠**:

**1. 業務日付テーブルの設定**

業務日付はデータベーステーブルで管理します。`BasicBusinessDateProvider`をコンポーネント定義に追加し、初期化リストにも登録します。

```xml
<component name="businessDateProvider" class="nablarch.core.date.BasicBusinessDateProvider">
  <!-- テーブル名 -->
  <property name="tableName" value="BUSINESS_DATE" />
  <!-- 区分のカラム名 -->
  <property name="segmentColumnName" value="SEGMENT"/>
  <!-- 日付のカラム名 -->
  <property name="dateColumnName" value="BIZ_DATE"/>
  <!-- 区分を省略して業務日付を取得した場合に使用される区分 -->
  <property name="defaultSegment" value="00"/>
  <!-- データベースアクセスに使用するトランザクションマネージャ -->
  <property name="transactionManager" ref="transactionManager" />
</component>

<component name="initializer"
    class="nablarch.core.repository.initialization.BasicApplicationInitializer">
  <property name="initializeList">
    <list>
      <!-- 他のコンポーネントは省略 -->
      <component-ref name="businessDateProvider" />
    </list>
  </property>
</component>
```

テーブルのレイアウト:
| カラム | 説明 |
|---|---|
| 区分(PK) | 業務日付を識別するための値（文字列型） |
| 日付 | 業務日付（文字列型、yyyyMMdd形式） |

**2. 業務日付の取得**

`BusinessDateUtil`を使用して取得します。区分を指定することで、オンライン処理用・バッチ処理用など用途別の業務日付を取り分けられます。

```java
// デフォルト区分で取得
String date = BusinessDateUtil.getDate();

// 区分を指定して取得（例：締め処理用の区分）
String closingDate = BusinessDateUtil.getDate("closing");
```

**3. 締め処理での業務日付更新**

締め処理で翌営業日に業務日付を進める場合は、`BasicBusinessDateProvider`の`setDate`メソッドを使用します。

```java
// システムリポジトリからBasicBusinessDateProviderを取得する
BusinessDateProvider provider = SystemRepository.get("businessDateProvider");

// setDateメソッドを呼び出し、更新する
provider.setDate(segment, date);
```

**4. バッチ再実行時の日付上書き**

障害時の再実行など、特定プロセスのみ過去日付で業務処理を行いたい場合は、システムプロパティで上書きできます。

```
# 区分"batch"の日付を2016/03/17に上書きする場合
java -DBasicBusinessDateProvider.batch=20160317 Main
```

**注意点**:
- `BasicBusinessDateProvider`は初期化が必要なため、`initializeList`への登録を忘れないこと
- `cacheEnabled`プロパティはデフォルトでtrueとなっており、`ThreadContext`がクリアされるまでキャッシュされる。リクエスト単位でキャッシュが更新されるため、オンライン処理では通常問題ない
- `setDate`で区分または日付がnullや空文字、`yyyyMMdd`形式でない場合は`IllegalArgumentException`がスローされる

参照: libraries-date.json:s7, libraries-date.json:s8, libraries-date.json:s9, libraries-date.json:s10, javadoc-nablarch-core-date-BusinessDateUtil.json, javadoc-nablarch-core-date-BasicBusinessDateProvider.json

## 参照ナレッジ

- [業務日付管理機能を使うための設定](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-date.md#業務日付管理機能を使うための設定) (s7)
- [業務日付を取得する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-date.md#業務日付を取得する) (s8)
- [業務日付を任意の日付に上書く](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-date.md#業務日付を任意の日付に上書く) (s9)
- [業務日付を更新する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-date.md#業務日付を更新する) (s10)
- [システム日時(OS日時)と業務日付の切り替えができる](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-date.md#システム日時os日時と業務日付の切り替えができる) (s2)
- [システム日時の管理機能を使うための設定](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-date.md#システム日時の管理機能を使うための設定) (s5)
- [システム日時を取得する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-date.md#システム日時を取得する) (s6)
- [getDate](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/javadoc/javadoc-nablarch-core-date-BusinessDateUtil.md#getdate) (s6)
- [getDate](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/javadoc/javadoc-nablarch-core-date-BusinessDateUtil.md#getdate) (s7)
- [setDate](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/javadoc/javadoc-nablarch-core-date-BasicBusinessDateProvider.md#setdate) (s29)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output fully covers both key facts from the Expected Output checklist: (1) it explicitly mentions using BusinessDateUtil to retrieve business dates with code examples showing BusinessDateUtil.getDate(), and (2) it explains that the business date management feature uses a database to manage multiple business dates and requires BasicBusinessDateProvider configuration, including detailed XML configuration examples. Both expected facts are thoroughly addressed. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is perfectly relevant, directly addressing the question about obtaining business dates separately from OS datetime and managing them distinctly during closing processes. No irrelevant statements were found! |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「BusinessDateUtilを使用して業務日付を取得する」は回答の「`BusinessDateUtil.getDate()`」コード例に含まれており、「業務日付管理機能はデータベースで複数の業務日付を管理し、BasicBusinessDateProviderの設定が必要」は回答の「業務日付はデータベーステーブルで管理します。`BasicBusinessDateProvider`をコンポーネント定義に追加し」および詳細なXML設定例に含まれている |
| answer_relevancy | — | —
| faithfulness | — | —

### 参照事実（expected_facts）

- BusinessDateUtilを使用して業務日付を取得する
- 業務日付管理機能はデータベースで複数の業務日付を管理し、BasicBusinessDateProviderの設定が必要
