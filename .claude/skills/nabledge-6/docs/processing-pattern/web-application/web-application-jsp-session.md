# JSPで自動的にHTTPセッションを作成しないようにする方法

<details>
<summary>keywords</summary>

HTTPセッション自動作成防止, JSPセッション設定, page session false, メモリ消費削減, hidden暗号化機能, tag-hidden_encryption

</details>

JSPのデフォルトの動作では、HTTPセッションが存在しない場合に自動的にHTTPセッションが作成される。
例えば、HTTPセッションを必要としないようなログイン画面の表示などでも、デフォルトでは自動的にHTTPセッションが作成され、
アプリケーションサーバ上のメモリが無駄に消費される。

このため、JSPでHTTPセッションを自動的に作成しないようにすることを推奨する。

JSPでHTTPセッションを自動的に作成しないようにするには、各JSPの先頭に以下の設定を追加する。

```jsp
<%@ page session="false" %>
```
> **Important:** `hidden暗号化機能(非推奨機能) <tag-hidden_encryption>` を使用した場合、hidden暗号化処理内でHTTPセッションを使用するため、上記設定を使用することは出来ないので注意すること。
