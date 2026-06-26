**結論**: NablarchはOS日時（システム日時）と業務日付を独立して管理する機能を提供しています。業務日付の取得には `BusinessDateUtil`、OS日時の取得には `SystemTimeUtil` を使い、それぞれ別のコンポーネントで管理します。

**根拠**:

Nablarchの日付管理機能では、コンポーネント定義で指定するクラスを差し替えるだけで取得方法を切り替えられます。

**1. 業務日付の設定（DBで管理）**

業務日付はデータベースのテーブルで管理します。テーブルは「区分（PK）」と「日付（yyyyMMdd形式）」の2カラム構成で、複数の区分（例: 締め処理ごとに異なる業務日付）を管理できます。

```xml
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

**2. システム日時の設定（OS日時）**

```xml
<component name="systemTimeProvider" class="nablarch.core.date.BasicSystemTimeProvider" />
```

**3. アプリケーションコードからの取得**

- 業務日付: `BusinessDateUtil` を使用
- システム日時(OS日時): `SystemTimeUtil` を使用

**4. 業務日付の更新（締め処理後の日付更新）**

```java
// SystemRepositoryからBasicBusinessDateProviderを取得する
BusinessDateProvider provider = SystemRepository.get("businessDateProvider");

// setDateメソッドを呼び出し、更新する（区分ごとに更新可能）
provider.setDate(segment, date);
```

**5. バッチ再実行時の業務日付上書き**

バッチ処理の再実行時など、特定プロセスのみ業務日付を変更したい場合はシステムプロパティで上書きできます。

```
-DBasicBusinessDateProvider.batch=20160317
```

**注意点**:
- 業務日付管理機能を使用するには `nablarch-common-jdbc` モジュールが追加で必要です。
- `BasicBusinessDateProvider` は初期化対象リスト（`initializeList`）への登録が必要です。忘れると起動時にエラーになります。
- 業務日付は `defaultSegment` で指定した区分がデフォルトで使用されます。締め処理ごとに異なる業務日付を管理する場合は区分値を明示的に指定して取得・更新してください。

参照: `libraries-date.json:s2`, `libraries-date.json:s3`, `libraries-date.json:s5`, `libraries-date.json:s6`, `libraries-date.json:s7`, `libraries-date.json:s8`, `libraries-date.json:s9`, `libraries-date.json:s10`