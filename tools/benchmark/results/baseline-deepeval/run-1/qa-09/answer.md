セクション内容を確認しました。Step 5〜7を実行して回答を生成します。

---

**結論**: Nablarchには「日付管理」機能があり、OS日時は `SystemTimeUtil`、業務日付は `BusinessDateUtil` で独立して取得できます。業務日付はDBテーブルで管理し、締め処理では `BasicBusinessDateProvider.setDate()` で更新します。

**根拠**:

**1. コンポーネント定義の設定**

システム日時と業務日付、それぞれのProviderをコンポーネント定義に追加します。

```xml
<!-- システム日時 -->
<component name="systemTimeProvider" class="nablarch.core.date.BasicSystemTimeProvider" />

<!-- 業務日付（DBテーブルで管理） -->
<component name="businessDateProvider" class="nablarch.core.date.BasicBusinessDateProvider">
  <property name="tableName" value="BUSINESS_DATE" />
  <property name="segmentColumnName" value="SEGMENT"/>
  <property name="dateColumnName" value="BIZ_DATE"/>
  <!-- 区分省略時のデフォルト値 -->
  <property name="defaultSegment" value="00"/>
  <property name="transactionManager" ref="transactionManager" />
</component>

<!-- 初期化対象に追加 -->
<component name="initializer" class="nablarch.core.repository.initialization.BasicApplicationInitializer">
  <property name="initializeList">
    <list>
      <component-ref name="businessDateProvider" />
    </list>
  </property>
</component>
```

業務日付テーブルのレイアウト:

| カラム | 説明 |
|--------|------|
| 区分（PK） | 業務日付を識別する文字列 |
| 日付 | yyyyMMdd形式の文字列 |

**2. 日時・日付の取得**

```java
// OS日時の取得
SystemTimeUtil.getSystemDateTime();

// 業務日付の取得（区分省略でデフォルト区分を使用）
BusinessDateUtil.getDate();
```

**3. 締め処理での業務日付の更新**

```java
// SystemRepositoryからProviderを取得して更新
BusinessDateProvider provider = SystemRepository.get("businessDateProvider");
provider.setDate(segment, date);
```

**4. 依存モジュール（pom.xml）**

```xml
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-core</artifactId>
</dependency>
<!-- 業務日付管理機能を使用する場合のみ -->
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-common-jdbc</artifactId>
</dependency>
```

**注意点**:
- `区分（segment）` を使うと複数の業務日付を独立して管理できます（例: バッチ用とWeb用で別区分）。
- バッチの障害再実行時は、DBを変更せずにシステムプロパティで業務日付を上書きできます。  
  例: `-DBasicBusinessDateProvider.batch=20160317`（区分が"batch"の場合）
- Webアプリケーションのように全機能が1プロセスで動く場合は、DBの日付を直接更新するだけで足ります。

参照: `libraries-date.json:s5`, `libraries-date.json:s6`, `libraries-date.json:s7`, `libraries-date.json:s8`, `libraries-date.json:s9`, `libraries-date.json:s10`, `libraries-date.json:s3`

---