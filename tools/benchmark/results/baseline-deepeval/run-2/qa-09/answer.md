Step 5-7: 回答を生成し、検証します。

---

**結論**: Nablarchの日付管理機能を使用すると、OS日時（`SystemTimeUtil`）と業務日付（`BusinessDateUtil`）を独立して管理・取得できます。業務日付はデータベースで管理し、複数の「区分」ごとに異なる業務日付を保持できます。

**根拠**:

### 業務日付の設定（コンポーネント定義）

業務日付はデータベーステーブルで管理します。テーブルレイアウトは以下のとおりです：

| カラム | 内容 |
|--------|------|
| 区分（PK） | 業務日付を識別する文字列（例：`00`、`batch` など） |
| 日付 | 業務日付（文字列、yyyyMMdd形式） |

コンポーネント定義に `BasicBusinessDateProvider` を追加します：

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

また、OS日時（システム日時）を使う場合は別途以下を設定します：

```xml
<component name="systemTimeProvider" class="nablarch.core.date.BasicSystemTimeProvider" />
```

### コードでの取得

- **OS日時**：`SystemTimeUtil` を使用して取得
- **業務日付**：`BusinessDateUtil` を使用して取得

### 業務日付の更新（締め処理など）

締め処理で業務日付を進める場合は `BasicBusinessDateProvider` の `setDate` メソッドを使います：

```java
// システムリポジトリからBasicBusinessDateProviderを取得する
BusinessDateProvider provider = SystemRepository.get("businessDateProvider");

// setDateメソッドを呼び出し、更新する
provider.setDate(segment, date);
```

### 特定プロセスだけ業務日付を上書く場合

バッチ再実行時など、特定プロセスのみ過去日付を使いたい場合はシステムプロパティで上書きできます：

```
-DBasicBusinessDateProvider.batch=20160317
```

**注意点**:
- `BasicBusinessDateProvider` は初期化対象リストへの登録が必要です（登録漏れに注意）。
- 業務日付テーブルの「区分」が複数ある場合、`defaultSegment` で指定した区分が区分省略時のデフォルトになります。
- ウェブアプリケーションのように単一プロセスの場合、日付を全体で切り替えるにはデータベースの日付値を直接更新すれば済みます。

参照: libraries-date.json:s5, libraries-date.json:s6, libraries-date.json:s7, libraries-date.json:s8, libraries-date.json:s9, libraries-date.json:s10

---