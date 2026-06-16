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