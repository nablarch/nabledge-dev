# Redisヘルスチェッカ(Lettuce)アダプタ

[Redis(外部サイト、英語)](https://redis.io/) のヘルスチェックをできるようにするアダプタを提供する。
ヘルスチェックについては ヘルスチェックエンドポイントハンドラ を参照。

ヘルスチェックは、 ヘルスチェックを追加する で説明している
`HealthChecker` を継承したクラスを作成して追加できる。
このアダプタでは、HealthCheckerを継承した `RedisHealthChecker` を提供している。

## Redisのヘルスチェックを行う

HealthCheckEndpointHandlerのhealthCheckersプロパティにRedisHealthCheckerを指定することで、Redisのヘルスチェックを実現できる。

設定例を以下に示す。

```xml
<!-- ヘルスチェックエンドポイントハンドラ -->
<component class="nablarch.fw.web.handler.HealthCheckEndpointHandler">
  <!-- healthCheckersプロパティはリストで指定 -->
  <property name="healthCheckers">
    <list>
      <!-- Redisのヘルスチェック -->
      <component class="nablarch.integration.health.RedisHealthChecker">
        <!-- Redisのクライアント(LettuceRedisClient)を指定 -->
        <property name="client" ref="lettuceRedisClient" />
      </component>
    </list>
  </property>
</component>
```
RedisHealthCheckerは `LettuceRedisClient` を使って、
キーの存在確認を行い、例外が発生しなけければヘルスチェックが成功と判断する。キーは存在しなくてよい。
LettuceRedisClient については 構成ごとに用意されたクライアントクラス を参照。

キーを変更したい場合はRedisHealthCheckerのkeyプロパティに指定する。

```xml
<!-- Redisのヘルスチェック -->
<component class="nablarch.integration.health.RedisHealthChecker">
  <!-- Redisのクライアント(LettuceRedisClient)を指定 -->
  <property name="client" ref="lettuceRedisClient" />
  <!-- キーを指定 -->
  <property name="key" ref="pingtest" />
</component>
```

<details>
<summary>keywords</summary>

RedisHealthChecker, LettuceRedisClient, HealthChecker, HealthCheckEndpointHandler, healthCheckers, client, key, Redisヘルスチェック, ヘルスチェック設定, Lettuceアダプタ

</details>
