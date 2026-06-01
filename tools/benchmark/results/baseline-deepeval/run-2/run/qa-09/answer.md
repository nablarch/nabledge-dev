**結論**: NablarchはOS日時（`SystemTimeUtil`）と業務日付（`BusinessDateUtil`）を明確に分離して管理できる。業務日付はデータベースのテーブルで管理され、複数の「区分」（例: 通常処理用・締め処理用）を持つことが可能。

**根拠**:

**システム日時の取得**（OS日時そのもの）:
- コンポーネント定義に `BasicSystemTimeProvider` を設定する
- `SystemTimeUtil` を使って取得する

```xml
<component name="systemTimeProvider" class="nablarch.core.date.BasicSystemTimeProvider" />
```

**業務日付の設定**:
`BasicBusinessDateProvider` をコンポーネント定義に追加する。業務日付はDBテーブルで管理され、テーブルレイアウトは「区分（文字列、PK）」と「日付（yyyyMMdd形式の文字列）」の2カラム。

```xml
<component name="businessDateProvider" class="nablarch.core.date.BasicBusinessDateProvider">
  <property name="tableName" value="BUSINESS_DATE" />
  <property name="segmentColumnName" value="SEGMENT"/>
  <property name="dateColumnName" value="BIZ_DATE"/>
  <property name="defaultSegment" value="00"/>
  <property name="transactionManager" ref="transactionManager" />
</component>
```

初期化対象リストへの登録も必要（`initializer` の `initializeList` に追加）。

**業務日付の取得**:
```java
// BusinessDateUtil を使って取得する
BusinessDateUtil.getDate();  // defaultSegmentの区分
```

**締め処理での業務日付更新**:
```java
BusinessDateProvider provider = SystemRepository.get("businessDateProvider");
provider.setDate(segment, date);  // 区分と日付(yyyyMMdd)を指定して更新
```

**業務日付の上書き（バッチ再実行など、特定プロセスのみ）**:
特定のプロセスだけ別の日付で実行したい場合、システムプロパティで上書きできる。

```
-DBasicBusinessDateProvider.batch=20160317
```

**注意点**:
- 業務日付管理機能には `nablarch-common-jdbc` モジュールが必要（依存関係に追加すること）
- ウェブアプリケーションのように全機能が1プロセス内で動く場合は、DBの日付を直接更新すれば全体に反映される
- バッチのように複数プロセスで実行する場合に、特定プロセスのみ上書きするシステムプロパティが有効

参照: libraries-date.json:s5, libraries-date.json:s6, libraries-date.json:s7, libraries-date.json:s8, libraries-date.json:s9, libraries-date.json:s10

---