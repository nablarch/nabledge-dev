**結論**: Nablarchのコンポーネント定義で `systemTimeProvider` という名前のクラスを差し替えることで、テスト時だけシステム日時を任意の固定値に切り替えられる。テスト用には `FixedSystemTimeProvider` クラスが提供されている。

**根拠**:

**仕組み**

Nablarchはシステム日時を `SystemTimeProvider` インタフェースの実装クラスから取得する。本番環境では `BasicSystemTimeProvider`（OSの現在時刻を返す）を使用するが、コンポーネント定義で指定するクラスを差し替えるだけで取得元を変更できる。

本番用のコンポーネント定義:
```xml
<component name="systemTimeProvider" class="nablarch.core.date.BasicSystemTimeProvider" />
```

**テスト時の差し替え**

テスト用コンポーネント設定ファイルで `FixedSystemTimeProvider` を同じ名前 `systemTimeProvider` で上書き登録する。コンポーネント定義では「同じ name 属性のコンポーネントを後から登録すると上書きされる」という仕組みを利用する。

```xml
<component name="systemTimeProvider"
    class="nablarch.test.FixedSystemTimeProvider">
  <property name="fixedDate" value="20100913123456" />
</component>
```

`fixedDate` プロパティには以下のフォーマットで日時を指定する:
- `yyyyMMddHHmmss`（14桁）
- `yyyyMMddHHmmssSSS`（17桁）

テストコードからシステム日時を取得する場合:
```java
SystemTimeProvider provider = (SystemTimeProvider) SystemRepository.getObject("systemTimeProvider");
Date now = provider.getDate();
```

**本番/テストの切り替え方法**

環境ごとのコンポーネント設定ファイル（XMLファイル）を切り替えることで実現する。テスト環境ではテスト用の設定ファイル（`FixedSystemTimeProvider` を定義）を読み込み、本番環境では本番用の設定ファイルを読み込む構成にする。

**注意点**:
- 異なるクラスで上書きした場合、上書き前の `property` への設定は全て破棄される。
- 業務日付（データベースで管理する日付）を切り替えたい場合は、`BusinessDateProvider` インタフェースを実装したテスト用クラスを同様に差し替える。

参照: libraries-date.json:s2, libraries-date.json:s5, libraries-date.json:s12, testing-framework-03-Tips.json:s11, testing-framework-03-Tips.json:s12, libraries-repository.json:s8, setting-guide-ManagingEnvironmentalConfiguration.json:s9