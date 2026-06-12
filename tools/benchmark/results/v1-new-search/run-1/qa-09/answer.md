十分な情報が得られました。Step 5〜8を実行します。

---

**結論**: Nablarchの日付管理機能を使うことで、OS日時（`SystemTimeUtil`）と業務日付（`BusinessDateUtil`）を独立して管理できます。業務日付はデータベーステーブルで管理され、締め処理での業務日付更新も`BasicBusinessDateProvider.setDate()`で行えます。

**根拠**:

### 1. 業務日付管理の設定

業務日付はデータベースのテーブルで管理します。テーブルレイアウト：

| カラム | 内容 |
|--------|------|
| 区分(PK) | 業務日付を識別する文字列（例：`"00"`, `"batch"`） |
| 日付 | 業務日付（yyyyMMdd形式の文字列） |

コンポーネント定義：

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
      <component-ref name="businessDateProvider" />
    </list>
  </property>
</component>
```

また、OS日時を使うシステム日時管理の設定：

```xml
<component name="systemTimeProvider" class="nablarch.core.date.BasicSystemTimeProvider" />
```

### 2. 取得方法

- **OS日時（システム日時）の取得**：`SystemTimeUtil` を使用
- **業務日付の取得**：`BusinessDateUtil` を使用

### 3. 締め処理での業務日付更新

締め処理で業務日付を翌営業日に進める際は、`BasicBusinessDateProvider.setDate()` を使用します：

```java
// システムリポジトリからBasicBusinessDateProviderを取得する
BusinessDateProvider provider = SystemRepository.get("businessDateProvider");

// setDateメソッドを呼び出し、更新する
provider.setDate(segment, date);
```

### 4. 特定プロセスのみ業務日付を上書く（バッチ再実行等）

バッチ障害時の再実行で過去日付を使いたい場合、システムプロパティで上書きできます：

```
-DBasicBusinessDateProvider.batch=20160317
```

**注意点**:
- 業務日付管理機能を使用する場合、`nablarch-common-jdbc` モジュールの依存関係追加が必要です
- `BasicBusinessDateProvider` は初期化が必要なため、`initializer` の `initializeList` に設定すること
- 「区分」を使うことで複数の業務日付を同一テーブルで管理できます（例：本番業務用・バッチ用を分けるなど）

参照: libraries-date.json:s5, libraries-date.json:s6, libraries-date.json:s7, libraries-date.json:s8, libraries-date.json:s9, libraries-date.json:s10

---