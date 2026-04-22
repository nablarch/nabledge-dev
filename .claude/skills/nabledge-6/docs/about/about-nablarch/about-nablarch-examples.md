# Example

Exampleは、Nablarchアプリケーションフレームワークの機能の使用方法を示した実装例であり、 実行制御基盤 毎に作成している。
本章では、Exampleに必要な環境構築手順と、アプリケーションの実行手順を解説する。

> **Tip:**
> Exampleを改修して本格的なアプリケーションを作成することは想定していない。

> 本格的なアプリケーションを作成する場合は ブランクプロジェクト から作成すること。

## Exampleの実行方法

## 環境構築手順

Exampleは、Apache Mavenを使用してアプリケーションをビルド、実行する。以下のページを参考に、ApacheMavenのPCへのインストール及び必要な設定を行うこと。

maven

## 実行手順

Exampleの実行手順は、各ExampleのGitHubリポジトリトップにあるREADMEを参照すること。

## Java 21 で動かす場合

ExampleはJava 17での実行を前提としている。
Java 21で動かす場合は、個別にセットアップが必要となる。
詳細は、以下のブランクプロジェクトの説明を参照のこと。

Java21で使用する場合のセットアップ方法

## Exampleの一覧

実行制御基盤毎のExampleを以下に示す。実装の解説も用意しているので、必要に応じて、以下一覧の「解説」リンクより参照すること。

## ウェブアプリケーション

* [ウェブアプリケーション (JSP)](https://github.com/nablarch/nablarch-example-web) (解説)
* [ウェブアプリケーション (Thymeleaf)](https://github.com/nablarch/nablarch-example-thymeleaf-web) (解説)

## ウェブサービス

* [RESTfulウェブサービス](https://github.com/nablarch/nablarch-example-rest) (解説)
* [HTTPメッセージング (受信)](https://github.com/nablarch/nablarch-example-http-messaging) (解説)
* [HTTPメッセージング (送信)](https://github.com/nablarch/nablarch-example-http-messaging-send) (解説)

## バッチアプリケーション

* [Jakarta Batchに準拠したバッチアプリケーション](https://github.com/nablarch/nablarch-example-batch-ee) (解説)
* [Nablarchバッチアプリケーション](https://github.com/nablarch/nablarch-example-batch) (解説)

## メッセージング

* MOMによるメッセージング (解説)

  * [応答不要メッセージ送信](https://github.com/nablarch/nablarch-example-mom-delayed-send)
  * [同期応答メッセージ送信](https://github.com/nablarch/nablarch-example-mom-sync-send-batch)
  * [応答不要メッセージ受信](https://github.com/nablarch/nablarch-example-mom-delayed-receive)
  * [同期応答メッセージ受信](https://github.com/nablarch/nablarch-example-mom-sync-receive)
* [テーブルをキューとして使ったメッセージング](https://github.com/nablarch/nablarch-example-db-queue) (解説)
