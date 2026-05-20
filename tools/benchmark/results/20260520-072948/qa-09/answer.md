**結論**: Nablarchの「業務日付管理機能」を使うことで、OS日時とは独立した業務日付をデータベースで管理・取得できます。`BusinessDateUtil` で取得し、`BasicBusinessDateProvider.setDate()` で更新（締め処理後の日付繰り越し等）が可能です。

**根拠**:

業務日付はDBテーブルで管理されます。テーブルレイアウトは次のとおりです。

| カラム | 説明 |
|-------|------|
| 区分（PK） | 業務日付を識別する文字列（例: "00", "monthly" 等） |
| 日付 | yyyyMMdd形式の文字列 |

**1. コンポーネント定義の設定**

`BasicBusinessDateProvider` をコンポーネント名 `businessDateProvider` で登録し、初期化対象にも追加します。

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

**2. 業務日付の取得**

`BusinessDateUtil` を使って業務日付を取得します。

**3. 月次締め処理後に業務日付を更新する**

締め処理完了後、翌月の業務日付に更新するには次のように `setDate()` を呼び出します。

```java
// SystemRepositoryからBasicBusinessDateProviderを取得する
BusinessDateProvider provider = SystemRepository.get("businessDateProvider");

// 区分と新しい日付（yyyyMMdd形式）で更新する
provider.setDate(segment, date);
```

**注意点**:
- 区分（SEGMENT）を使うことで、複数の業務日付を独立して管理できます（例: 決済日付・会計日付を別区分で管理するなど）。
- バッチ再実行時に特定プロセスだけ過去日付を使いたい場合は、システムプロパティ `-DBasicBusinessDateProvider.<区分>=yyyyMMdd` で上書き可能です。
- モジュールとして `nablarch-common-jdbc` が追加で必要です。

参照: libraries-date.json:s7, libraries-date.json:s8, libraries-date.json:s10, libraries-date.json:s9