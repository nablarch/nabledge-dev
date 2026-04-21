# ループ制御ハンドラ

## 概要

本ハンドラは、データリーダ上に処理対象のデータが存在する間、後続ハンドラの処理を繰り返し実行する。

> **Important:** DBに接続するバッチアプリケーションではトランザクション管理が必要になるため、本ハンドラではなく トランザクションループ制御ハンドラ を使用すること。
処理の流れは以下のとおり。

![](../../../knowledge/assets/handlers-dbless-loop-handler/flow.png)

## ハンドラクラス名

* `nablarch.fw.handler.DbLessLoopHandler`

<details>
<summary>keywords</summary>

ループ制御ハンドラ, DbLessLoopHandler, 繰り返し実行, データリーダ, 後続ハンドラ, DBなしバッチ, 処理対象データ, DbLessLoopHandler, nablarch.fw.handler.DbLessLoopHandler, ループ制御ハンドラ, DBなしバッチ, 繰り返し実行, データリーダ, loop_handler

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

nablarch-fw-standalone, com.nablarch.framework, Maven依存関係, モジュール

</details>

## 制約

なし。
