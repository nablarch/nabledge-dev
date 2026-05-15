**結論**: Nablarchは `BusinessDateUtil` を使って業務日付を取得する機能を提供しており、OS日時（`SystemTimeUtil`）とは完全に分離して管理できます。締め処理のような複数の業務日付を扱うシナリオでは、**区分（セグメント）** キーを使ってDBで複数の業務日付を独立管理できます。

**根拠**:

**業務日付の取得**

```java
// 業務日付の取得
BusinessDateUtil.getDate();              // デフォルト区分の業務日付
BusinessDateUtil.getDate("closing");     // 区分を指定して取得
```

**DBテーブル構造**（業務日付はDBで管理）

| カラム | 説明 |
|--------|------|
| 区分（PK） | 業務日付を識別するキー（例："00", "batch", "closing"） |
| 日付 | 業務日付（yyyyMMdd形式） |

**コンポーネント定義（component.xml）**

```xml
<component name="businessDateProvider" class="nablarch.core.date.BasicBusinessDateProvider">
  <property name="tableName" value="BUSINESS_DATE" />
  <property name="segmentColumnName" value="SEGMENT"/>
  <property name="dateColumnName" value="BIZ_DATE"/>
  <property name="defaultSegment" value="00"/>
  <property name="transactionManager" ref="transactionManager" />
</component>
```

初期化リストへの追加も必要：

```xml
<component name="initializer"
    class="nablarch.core.repository.initialization.BasicApplicationInitializer">
  <property name="initializeList">
    <list>
      <component-ref name="businessDateProvider" />
    </list>
  </property>
</component>
```

**業務日付の更新（締め処理での日付送り）**

```java
BusinessDateProvider provider = SystemRepository.get("businessDateProvider");
provider.setDate(segment, newDate);  // 区分を指定して更新
```

**システム日時の取得（OS日時が必要な場合）**

```java
SystemTimeUtil.getDate();  // OS日時
```

**注意点**:

- 区分（segment）を活用することで「通常業務用」「締め処理用」「バッチ用」など複数の業務日付を同一DBで独立管理できます
- バッチ再実行時に特定プロセスだけ過去日付を使いたい場合は、システムプロパティで上書き可能です：
  `-DBasicBusinessDateProvider.batch=20160317`
  ※ウェブアプリのように全機能が1プロセス内で動く場合は、DBの日付を直接更新するだけで対応できます
- `BasicBusinessDateProvider` は初期化が必要なため、`initializeList` への登録を忘れずに行ってください

参照: `component/libraries/libraries-date.json#s7`, `component/libraries/libraries-date.json#s8`, `component/libraries/libraries-date.json#s10`, `component/libraries/libraries-date.json#s2`