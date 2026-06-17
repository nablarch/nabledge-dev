**結論**: Nablarchの「日付管理」機能を使用することで、OS日時とは独立した業務日付をデータベースで管理し、`BusinessDateUtil`で取得できます。締め処理など用途別に区分を分けて複数の業務日付を管理することも可能です。

**根拠**:

**1. 業務日付テーブルの設定**

業務日付はデータベーステーブルで管理します。`BasicBusinessDateProvider`をコンポーネント定義に追加し、初期化リストにも登録します。

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
      <!-- 他のコンポーネントは省略 -->
      <component-ref name="businessDateProvider" />
    </list>
  </property>
</component>
```

テーブルのレイアウト:
| カラム | 説明 |
|---|---|
| 区分(PK) | 業務日付を識別するための値（文字列型） |
| 日付 | 業務日付（文字列型、yyyyMMdd形式） |

**2. 業務日付の取得**

`BusinessDateUtil`を使用して取得します。区分を指定することで、オンライン処理用・バッチ処理用など用途別の業務日付を取り分けられます。

```java
// デフォルト区分で取得
String date = BusinessDateUtil.getDate();

// 区分を指定して取得（例：締め処理用の区分）
String closingDate = BusinessDateUtil.getDate("closing");
```

**3. 締め処理での業務日付更新**

締め処理で翌営業日に業務日付を進める場合は、`BasicBusinessDateProvider`の`setDate`メソッドを使用します。

```java
// システムリポジトリからBasicBusinessDateProviderを取得する
BusinessDateProvider provider = SystemRepository.get("businessDateProvider");

// setDateメソッドを呼び出し、更新する
provider.setDate(segment, date);
```

**4. バッチ再実行時の日付上書き**

障害時の再実行など、特定プロセスのみ過去日付で業務処理を行いたい場合は、システムプロパティで上書きできます。

```
# 区分"batch"の日付を2016/03/17に上書きする場合
java -DBasicBusinessDateProvider.batch=20160317 Main
```

**注意点**:
- `BasicBusinessDateProvider`は初期化が必要なため、`initializeList`への登録を忘れないこと
- `cacheEnabled`プロパティはデフォルトでtrueとなっており、`ThreadContext`がクリアされるまでキャッシュされる。リクエスト単位でキャッシュが更新されるため、オンライン処理では通常問題ない
- `setDate`で区分または日付がnullや空文字、`yyyyMMdd`形式でない場合は`IllegalArgumentException`がスローされる

参照: libraries-date.json:s7, libraries-date.json:s8, libraries-date.json:s9, libraries-date.json:s10, javadoc-nablarch-core-date-BusinessDateUtil.json, javadoc-nablarch-core-date-BasicBusinessDateProvider.json