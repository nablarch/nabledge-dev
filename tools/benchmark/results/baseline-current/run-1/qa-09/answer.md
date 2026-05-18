**結論**: Nablarch には業務日付管理機能があり、OS日時（システム日時）とは独立した業務日付をデータベースで管理・取得できます。締め処理での日付更新も API で実現できます。

**根拠**:

業務日付はデータベース上のテーブルで管理されます。テーブル構造は以下の通りです。

| カラム | 説明 |
|--------|------|
| 区分（PK） | 業務日付を識別する文字列（例: `00`, `batch` など） |
| 日付 | `yyyyMMdd` 形式の文字列 |

**設定（コンポーネント定義）**:

```xml
<component name="businessDateProvider" class="nablarch.core.date.BasicBusinessDateProvider">
  <property name="tableName" value="BUSINESS_DATE" />
  <property name="segmentColumnName" value="SEGMENT"/>
  <property name="dateColumnName" value="BIZ_DATE"/>
  <!-- 区分を省略した場合に使用されるデフォルト区分 -->
  <property name="defaultSegment" value="00"/>
  <property name="transactionManager" ref="transactionManager" />
</component>
```

`BasicApplicationInitializer` の `initializeList` への登録も必要です。

**業務日付の取得**:

```java
// BusinessDateUtil を使用
String bizDate = BusinessDateUtil.getDate(); // デフォルト区分
String bizDate = BusinessDateUtil.getDate("batch"); // 区分指定
```

**締め処理での業務日付更新**:

```java
BusinessDateProvider provider = SystemRepository.get("businessDateProvider");
provider.setDate(segment, date); // 区分と新しい日付を指定して更新
```

**OS日時（システム日時）の取得**（並行して使用可能）:

```java
// SystemTimeUtil を使用（OS日時）
Date sysTime = SystemTimeUtil.getDate();
```

**注意点**:
- 業務日付管理機能を使用する場合は `nablarch-common-jdbc` モジュールが追加で必要です
- バッチ障害時の再実行で特定区分の業務日付を上書きしたい場合は、システムプロパティで指定できます（`-DBasicBusinessDateProvider.batch=20160317`）
- 複数の締め区分（例: 日次・月次）を管理したい場合は、区分（segment）を複数定義することで対応できます

参照: `libraries-date.json#s7`, `libraries-date.json#s8`, `libraries-date.json#s10`, `libraries-date.json#s2`