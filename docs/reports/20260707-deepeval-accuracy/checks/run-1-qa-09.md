# qa-09 — run-1

## 質問

OS日時ではなく業務上の日付を取得する方法はあるか？締め処理でシステム日時と業務日付を分けて管理したい

## 回答

**結論**: Nablarchの日付管理機能を使うことで、OS日時（システム日時）と業務日付を独立して管理できます。業務日付は `BusinessDateUtil.getDate()` で取得し、`BasicBusinessDateProvider` がDBテーブルで管理します。

**根拠**:

**1. システム日時の設定と取得**

コンポーネント定義に `BasicSystemTimeProvider` を登録します（コンポーネント名は `systemTimeProvider` と指定）：

```xml
<component name="systemTimeProvider" class="nablarch.core.date.BasicSystemTimeProvider" />
```

アプリケーションコードからは `SystemTimeUtil` で取得します：

```java
// java.util.Date で取得
Date sysDate = SystemTimeUtil.getDate();

// yyyyMMdd 形式の文字列で取得
String sysDateStr = SystemTimeUtil.getDateString();
```

**2. 業務日付の設定と取得**

業務日付はDBテーブル（区分＋日付の2カラム構成）で管理します。コンポーネント定義：

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
```

初期化対象リストへの追加も必要です。アプリケーションコードからは `BusinessDateUtil` で取得します：

```java
// デフォルト区分の業務日付を取得（yyyyMMdd形式の文字列）
String bizDate = BusinessDateUtil.getDate();

// 区分を指定して業務日付を取得（例: オンライン用とバッチ用で区分を分ける）
String batchBizDate = BusinessDateUtil.getDate("batch");
```

**3. 業務日付の更新（締め処理での使用）**

締め処理など、業務日付を翌日に進める場合は `BasicBusinessDateProvider.setDate()` を使います：

```java
// システムリポジトリからBasicBusinessDateProviderを取得する
BusinessDateProvider provider = SystemRepository.get("businessDateProvider");

// setDateメソッドを呼び出し、更新する
provider.setDate(segment, date);
```

**4. バッチのみ業務日付を上書く場合**

バッチ障害時の再実行など、特定プロセスだけ業務日付を変えたい場合はシステムプロパティで上書きできます：

```
# 区分 "batch" の業務日付を 2016/03/17 に上書く
-DBasicBusinessDateProvider.batch=20160317
```

**注意点**:
- `BasicBusinessDateProvider` は初期化対象のリスト（`initializer`）への登録が必要です。忘れると起動時にエラーになります。
- オンライン処理のように1プロセス内で完結する場合は、業務日付テーブルの値を直接変更するだけで済みます（システムプロパティ上書きはバッチの再実行など特殊ケース向け）。
- 業務日付はyyyyMMdd形式の文字列として管理されます。

参照: libraries-date.json:s5, libraries-date.json:s6, libraries-date.json:s7, libraries-date.json:s8, libraries-date.json:s9, libraries-date.json:s10, javadoc-nablarch-core-date-BusinessDateUtil.json:s6, javadoc-nablarch-core-date-BusinessDateUtil.json:s7, javadoc-nablarch-core-date-SystemTimeUtil.json:s9, javadoc-nablarch-core-date-SystemTimeUtil.json:s12

## 参照ナレッジ

- [システム日時の管理機能を使うための設定](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-date.md#システム日時の管理機能を使うための設定) (s5)
- [システム日時を取得する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-date.md#システム日時を取得する) (s6)
- [業務日付管理機能を使うための設定](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-date.md#業務日付管理機能を使うための設定) (s7)
- [業務日付を取得する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-date.md#業務日付を取得する) (s8)
- [業務日付を任意の日付に上書く](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-date.md#業務日付を任意の日付に上書く) (s9)
- [業務日付を更新する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-date.md#業務日付を更新する) (s10)
- [getDate](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/javadoc/javadoc-nablarch-core-date-BusinessDateUtil.md#getdate) (s6)
- [getDate](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/javadoc/javadoc-nablarch-core-date-BusinessDateUtil.md#getdate) (s7)
- [getDate](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/javadoc/javadoc-nablarch-core-date-SystemTimeUtil.md#getdate) (s9)
- [getDateString](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/javadoc/javadoc-nablarch-core-date-SystemTimeUtil.md#getdatestring) (s12)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The actual output covers both expected facts: (1) it explicitly shows BusinessDateUtil.getDate() usage for retrieving business dates, and (2) it explains that BasicBusinessDateProvider manages multiple business dates via a database table with segment+date column structure. Both key facts from the expected output are clearly addressed in the actual output. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is fully relevant to the question about obtaining business dates separately from OS datetime, and how to manage system datetime and business dates separately in closing processes. No irrelevant statements were detected! |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「BusinessDateUtilを使用して業務日付を取得する」は回答の `String bizDate = BusinessDateUtil.getDate();` に含まれている。参照事実「業務日付管理機能はデータベースで複数の業務日付を管理し、BasicBusinessDateProviderの設定が必要」は回答の「業務日付はDBテーブル（区分＋日付の2カラム構成）で管理します」および BasicBusinessDateProvider の XML 設定例に含まれている |
| answer_relevancy | OK | 回答は「OS日時と業務日付を分けて管理したい」という質問に直接答えており、システム日時（BasicSystemTimeProvider/SystemTimeUtil）と業務日付（BasicBusinessDateProvider/BusinessDateUtil）の設定・取得・更新・上書きをすべてカバーしている。的外れな内容は含まれていない。 |
| faithfulness | OK | 回答のXML設定・Javaコード・システムプロパティ形式はすべてnabledge-6/docs/component/libraries/libraries-date.mdの記述と一致している。BasicBusinessDateProviderのコンポーネント定義（tableName, segmentColumnName, dateColumnName, defaultSegment, transactionManager）、initializer登録必須、システムプロパティ形式（-DBasicBusinessDateProvider.batch=20160317）、setDate更新コードもナレッジの内容を正確に反映しており、矛盾は見当たらない。 |

### 参照事実（expected_facts）

- BusinessDateUtilを使用して業務日付を取得する
- 業務日付管理機能はデータベースで複数の業務日付を管理し、BasicBusinessDateProviderの設定が必要
