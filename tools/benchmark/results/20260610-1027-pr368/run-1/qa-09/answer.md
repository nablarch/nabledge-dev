**結論**: NablarchはOS日時（システム日時）と業務日付を別々に管理する機能を提供しており、`SystemTimeUtil` でOS日時を、`BusinessDateUtil` で業務日付を取得できます。業務日付はデータベースで管理され、「区分」ごとに複数保持できるため、締め処理で日付を切り替える用途に対応しています。

**根拠**:

**1. システム日時（OS日時）の取得**

コンポーネント定義に `BasicSystemTimeProvider` を設定します。

```xml
<component name="systemTimeProvider" class="nablarch.core.date.BasicSystemTimeProvider" />
```

アプリケーションからは `SystemTimeUtil` を使って取得します。

---

**2. 業務日付の設定（DBテーブル管理）**

業務日付はDBテーブルで管理します。テーブルのレイアウトは以下です。

| カラム | 説明 |
|--------|------|
| 区分（PK） | 業務日付を識別するための文字列値 |
| 日付 | 業務日付（文字列、yyyyMMdd形式） |

コンポーネント定義に `BasicBusinessDateProvider` を設定します。

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
  <!-- DBアクセス用トランザクションマネージャ -->
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

---

**3. 業務日付の取得**

アプリケーションからは `BusinessDateUtil` を使います。

---

**4. 業務日付の更新（締め処理での日付送り）**

`BasicBusinessDateProvider` の `setDate` メソッドで更新します。

```java
// システムリポジトリからBasicBusinessDateProviderを取得する
BusinessDateProvider provider = SystemRepository.get("businessDateProvider");

// setDateメソッドを呼び出し、更新する
provider.setDate(segment, date);
```

---

**5. バッチ再実行時に特定プロセスのみ業務日付を上書く**

システムプロパティで指定します。

```
-DBasicBusinessDateProvider.batch=20160317
```

形式: `BasicBusinessDateProvider.<区分>=日付（yyyyMMdd形式）`

**注意点**:
- 業務日付管理機能を使用する場合、`nablarch-common-jdbc` モジュールが追加で必要です。
- `BasicBusinessDateProvider` は初期化が必要なため、`initializeList` への登録を忘れないようにしてください。
- ウェブアプリケーションのようにすべてが1プロセス内で動く場合、締め処理での日付変更は単純にDB上のレコードを `setDate` で更新すれば全機能に反映されます。

参照: libraries-date.json:s2, libraries-date.json:s5, libraries-date.json:s6, libraries-date.json:s7, libraries-date.json:s8, libraries-date.json:s9, libraries-date.json:s10