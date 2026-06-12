**結論**: Nablarch 6 には「業務日付管理機能」が組み込まれており、OS日時（システム日時）とは独立した業務日付をデータベースで管理できます。締め処理のような用途で「区分（セグメント）」を使って複数の業務日付を使い分けることも可能です。

**根拠**:

1. **システム日時と業務日付は別管理**
   - システム日時（OS日時）は `BasicSystemTimeProvider` / `SystemTimeUtil` で取得
   - 業務日付は `BasicBusinessDateProvider` / `BusinessDateUtil` で取得
   - それぞれ独立したコンポーネントとして定義するため、両者を同時に使い分けられます

2. **業務日付の設定（コンポーネント定義）**
   ```xml
   <component name="businessDateProvider" class="nablarch.core.date.BasicBusinessDateProvider">
     <property name="tableName" value="BUSINESS_DATE" />
     <property name="segmentColumnName" value="SEGMENT"/>
     <property name="dateColumnName" value="BIZ_DATE"/>
     <property name="defaultSegment" value="00"/>
     <property name="transactionManager" ref="transactionManager" />
   </component>
   ```
   業務日付はDBテーブルで管理されます。テーブルには「区分（PK）」と「日付（yyyyMMdd形式）」のカラムが必要です。

3. **業務日付の取得**
   `BusinessDateUtil` を使って取得します。区分を指定することで、複数の業務日付（例: 締め処理用、通常処理用など）を使い分けられます。

4. **業務日付の更新（締め処理での利用に適した機能）**
   ```java
   BusinessDateProvider provider = SystemRepository.get("businessDateProvider");
   provider.setDate(segment, date); // 区分と日付を指定して更新
   ```

5. **再実行時の日付上書き（バッチ障害対応）**
   バッチの再実行時に過去日付を業務日付として使いたい場合は、システムプロパティで上書き可能です：
   ```
   -DBasicBusinessDateProvider.batch=20160317
   ```

**注意点**:
- 業務日付管理機能には `nablarch-common-jdbc` モジュールの追加が必要（システム日時のみなら `nablarch-core` だけで可）
- `BasicBusinessDateProvider` は初期化が必要なため、`initializer` の `initializeList` に登録すること
- ウェブアプリのように単一プロセスで全機能が動く場合、業務日付の変更はDBのレコードを直接更新するだけで済む

参照: `libraries-date.json#s2`, `libraries-date.json#s5`, `libraries-date.json#s6`, `libraries-date.json#s7`, `libraries-date.json#s8`, `libraries-date.json#s9`, `libraries-date.json#s10`