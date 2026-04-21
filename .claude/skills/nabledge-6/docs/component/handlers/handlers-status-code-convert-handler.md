# ステータスコード→プロセス終了コード変換ハンドラ

## 概要

後続ハンドラによる処理結果のステータスコードをプロセスの終了コードに変換するハンドラ。

処理の流れは以下のとおり。

![](../../../knowledge/assets/handlers-status-code-convert-handler/StatusCodeConvertHandler_flow.png)

## ハンドラクラス名

* `nablarch.fw.handler.StatusCodeConvertHandler`

<details>
<summary>keywords</summary>

StatusCodeConvertHandler, nablarch.fw.handler.StatusCodeConvertHandler, ハンドラクラス

</details>

## モジュール一覧

```xml
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-fw-standalone</artifactId>
</dependency>
```

<details>
<summary>keywords</summary>

nablarch-fw-standalone, モジュール依存関係, Maven依存関係

</details>

## 制約

main の直後に設定すること
本ハンドラが処理結果のステータスコードをプロセスの終了コードに変換するため。

<details>
<summary>keywords</summary>

制約, ハンドラ設定順序, main直後, 設定制約

</details>

## ステータスコード→プロセス終了コード変換

ステータスコード→プロセス終了コード変換は、以下のルールで行う。

> **Important:** アプリケーションのエラー処理でステータスコードを指定する場合は、 100～199を使用する。
| ステータスコード | プロセス終了コード |
|---|---|
| -1以下 | 1 |
| 0～199 | 0～199(変換は行わない) |
| 200～399 | 0 |
| 400 | 10 |
| 401 | 11 |
| 403 | 12 |
| 404 | 13 |
| 409 | 14 |
| 上記以外の400～499 | 15 |
| 500以上 | 20 |

> **Tip:** このハンドラは、設定などで変換ルールを切り替えることはできない。 このため、この変換ルールで要件を満たすことができない場合は、 プロジェクト固有の変換用ハンドラを作成し対応すること。

<details>
<summary>keywords</summary>

ステータスコード変換, プロセス終了コード, エラーコード変換ルール, 終了コードマッピング, 100～199, アプリケーションエラー処理

</details>
