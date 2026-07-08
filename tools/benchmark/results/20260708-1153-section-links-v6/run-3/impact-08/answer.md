**結論**: `SystemTimeProvider` インタフェースの実装クラスをコンポーネント定義で差し替えることで、本番とテストでシステム日時を切り替えられる。本番では `BasicSystemTimeProvider`（OS日時を使用）、テストでは `FixedSystemTimeProvider`（固定値を返すテスト用クラス）を指定する。

**根拠**:

Nablarch のシステム日時管理は、`SystemTimeProvider` インタフェースの実装クラスがシステム日時を提供する設計になっている。コンポーネント定義で `systemTimeProvider` という名前のコンポーネントに指定するクラスを切り替えるだけで動作が変わる。

**本番用設定**（OS日時をそのまま使用）:
```xml
<component name="systemTimeProvider" class="nablarch.core.date.BasicSystemTimeProvider" />
```

**テスト用設定**（固定日時を返す）:
```xml
<component name="systemTimeProvider"
    class="nablarch.test.FixedSystemTimeProvider">
  <property name="fixedDate" value="20100913123456" />
</component>
```

| property名 | 設定内容 |
|---|---|
| fixedDate | 指定したい日時を以下のフォーマットいずれかに合致する文字列で指定する。<br>・yyyyMMddHHmmss（14桁）<br>・yyyyMMddHHmmssSSS（17桁） |

アプリケーションコードからは `SystemTimeUtil` を使ってシステム日時を取得するため、テスト/本番どちらの設定でもコード変更は不要。

**注意点**:
- テスト用の設定ファイルと本番用の設定ファイルを分けて管理し、テスト実行時にテスト用設定が読み込まれるようにする必要がある。
- カスタムの日時ロジック（例: 特定のルールで日時を計算する）が必要な場合は、`SystemTimeProvider` を独自に実装したクラスを作成して設定することもできる。

参照:
- 日付管理
  .claude/skills/nabledge-6/docs/component/libraries/libraries-date.md
  システム日時(OS日時)と業務日付の切り替えができる
  システム日時の管理機能を使うための設定
  システム日時を取得する
  システム日時を切り替える
- 目的別API使用方法
  .claude/skills/nabledge-6/docs/development-tools/testing-framework/testing-framework-03-Tips.md
  システム日時を任意の値に固定したい
  設定ファイル例