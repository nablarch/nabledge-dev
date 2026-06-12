必要なセクション内容が揃いました。Step 5でアンサーを生成します。

---

**結論**: NablarchはOS日時とは別に「業務日付」をデータベースで管理する専用機能（`BasicBusinessDateProvider`）を提供しており、`BusinessDateUtil.getDate()` で業務日付、`SystemTimeUtil.getDate()` でOS日時をそれぞれ独立して取得できます。

**検証（Step 6）**: セクション内容との照合を行います。すべての主張はs5〜s10およびJavadocに直接記載されています。verify_result = PASS。

---

**結論**: NablarchはOS日時とは独立した「業務日付」をデータベースで管理する機能を標準提供しており、締め処理でシステム日時と業務日付を分けて管理できます。取得にはそれぞれ専用のユーティリティクラスを使います。

**根拠**:

NablarchはOS日時（`SystemTimeUtil`）と業務日付（`BusinessDateUtil`）を別々に管理する機能を持っています。

**業務日付のデータベーステーブル構成**

| カラム | 型・内容 |
|---|---|
| 区分(PK) | 業務日付を識別する文字列 |
| 日付 | yyyyMMdd形式の文字列 |

区分を使うことで、例えばオンラインとバッチで別の業務日付を管理することもできます。

**設定（コンポーネント定義）**

```xml
<!-- OS日時 -->
<component name="systemTimeProvider" class="nablarch.core.date.BasicSystemTimeProvider" />

<!-- 業務日付（DBで管理） -->
<component name="businessDateProvider" class="nablarch.core.date.BasicBusinessDateProvider">
  <property name="tableName" value="BUSINESS_DATE" />
  <property name="segmentColumnName" value="SEGMENT"/>
  <property name="dateColumnName" value="BIZ_DATE"/>
  <property name="defaultSegment" value="00"/>
  <property name="transactionManager" ref="transactionManager" />
</component>

<component name="initializer"
    class="nablarch.core.repository.initialization.BasicApplicationInitializer">
  <property name="initializeList">
    <list>
      <component-ref name="businessDateProvider" />
    </list>
  </property>
</component>
```

**取得**

```java
// OS日時を取得
Date systemDate = SystemTimeUtil.getDate();
LocalDateTime systemDateTime = SystemTimeUtil.getLocalDateTime();

// 業務日付を取得（デフォルト区分）
String bizDate = BusinessDateUtil.getDate(); // yyyyMMdd形式

// 区分を指定して業務日付を取得（例：バッチ用）
String batchBizDate = BusinessDateUtil.getDate("batch");
```

**業務日付の更新（締め処理）**

```java
BusinessDateProvider provider = SystemRepository.get("businessDateProvider");
provider.setDate(segment, date); // yyyyMMdd形式
```

**注意点**: 
- `BasicBusinessDateProvider` は初期化対象のリスト（`initializer`）への設定が必要です。
- バッチ処理で障害時の再実行など、特定プロセスのみ業務日付を上書きしたい場合は、JVMオプションで指定できます：`-DBasicBusinessDateProvider.batch=20160317`

参照: libraries-date.json:s5, libraries-date.json:s6, libraries-date.json:s7, libraries-date.json:s8, libraries-date.json:s9, libraries-date.json:s10, javadoc/javadoc-nablarch-core-date-BusinessDateUtil.json:s6, javadoc/javadoc-nablarch-core-date-BusinessDateUtil.json:s7, javadoc/javadoc-nablarch-core-date-SystemTimeUtil.json:s9

---