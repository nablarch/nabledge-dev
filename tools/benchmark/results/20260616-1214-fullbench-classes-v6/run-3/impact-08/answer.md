**結論**: Nablarchの日付管理機能では、コンポーネント定義に指定するクラスを差し替えるだけでシステム日時を切り替えられる。テスト用には `SystemTimeProvider` インターフェースを実装したクラスを作り、テスト環境のコンポーネント定義で `systemTimeProvider` として登録することで、任意の日時を返すよう切り替えられる。

---

**根拠**:

**仕組み**

アプリケーションは `SystemTimeUtil` 経由でシステム日時を取得するが、実際の取得処理は `systemTimeProvider` という名前でコンポーネント定義に登録されたクラス（`SystemTimeProvider` インターフェースの実装）に委譲される。コンポーネント定義で指定するクラスを差し替えるだけで取得方法が切り替わる。

**本番環境の設定（OS日時を返す）**

```xml
<component name="systemTimeProvider" class="nablarch.core.date.BasicSystemTimeProvider" />
```

**テスト環境への切り替え手順**

1. `SystemTimeProvider` インターフェースを実装したクラスを作成する（任意の日時を返す実装）
2. テスト用コンポーネント定義ファイルで、そのクラスを `systemTimeProvider` として設定する

---

**業務日付も同様の仕組み**

業務日付（`BusinessDateUtil` 経由で取得）も同じ方式で切り替えられる。

1. `BusinessDateProvider` インターフェースを実装したクラスを作成する
2. テスト用コンポーネント定義で `businessDateProvider` として設定する

本番環境では `BasicBusinessDateProvider`（DBのテーブルから取得）が使われるが、テスト用の実装に差し替えることで任意の日付を返せる。

---

**注意点**: この切り替えはコンポーネント定義ファイルの差し替えで実現するため、テスト実行時にテスト用コンポーネント定義が読み込まれる構成にする必要がある。

参照: component/libraries/libraries-date.json:s2, s5, s6, s12, s13