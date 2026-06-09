**結論**: NablarchはOS日時（システム日時）とは独立した業務日付管理機能を提供しており、`BusinessDateUtil`で業務日付を取得できます。業務日付はデータベースのテーブルで管理され、締め処理後に`BasicBusinessDateProvider.setDate()`で更新します。

---

**根拠**:

まず、業務日付管理のテーブルをDBに用意します。テーブルには2カラムが必要です：

| カラム | 内容 |
|---|---|
| 区分 (PK) | 業務日付を識別する文字列（例: `"00"`、`"batch"`） |
| 日付 | 業務日付。文字列型、yyyyMMdd形式 |

次に、コンポーネント定義で`BasicBusinessDateProvider`を登録します：

```xml
<component name="businessDateProvider" class="nablarch.core.date.BasicBusinessDateProvider">
  <!-- テーブル名 -->
  <property name="tableName" value="BUSINESS_DATE" />
  <!-- 区分のカラム名 -->
  <property name="segmentColumnName" value="SEGMENT"/>
  <!-- 日付のカラム名 -->
  <property name="dateColumnName" value="BIZ_DATE"/>
  <!-- 区分を省略した場合に使用されるデフォルト区分 -->
  <property name="defaultSegment" value="00"/>
  <!-- データベースアクセスに使用するトランザクションマネージャ -->
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

システム日時（OS日時）と業務日付はそれぞれ別のユーティリティで取得します：
- **業務日付**: `BusinessDateUtil`を使用
- **OS日時（システム日時）**: `SystemTimeUtil`を使用

締め処理後に業務日付を翌日へ進める場合、以下のように更新します：

```java
// システムリポジトリからBasicBusinessDateProviderを取得する
BusinessDateProvider provider = SystemRepository.get("businessDateProvider");

// setDateメソッドを呼び出し、更新する
provider.setDate(segment, date); // dateはyyyyMMdd形式の文字列
```

---

**注意点**:

- `basicBusinessDateProvider`の初期化を`BasicApplicationInitializer`の`initializeList`に追加する必要があります。これを忘れると起動時にエラーになります。
- バッチ再実行時に特定プロセスのみ業務日付を上書きしたい場合（障害時の再実行など）は、システムプロパティで指定できます：
  ```
  -DBasicBusinessDateProvider.batch=20160317
  ```
  ウェブアプリケーションのように全機能が1プロセス内で動く場合は、DBの日付を直接変更すればよいです。
- 業務日付管理機能を使用する場合は、`nablarch-common-jdbc`への依存を追加する必要があります（`nablarch-core`だけでは不足）。

参照: libraries-date.json:s7, libraries-date.json:s8, libraries-date.json:s9, libraries-date.json:s10, libraries-date.json:s5, libraries-date.json:s6