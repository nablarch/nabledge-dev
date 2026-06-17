**結論**: テスト時のシステム日時差し替えは、`SystemTimeProvider`インタフェースを実装したクラスをテスト用コンポーネント定義で `systemTimeProvider` という名前で登録することで実現できます。業務日付の差し替えも同様に、`BusinessDateProvider`インタフェースを実装したクラスを `businessDateProvider` という名前で登録することで切り替えられます。

**根拠**:

#### 仕組みの概要

Nablarchの日時管理機能は、`SystemRepository` から特定のコンポーネント名で登録されたクラスを通じて日時を提供する設計になっています。そのため、**コンポーネント定義ファイルを差し替えるだけで、アプリケーションコードを一切変更せずに本番とテストの動作を切り替えられます**。

---

#### システム日時（OS日時）の切り替え

`SystemTimeUtil` は、`SystemRepository` からコンポーネント名 `systemTimeProvider` で登録された `SystemTimeProvider` 実装を使用して日時を返します。

**本番用設定**（コンポーネント定義に追加）:
```xml
<component name="systemTimeProvider" class="nablarch.core.date.BasicSystemTimeProvider" />
```
`BasicSystemTimeProvider` は `new Date()` で現在時刻を返します。

**テスト用切り替え手順**:
1. `nablarch.core.date.SystemTimeProvider` インタフェースを実装したクラスを作成する
2. テスト用コンポーネント定義でそのクラスを `systemTimeProvider` という名前で登録する

アプリケーション側のコード (`SystemTimeUtil.getDate()` 等) は変更不要です。

---

#### 業務日付の切り替え

`BusinessDateUtil` は、`SystemRepository` からコンポーネント名 `businessDateProvider` で登録された `BusinessDateProvider` 実装を通じて業務日付を提供します。

**本番用設定**（DBテーブルから取得）:
```xml
<component name="businessDateProvider" class="nablarch.core.date.BasicBusinessDateProvider">
  <property name="tableName" value="BUSINESS_DATE" />
  <property name="segmentColumnName" value="SEGMENT"/>
  <property name="dateColumnName" value="BIZ_DATE"/>
  <property name="defaultSegment" value="00"/>
  <property name="transactionManager" ref="transactionManager" />
</component>
```

**テスト用切り替え手順**:
1. `nablarch.core.date.BusinessDateProvider` インタフェースを実装したクラスを作成する
2. テスト用コンポーネント定義でそのクラスを `businessDateProvider` という名前で登録する

また、`BasicBusinessDateProvider` を使ったまま特定の区分の業務日付だけを上書きしたい場合は、**システムプロパティ**でも対応できます:

```
java -DBasicBusinessDateProvider.batch=20160317 Main
java -DBasicBusinessDateProvider.00=20110101 Main
```
形式: `BasicBusinessDateProvider.<区分>=yyyyMMdd`

この方法はバッチアプリケーションで特定プロセスだけ業務日付を変えたい場合に有効です。

---

**注意点**:
- ウェブアプリケーションのように全機能が1プロセス内で動く場合、業務日付の変更はDBテーブルのデータを直接変更する方が簡単です
- システムプロパティによる上書きでは、形式が不正な場合に初回アクセス時に `RuntimeException` が送出されます
- `BasicBusinessDateProvider` はデフォルトでキャッシュが有効（`cacheEnabled=true`）なため、キャッシュの有効期間（1リクエスト単位など）に注意してください

参照: libraries-date.json:s2, libraries-date.json:s5, libraries-date.json:s9, libraries-date.json:s12, libraries-date.json:s13, javadoc-nablarch-core-date-SystemTimeUtil.json:s1, javadoc-nablarch-core-date-BasicBusinessDateProvider.json:s1