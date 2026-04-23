**結論**: バッチのリクエスト単体テストで起動パラメータ（コマンドライン引数）を指定するには、テストデータ（テストケース一覧）のカラムとして `args[n]` 形式（n は 0 以上の整数）を追加します。また、`diConfig`、`requestPath`、`userId` は必須のコマンドライン引数として専用カラムが用意されています。`args[n]` 以外の任意カラムを追加すると、そのカラム名がコマンドラインオプション（`-カラム名=値`）として渡されます。

**根拠**:

1. テストクラスは `nablarch.test.core.batch.BatchRequestTestSupport` を継承し、`<Actionクラス名>RequestTest` という名前で作成します。

    ```java
    package nablarch.sample.ss21AA;

    public class RM21AA001ActionRequestTest extends BatchRequestTestSupport {
    ```

2. テストケース一覧（`LIST_MAP` データタイプ、ID は `testShots`）で必須となるコマンドライン引数用カラム：

    | カラム名 | 説明 |
    |---|---|
    | `diConfig` | バッチ実行時のコンポーネント設定ファイルへのパス（必須） |
    | `requestPath` | バッチ実行時のリクエストパス（必須） |
    | `userId` | バッチ実行ユーザID（必須） |

3. バッチ起動時の位置引数を指定する場合は、`args[n]` 形式のカラムを追加します（**添字 n は 0 以上の連続した整数**）。

    | no | case | ... | args[0] | args[1] | args[2] |
    |---|---|---|---|---|---|
    | 1 | xxxのケース | ... | 第1引数 | 第2引数 | 第3引数 |

4. `args[n]` 以外の任意カラムを追加すると、コマンドラインオプションとして扱われます。例えば以下のようなカラム構成の場合：

    | no | case | ... | paramA | paramB |
    |---|---|---|---|---|
    | 1 | xxxのケース | ... | valueA | valueB |

    次と同等のコマンドラインオプションを指定したことになります。

    ```bash
    -paramA=valueA -paramB=valueB
    ```

**注意点**:
- `args[n]` の添字 n は **連続した整数**でなければなりません（例: `args[0]`, `args[1]`, `args[2]` のように飛ばさずに）。
- `diConfig`、`requestPath`、`userId` は必須カラムのため省略不可です。
- テストデータを記載した Excel ファイルは、テストソースコードと同じディレクトリに同じ名前（拡張子のみ異なる）で格納します。

参照:
- `development-tools/testing-framework/testing-framework-02-requestunittest-batch.json#s6` （コマンドライン引数）
- `development-tools/testing-framework/testing-framework-02-requestunittest-batch.json#s5` （テストケース一覧の必須カラム）
- `development-tools/testing-framework/testing-framework-02-requestunittest-batch.json#s1` （テストクラスの書き方）
