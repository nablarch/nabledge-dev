# Lettuceアダプタ

## 概要

Nablarchが提供する下記の機能で [Redis(外部サイト、英語)](https://redis.io/) を使用できるようにするアダプタを提供する。

- session_store
- health_check_endpoint_handler

本アダプタでは、Redisのクライアントライブラリとして [Lettuce(外部サイト、英語)](https://redis.github.io/lettuce/) を使用している。

## モジュール一覧

```xml
<!-- RedisStore Lettuceアダプタ -->
<dependency>
  <groupId>com.nablarch.integration</groupId>
  <artifactId>nablarch-lettuce-adaptor</artifactId>
</dependency>

<!-- デフォルトコンフィグレーション -->
<dependency>
  <groupId>com.nablarch.configuration</groupId>
  <artifactId>nablarch-main-default-configuration</artifactId>
</dependency>
```
> **Tip:** Redisは5.0.9、Lettuceは5.3.0.RELEASEのバージョンを使用してテストを行っている。 バージョンを変更する場合は、プロジェクト側でテストを行い問題ないことを確認すること。
各機能に対応したアダプタの説明は下記を参照。
