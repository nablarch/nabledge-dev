全セクションの内容が揃いました。Step 5で回答を生成します。

**Step 6 verify:**

主なNablarch固有クレームの確認:
- `BasicSystemTimeProvider` → s5で直接記載 ✅
- `SystemTimeUtil` → s6で直接記載 ✅
- `BasicBusinessDateProvider` → s7, s10で直接記載 ✅
- `BusinessDateUtil` → s8で直接記載 ✅
- DBテーブルで業務日付を管理 → s7で直接記載 ✅
- `setDate(segment, date)` → s10で直接記載 ✅
- システムプロパティで上書き `-DBasicBusinessDateProvider.batch=20160317` → s9で直接記載 ✅
- `businessDateProvider` コンポーネント名 → s7で直接記載 ✅

verify_result = PASS

---

**結論**: Nablarchの日付管理機能を使うことで、OS日時（`SystemTimeUtil`）と業務日付（`BusinessDateUtil`）を独立して管理・取得できます。業務日付はデータベースのテーブルで管理され、複数の区分（例: 締め処理の種別ごと）を持つことが可能です。

**根拠**:

**システム日時の設定と取得**

コンポーネント定義に `BasicSystemTimeProvider` を設定します：

```xml
<component name="systemTimeProvider" class="nablarch.core.date.BasicSystemTimeProvider" />
```

アプリケーションコードでは `SystemTimeUtil` を使用してOS日時を取得します。

**業務日付の設定と取得**

業務日付はDBテーブルで管理します。テーブルのレイアウト：

| 区分(PK) | 業務日付を識別するための値。文字列型 |
|---|---|
| 日付 | 業務日付。文字列型で値はyyyyMMdd形式 |

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

アプリケーションコードでは `BusinessDateUtil` を使用して業務日付を取得します。

**業務日付の更新（締め処理での日付送り）**

```java
// システムリポジトリからBasicBusinessDateProviderを取得する
BusinessDateProvider provider = SystemRepository.get("businessDateProvider");

// setDateメソッドを呼び出し、更新する
provider.setDate(segment, date);
```

**注意点**:
- 業務日付管理機能を使用する場合、`nablarch-common-jdbc` モジュールへの依存が必要です
- `BasicBusinessDateProvider` は初期化対象のリストに設定する必要があります
- バッチの障害再実行時など、特定プロセスのみ業務日付を変更したい場合は、システムプロパティで上書きできます：
  ```
  -DBasicBusinessDateProvider.<区分>=yyyyMMdd形式の日付
  ```
  例: `-DBasicBusinessDateProvider.batch=20160317`
- ウェブアプリケーションのように全機能が1プロセスで動く場合は、DBのデータを直接変更する方法が簡単です

参照: libraries-date.json:s5, libraries-date.json:s6, libraries-date.json:s7, libraries-date.json:s8, libraries-date.json:s9, libraries-date.json:s10

---