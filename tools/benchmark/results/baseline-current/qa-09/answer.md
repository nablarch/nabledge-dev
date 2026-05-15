**結論**: Nablarchには業務日付管理機能があり、OS日時（システム日時）とは独立してDBで業務日付を管理できます。月次締め処理での業務日付更新も `BasicBusinessDateProvider.setDate()` で実現できます。

**根拠**:

**1. 業務日付の設定（コンポーネント定義）**

業務日付はDBテーブルで管理します。テーブルのレイアウト：

| カラム | 内容 |
|---|---|
| 区分（PK） | 業務日付を識別する文字列（例：`"00"`, `"batch"` など） |
| 日付 | yyyyMMdd形式の文字列 |

コンポーネント定義（`component-configuration.xml`）：

```xml
<component name="businessDateProvider" class="nablarch.core.date.BasicBusinessDateProvider">
  <property name="tableName" value="BUSINESS_DATE" />
  <property name="segmentColumnName" value="SEGMENT"/>
  <property name="dateColumnName" value="BIZ_DATE"/>
  <!-- 区分省略時に使われるデフォルト区分 -->
  <property name="defaultSegment" value="00"/>
  <property name="transactionManager" ref="transactionManager" />
</component>

<!-- 初期化リストへの追加が必要 -->
<component name="initializer"
    class="nablarch.core.repository.initialization.BasicApplicationInitializer">
  <property name="initializeList">
    <list>
      <component-ref name="businessDateProvider" />
    </list>
  </property>
</component>
```

**2. 業務日付の取得**

```java
// BusinessDateUtil で取得（DBの業務日付を返す）
String bizDate = BusinessDateUtil.getDate();

// OS日時は SystemTimeUtil で別途取得
Date sysTime = SystemTimeUtil.getDate();
```

**3. 月次締め処理での業務日付更新**

締め処理の締め後に業務日付を翌月初日へ進める例：

```java
BusinessDateProvider provider = SystemRepository.get("businessDateProvider");
// 区分 "monthly" の業務日付を更新
provider.setDate("monthly", "20260601");
```

**4. Maven依存関係**

```xml
<!-- 業務日付管理機能を使用する場合のみ追加 -->
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-common-jdbc</artifactId>
</dependency>
```

**注意点**:
- `BasicBusinessDateProvider` は初期化が必要（`initializeList` への登録を忘れないこと）
- 区分（segment）を使うことで、複数の業務日付（例：処理日付、基準日付など）を同一テーブルで管理できる
- バッチ障害時の再実行で過去日付を使いたい場合は、JVMシステムプロパティで上書きが可能：`-DBasicBusinessDateProvider.batch=20260317`（DBを変更せず特定プロセスだけ別日付で実行できる）
- `setDate()` はDB更新を行うため、トランザクション管理に注意

参照: `component/libraries/libraries-date.json#s7`, `component/libraries/libraries-date.json#s8`, `component/libraries/libraries-date.json#s10`, `component/libraries/libraries-date.json#s2`