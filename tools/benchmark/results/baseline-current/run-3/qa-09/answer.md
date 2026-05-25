**結論**: はい、Nablarchには業務日付管理機能があり、OS日時（システム日時）とは独立して業務日付をデータベースで管理・取得できます。複数の区分（セグメント）で業務日付を分けて管理することも可能です。

**根拠**:

### 概要

業務日付管理機能では、データベースのテーブルを使って複数の業務日付を管理します。テーブル構造は以下の通りです。

| カラム | 説明 |
|--------|------|
| 区分（PK） | 業務日付を識別するための値（文字列型） |
| 日付 | 業務日付（文字列型、`yyyyMMdd` 形式） |

「区分」により、例えば締め処理用・通常処理用など複数の業務日付を独立して管理できます。

### 設定（コンポーネント定義）

`nablarch-common-jdbc` の依存追加と、以下のコンポーネント定義が必要です。

```xml
<component name="businessDateProvider" class="nablarch.core.date.BasicBusinessDateProvider">
  <property name="tableName" value="BUSINESS_DATE" />
  <property name="segmentColumnName" value="SEGMENT"/>
  <property name="dateColumnName" value="BIZ_DATE"/>
  <property name="defaultSegment" value="00"/>
  <property name="transactionManager" ref="transactionManager" />
</component>
```

初期化リストへの登録も必要です。

### 業務日付の取得

```java
BusinessDateUtil.getDate();           // デフォルト区分で取得
BusinessDateUtil.getDate("closing");  // 区分指定で取得
```

### 業務日付の更新（締め処理での日付送り）

```java
BusinessDateProvider provider = SystemRepository.get("businessDateProvider");
provider.setDate(segment, date);
```

### バッチ再実行時の過去日付上書き

```
-DBasicBusinessDateProvider.batch=20160317
```

**注意点**:
- `BasicBusinessDateProvider` は初期化が必要なため、`initializeList` への登録を忘れないこと
- システム日時（OS日時）の取得は別クラス `SystemTimeUtil` を使用する。業務日付とは独立しており、混在して使用できる
- ウェブアプリケーションのように全機能が1プロセスで動く場合、業務日付の変更はデータベースの値を直接変更すれば全体に反映される
- コンポーネント定義でクラスを差し替えることで、テスト時に業務日付を任意の値に切り替えることも可能

参照: component/libraries/libraries-date.json#s7, #s8, #s9, #s10, #s2