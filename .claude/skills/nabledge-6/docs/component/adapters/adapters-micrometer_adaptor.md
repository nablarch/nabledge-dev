# Micrometerアダプタ

## モジュール一覧

[Micrometer (外部サイト、英語)](https://micrometer.io/) を使用したメトリクス収集を行うためのアダプタを提供する。

* JVM のメモリ使用量や CPU 使用率など、アプリケーションのメトリクスを収集できる
* 収集したメトリクスを [Datadog (外部サイト)](https://www.datadoghq.com/ja/) や [CloudWatch (外部サイト)](https://aws.amazon.com/jp/cloudwatch/) などの監視サービスに連携できる

**モジュール**:

```xml
<dependency>
  <groupId>com.nablarch.integration</groupId>
  <artifactId>nablarch-micrometer-adaptor</artifactId>
</dependency>
```

> **補足**: Micrometer バージョン 1.13.0 で検証済み。バージョン変更時はプロジェクト側での検証が必須。

## Micrometerアダプタを使用するための設定を行う

Micrometerアダプタのセットアップに必要な手順。

> **補足**: LoggingMeterRegistryはSLF4JまたはJava Util Loggingでメトリクスをログ出力する。デフォルトではJava Util Loggingで標準出力に出力されるため、簡単な動作確認に適している。他のレジストリはサービス準備や実装が必要になる。

### DefaultMeterBinderListProviderの宣言

**クラス**: `DefaultMeterBinderListProvider`

Micrometerには `MeterBinder` というインタフェースが存在する。JVMのメモリ使用量やCPU使用率など、よく使用するメトリクスの収集は、このインタフェースを実装したクラスとしてあらかじめ用意されている。

例：
- JVMのメモリ使用量: `JvmMemoryMetrics`
- CPU使用率: `ProcessorMetrics`

`DefaultMeterBinderListProvider` は、この `MeterBinder` のリストを提供するクラスで、本クラスを使用することでJVMのメモリ使用量やCPU使用率などのメトリクスを収集できるようになる。

web-component-configuration.xmlに以下を追加:

```xml
<component name="meterBinderListProvider"
           class="nablarch.integration.micrometer.DefaultMeterBinderListProvider" />
```

### DefaultMeterBinderListProviderの廃棄処理

廃棄処理が必要。以下をdisposerに登録:

```xml
<component name="disposer"
    class="nablarch.core.repository.disposal.BasicApplicationDisposer">

  <property name="disposableList">
    <list>
      <component-ref name="meterBinderListProvider"/>
    </list>
  </property>

</component>
```

### レジストリファクトリの宣言

**クラス**: `LoggingMeterRegistryFactory`

使用するレジストリのファクトリクラスをコンポーネント宣言:

```xml
<component class="nablarch.integration.micrometer.logging.LoggingMeterRegistryFactory">
  <property name="meterBinderListProvider" ref="meterBinderListProvider" />
  <property name="applicationDisposer" ref="disposer" />
</component>
```

設定プロパティ:
- **meterBinderListProvider**: `DefaultMeterBinderListProvider` への参照（必須）
- **applicationDisposer**: `BasicApplicationDisposer` への参照（必須）

提供ファクトリクラス一覧: :ref:`micrometer_registry_factory`

### micrometer.propertiesの作成

src/main/resourcesに micrometer.properties を作成。内容が空でも配置が必須:

```properties
# 確認を楽にするため、5秒ごとにメトリクスを出力する（デフォルトは1分）
nablarch.micrometer.logging.step=5s
# step で指定した時間よりも早くアプリケーションが終了した場合でも廃棄処理でログが出力されるよう設定
nablarch.micrometer.logging.logInactive=true
```

> **重要**: micrometer.propertiesは内容が空であっても必ず配置しなければならない。

### 実行結果

アプリケーションを起動すると、以下のように収集されたメトリクスが標準出力に出力されていることを確認できる。

```text
2020-09-04 15:33:40.689 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: jvm.gc.count{memory.manager.name=PS Scavenge} throughput=2.6/s
2020-09-04 15:33:40.690 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: jvm.gc.count{memory.manager.name=PS MarkSweep} throughput=0.4/s
2020-09-04 15:33:40.691 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: jvm.buffer.count{id=mapped} value=0 buffers
2020-09-04 15:33:40.691 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: jvm.buffer.count{id=direct} value=2 buffers
2020-09-04 15:33:40.692 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: jvm.buffer.memory.used{id=direct} value=124 KiB
2020-09-04 15:33:40.692 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: jvm.buffer.memory.used{id=mapped} value=0 B
2020-09-04 15:33:40.692 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: jvm.buffer.total.capacity{id=mapped} value=0 B
2020-09-04 15:33:40.692 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: jvm.buffer.total.capacity{id=direct} value=124 KiB
2020-09-04 15:33:40.693 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: jvm.classes.loaded{} value=9932 classes
2020-09-04 15:33:40.693 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: jvm.gc.live.data.size{} value=0 B
2020-09-04 15:33:40.693 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: jvm.gc.max.data.size{} value=2.65918 GiB
2020-09-04 15:33:40.694 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: jvm.memory.committed{area=heap,id=PS Old Gen} value=182.5 MiB
2020-09-04 15:33:40.694 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: jvm.memory.committed{area=heap,id=PS Survivor Space} value=44 MiB
2020-09-04 15:33:40.694 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: jvm.memory.committed{area=heap,id=PS Eden Space} value=197 MiB
2020-09-04 15:33:40.694 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: jvm.memory.committed{area=nonheap,id=Code Cache} value=29.125 MiB
2020-09-04 15:33:40.694 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: jvm.memory.committed{area=nonheap,id=Compressed Class Space} value=6.796875 MiB
2020-09-04 15:33:40.695 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: jvm.memory.committed{area=nonheap,id=Metaspace} value=55.789062 MiB
2020-09-04 15:33:40.695 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: jvm.memory.max{area=heap,id=PS Old Gen} value=2.65918 GiB
2020-09-04 15:33:40.695 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: jvm.memory.max{area=heap,id=PS Survivor Space} value=44 MiB
2020-09-04 15:33:40.696 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: jvm.memory.max{area=nonheap,id=Code Cache} value=240 MiB
2020-09-04 15:33:40.696 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: jvm.memory.max{area=nonheap,id=Metaspace} value=-1 B
2020-09-04 15:33:40.696 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: jvm.memory.max{area=heap,id=PS Eden Space} value=1.243652 GiB
2020-09-04 15:33:40.696 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: jvm.memory.max{area=nonheap,id=Compressed Class Space} value=1 GiB
2020-09-04 15:33:40.697 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: jvm.memory.used{area=nonheap,id=Code Cache} value=28.618713 MiB
2020-09-04 15:33:40.697 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: jvm.memory.used{area=nonheap,id=Compressed Class Space} value=6.270714 MiB
2020-09-04 15:33:40.697 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: jvm.memory.used{area=nonheap,id=Metaspace} value=54.118324 MiB
2020-09-04 15:33:40.698 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: jvm.memory.used{area=heap,id=PS Old Gen} value=69.320663 MiB
2020-09-04 15:33:40.698 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: jvm.memory.used{area=heap,id=PS Survivor Space} value=7.926674 MiB
2020-09-04 15:33:40.698 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: jvm.memory.used{area=heap,id=PS Eden Space} value=171.750542 MiB
2020-09-04 15:33:40.698 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: jvm.threads.daemon{} value=28 threads
2020-09-04 15:33:40.698 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: jvm.threads.live{} value=29 threads
2020-09-04 15:33:40.699 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: jvm.threads.peak{} value=31 threads
2020-09-04 15:33:40.702 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: jvm.threads.states{state=blocked} value=0 threads
2020-09-04 15:33:40.703 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: jvm.threads.states{state=runnable} value=9 threads
2020-09-04 15:33:40.703 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: jvm.threads.states{state=new} value=0 threads
2020-09-04 15:33:40.703 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: jvm.threads.states{state=timed-waiting} value=3 threads
2020-09-04 15:33:40.703 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: jvm.threads.states{state=terminated} value=0 threads
2020-09-04 15:33:40.704 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: jvm.threads.states{state=waiting} value=17 threads
2020-09-04 15:33:41.199 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: process.cpu.usage{} value=0.111672
2020-09-04 15:33:41.199 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: process.start.time{} value=444222h 33m 14.544s
2020-09-04 15:33:41.199 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: process.uptime{} value=26.729s
2020-09-04 15:33:41.200 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: system.cpu.count{} value=8
2020-09-04 15:33:41.200 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: system.cpu.usage{} value=0.394545
```

この出力により、メトリクスが正常に収集・出力されていることが確認できる.

## レジストリファクトリ

このアダプタが提供するレジストリのファクトリクラス：

| レジストリ | ファクトリクラス | アダプタバージョン |
|---|---|---|
| SimpleMeterRegistry | `SimpleMeterRegistryFactory` | 1.0.0 以上 |
| LoggingMeterRegistry | `LoggingMeterRegistryFactory` | 1.0.0 以上 |
| CloudWatchMeterRegistry | `CloudWatchMeterRegistryFactory` | 1.0.0 以上 |
| DatadogMeterRegistry | `DatadogMeterRegistryFactory` | 1.0.0 以上 |
| StatsdMeterRegistry | `StatsdMeterRegistryFactory` | 1.0.0 以上 |
| OtlpMeterRegistry | `OtlpMeterRegistryFactory` | 1.3.0 以上 |

## 設定ファイル

### 配置場所

設定ファイルは、クラスパス直下に `micrometer.properties` という名前で配置する。

### フォーマット

設定は以下のフォーマットで記述：

```
nablarch.micrometer.<subPrefix>.<key>=値
```

`<subPrefix>` の値はレジストリファクトリごとに異なる：

| レジストリファクトリ | subPrefix |
|---|---|
| `SimpleMeterRegistryFactory` | `simple` |
| `LoggingMeterRegistryFactory` | `logging` |
| `CloudWatchMeterRegistryFactory` | `cloudwatch` |
| `DatadogMeterRegistryFactory` | `datadog` |
| `StatsdMeterRegistryFactory` | `statsd` |
| `OtlpMeterRegistryFactory` | `otlp` |

`<key>` には、各レジストリの[Micrometer設定クラス](https://javadoc.io/doc/io.micrometer/micrometer-core/1.13.0/io/micrometer/core/instrument/config/MeterRegistryConfig.html)で定義されたメソッドと同じ名前を指定する。

例：`DatadogMeterRegistry` に対する `DatadogConfig` の `apiKey()` メソッドに対応：

```
nablarch.micrometer.datadog.apiKey=XXXXXXXXXXXXXXXXXXXX
```

### OS環境変数・システムプロパティで上書きする

`micrometer.properties` の設定値は、OS環境変数およびシステムプロパティで上書き可能。優先度（高→低）：

1. システムプロパティで指定した値
2. OS環境変数で指定した値
3. `micrometer.properties` の設定値

例：

micrometer.properties:
```
nablarch.micrometer.example.one=PROPERTIES
nablarch.micrometer.example.two=PROPERTIES
nablarch.micrometer.example.three=PROPERTIES
```

OS環境変数:
```
export NABLARCH_MICROMETER_EXAMPLE_TWO=OS_ENV
export NABLARCH_MICROMETER_EXAMPLE_THREE=OS_ENV
```

システムプロパティ:
```
-Dnablarch.micrometer.example.three=SYSTEM_PROP
```

最終的な採用値：

| キー | 採用される値 |
|---|---|
| `one` | `PROPERTIES` |
| `two` | `OS_ENV` |
| `three` | `SYSTEM_PROP` |

OS環境変数で上書きするときの名前ルールについては :ref:`OS環境変数の名前について <repository-overwrite_environment_configuration_by_os_env_var_naming_rule>` を参照。

### 設定のプレフィックスを変更する

レジストリファクトリの `prefix` プロパティを指定することで、プレフィックス `nablarch.micrometer.<subPrefix>` を変更できる。

例：

```xml
<component name="meterRegistry" class="nablarch.integration.micrometer.logging.LoggingMeterRegistryFactory">
  <property name="meterBinderListProvider" ref="meterBinderListProvider" />
  <property name="applicationDisposer" ref="disposer" />
  <property name="prefix" value="sample.prefix" />
</component>
```

この場合、`micrometer.properties` は以下のように設定：

```
sample.prefix.step=10s
```

### 設定ファイルの場所を変更する

レジストリファクトリの `xmlConfigPath` プロパティに、設定ファイルを読み込むXMLファイルのパスを指定する。

例：

```xml
<component name="meterRegistry" class="nablarch.integration.micrometer.logging.LoggingMeterRegistryFactory">
  <property name="meterBinderListProvider" ref="meterBinderListProvider" />
  <property name="applicationDisposer" ref="disposer" />
  <property name="xmlConfigPath" value="config/metrics.xml" />
</component>
```

`xmlConfigPath` で指定した場所に配置するXMLファイル（クラスパス内の `config/metrics.properties` を読み込む例）：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<component-configuration
        xmlns="http://tis.co.jp/nablarch/component-configuration"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://tis.co.jp/nablarch/component-configuration https://nablarch.github.io/schema/component-configuration.xsd">

  <!-- Micrometerアダプタの設定を読み込む -->
  <config-file file="config/metrics.properties" />

</component-configuration>
```

> **補足**: このXMLファイルはコンポーネント設定ファイルと同じ書式で記述できる。ただし、このファイルでコンポーネントを定義しても、システムリポジトリから参照を取得できない。

## DefaultMeterBinderListProviderで収集されるメトリクス

DefaultMeterBinderListProvider が生成する MeterBinder には、以下のクラスが含まれている：

- `JvmMemoryMetrics`
- `JvmGcMetrics`
- `JvmThreadMetrics`
- `ClassLoaderMetrics`
- `ProcessorMetrics`
- `FileDescriptorMetrics`
- `UptimeMetrics`
- `NablarchGcCountMetrics`

これらにより、以下のメトリクスが収集される：

| メトリクス名 | 説明 |
|---|---|
| `jvm.buffer.count` | バッファプール内のバッファの数 |
| `jvm.buffer.memory.used` | バッファプールの使用量 |
| `jvm.buffer.total.capacity` | バッファプールの合計容量 |
| `jvm.memory.used` | メモリプールのメモリ使用量 |
| `jvm.memory.committed` | メモリプールのコミットされたメモリ量 |
| `jvm.memory.max` | メモリプールの最大メモリ量 |
| `jvm.gc.max.data.size` | OLD領域の最大メモリ量 |
| `jvm.gc.live.data.size` | Full GC 後の OLD 領域のメモリ使用量 |
| `jvm.gc.memory.promoted` | GC 前後で増加した OLD 領域のメモリ使用量の増分 |
| `jvm.gc.memory.allocated` | 前回の GC 後から今回の GC までの Young 領域のメモリ使用量の増分 |
| `jvm.gc.concurrent.phase.time` | コンカレントフェーズの処理時間 |
| `jvm.gc.pause` | GC の一時停止に費やされた時間 |
| `jvm.threads.peak` | スレッド数のピーク数 |
| `jvm.threads.daemon` | 現在のデーモンスレッドの数 |
| `jvm.threads.live` | 現在の非デーモンスレッドの数 |
| `jvm.threads.states` | 現在のスレッドの状態ごとの数 |
| `jvm.classes.loaded` | 現在ロードされているクラスの数 |
| `jvm.classes.unloaded` | JVM が起動してから今までにアンロードされたクラスの数 |
| `system.cpu.count` | JVM で使用できるプロセッサーの数 |
| `system.load.average.1m` | 最後の1分のシステム負荷平均 （参考： [OperatingSystemMXBean](https://docs.oracle.com/javase/jp/17/docs/api/java.management/java/lang/management/OperatingSystemMXBean.html#getSystemLoadAverage())） |
| `system.cpu.usage` | システム全体の直近の CPU 使用率 |
| `process.cpu.usage` | JVM の直近の CPU 使用率 |
| `process.files.open` | 開いているファイルディスクリプタの数 |
| `process.files.max` | ファイルディスクリプタの最大数 |
| `process.uptime` | JVM の稼働時間 |
| `process.start.time` | JVM の起動時刻（UNIX 時間） |
| `jvm.gc.count` | GC の回数 |
| `jvm.threads.started` | JVM で起動したスレッド数 |
| `process.cpu.time` | Java仮想マシン・プロセスによって使用される CPU 時間 |

詳細は :ref:`micrometer_metrics_output_example` を参照。

## 共通のタグを設定する

レジストリファクトリの`tags` プロパティで、すべてのメトリクスに共通するタグを設定できる。この機能はアプリケーションが稼働しているホスト、インスタンス、リージョンなどを識別する情報を設定する用途として使用できる。

**設定例:**

```xml
<component name="meterRegistry" class="nablarch.integration.micrometer.logging.LoggingMeterRegistryFactory">
  <property name="meterBinderListProvider" ref="meterBinderListProvider" />
  <property name="applicationDisposer" ref="disposer" />

  <!-- tags プロパティで共通のタグを設定 -->
  <property name="tags">
    <map>
      <entry key="foo" value="FOO" />
      <entry key="bar" value="BAR" />
    </map>
  </property>
</component>
```

**プロパティ仕様:**

| プロパティ名 | 型 | 説明 |
|---|---|---|
| tags | Map<String, String> | マップのキーがタグ名、値がタグ値に対応付けられる |

**出力例:**

上記設定の場合、全てのメトリクスにfoo=FOO, bar=BARのタグが設定される。

```text
2020-09-04 17:30:06.656 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: process.start.time{bar=BAR,foo=FOO} value=444224h 29m 38.875000064s
2020-09-04 17:30:06.656 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: process.uptime{bar=BAR,foo=FOO} value=27.849s
2020-09-04 17:30:06.657 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: system.cpu.count{bar=BAR,foo=FOO} value=8
2020-09-04 17:30:06.657 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: system.cpu.usage{bar=BAR,foo=FOO} value=0.475654
```

## 監視サービスと連携する

## 監視サービスと連携する

監視サービスと連携するためには、以下のとおり設定する必要がある：

1. 監視サービスや連携方法ごとに用意された Micrometer のモジュールを依存関係に追加する
2. 使用するレジストリファクトリをコンポーネントとして定義する
3. その他、監視サービスごとに独自に設定する

### Datadog と連携する

**依存関係**：

```xml
<dependency>
  <groupId>io.micrometer</groupId>
  <artifactId>micrometer-registry-datadog</artifactId>
  <version>1.13.0</version>
</dependency>
```

**レジストリファクトリ**：

**クラス**: `DatadogMeterRegistryFactory`

```xml
<component name="meterRegistry" class="nablarch.integration.micrometer.datadog.DatadogMeterRegistryFactory">
  <property name="meterBinderListProvider" ref="meterBinderListProvider" />
  <property name="applicationDisposer" ref="disposer" />
</component>
```

**APIキー設定**：

プロパティ: `nablarch.micrometer.datadog.apiKey=XXXXXXXXXXXXXXXX`

**サイトURL設定**：

プロパティ: `nablarch.micrometer.datadog.uri=<サイトURL>`

その他の設定については `DatadogConfig(外部サイト、英語)` を参照。

**連携を無効にする**：

```
nablarch.micrometer.datadog.enabled=false
nablarch.micrometer.datadog.apiKey=XXXXXXXXXXXXXXXX
```

`nablarch.micrometer.datadog.enabled=false` で連携を無効化できる。この設定は環境変数で上書き可能なため、本番環境のみ環境変数で `true` に上書きして有効化できる。

> **重要**: 連携を無効にした場合でも、`nablarch.micrometer.datadog.apiKey` に何らかの値を設定する必要がある（ダミー値でよい）。

### CloudWatch と連携する

**依存関係**：

```xml
<dependency>
  <groupId>io.micrometer</groupId>
  <artifactId>micrometer-registry-cloudwatch2</artifactId>
  <version>1.13.0</version>
</dependency>
```

**レジストリファクトリ**：

**クラス**: `CloudWatchMeterRegistryFactory`

```xml
<component name="meterRegistry" class="nablarch.integration.micrometer.cloudwatch.CloudWatchMeterRegistryFactory">
  <property name="meterBinderListProvider" ref="meterBinderListProvider" />
  <property name="applicationDisposer" ref="disposer" />
</component>
```

**リージョンとアクセスキー設定**：

```bash
export AWS_REGION=ap-northeast-1
export AWS_ACCESS_KEY_ID=XXXXXXXXXXXXXXXXXXXXX
export AWS_SECRET_ACCESS_KEY=YYYYYYYYYYYYYYYYYYYYY
```

`micrometer-registry-cloudwatch2` は AWS SDK を使用する。リージョンやアクセスキーなどの設定は AWS SDK の方法に準拠する。詳細は [AWS SDK Java ドキュメント](https://docs.aws.amazon.com/ja_jp/sdk-for-java/v1/developer-guide/setup-credentials.html) を参照。

**名前空間設定**：

プロパティ: `nablarch.micrometer.cloudwatch.namespace=test`

その他の設定については `CloudWatchConfig(外部サイト、英語)` を参照。

**カスタムプロバイダによる詳細設定**：

`CloudWatchAsyncClientProvider` を実装することで詳細設定が可能。

```java
package example.micrometer.cloudwatch;

import nablarch.integration.micrometer.cloudwatch.CloudWatchAsyncClientProvider;
import software.amazon.awssdk.services.cloudwatch.CloudWatchAsyncClient;

public class CustomCloudWatchAsyncClientProvider implements CloudWatchAsyncClientProvider {
    @Override
    public CloudWatchAsyncClient provide() {
        return CloudWatchAsyncClient
                .builder()
                .asyncConfiguration(...) // 任意の設定
                .build();
    }
}
```

コンポーネント定義:

```xml
<component name="meterRegistry" class="nablarch.integration.micrometer.cloudwatch.CloudWatchMeterRegistryFactory">
  <property name="meterBinderListProvider" ref="meterBinderListProvider" />
  <property name="applicationDisposer" ref="disposer" />
  <property name="cloudWatchAsyncClientProvider">
    <component class="example.micrometer.cloudwatch.CustomCloudWatchAsyncClientProvider" />
  </property>
</component>
```

> **補足**: デフォルトでは `CloudWatchAsyncClient.create()` で作成されたインスタンスが使用される。

**連携を無効にする**：

```
nablarch.micrometer.cloudwatch.enabled=false
nablarch.micrometer.cloudwatch.namespace=test
```

`nablarch.micrometer.cloudwatch.enabled=false` で連携を無効化できる。環境変数で上書き可能。

> **重要**: 連携を無効にした場合でも、`nablarch.micrometer.cloudwatch.namespace` に値を設定し、環境変数 `AWS_REGION` を設定する必要がある（ダミー値でよい）。

### Azure と連携する

**Java 3.0 エージェント**：

Azure は JavaアプリケーションからAzureへのメトリクス連携方法として Java 3.0 エージェント（コード不要のアプリケーション）を提供している。このエージェントは Micrometer の [グローバルレジストリ](https://docs.micrometer.io/micrometer/reference/concepts/registry.html#_global_registry) に出力したメトリクスを自動的に収集し、Azure に連携する。

参考：
- [Azure Monitor Application Insights を監視する Java のコード不要のアプリケーション](https://learn.microsoft.com/ja-jp/azure/azure-monitor/app/opentelemetry-enable?tabs=java)
- [アプリケーションからカスタム テレメトリを送信する](https://learn.microsoft.com/ja-jp/azure/azure-monitor/app/opentelemetry-enable?tabs=java)

> **重要**: Java 3.0 エージェントは初期化処理中に大量のjarファイルをロードするため、初期化中のGCが頻発する。このため、アプリケーション起動後しばらくはGCの影響により性能が一時的に劣化する可能性がある。また、高負荷時は Java 3.0 エージェントの処理によるオーバーヘッドが性能に影響を与える可能性があるため、性能試験では本番同様に Java 3.0 エージェントを導入し、想定内の性能になることを確認する必要がある。

**MicrometerアダプタでAzureに連携する設定**：

グローバルレジストリを使うように設定する必要がある：

1. アプリケーションの起動オプションに Java 3.0 エージェントを追加する。詳細は [Azureドキュメント](https://learn.microsoft.com/ja-jp/azure/azure-monitor/app/opentelemetry-enable?tabs=java#modify-your-application) を参照。
2. `MeterRegistry` にグローバルレジストリを使うようコンポーネントを定義する

**クラス**: `GlobalMeterRegistryFactory`

```xml
<component name="meterRegistry" class="nablarch.integration.micrometer.GlobalMeterRegistryFactory">
  <property name="meterBinderListProvider" ref="meterBinderListProvider" />
  <property name="applicationDisposer" ref="disposer" />
</component>
```

この設定により、メトリクスはグローバルレジストリで収集され、Java 3.0 エージェントによってAzureに連携される。

> **補足**: Java 3.0 エージェント方式では Azure 用の `MeterRegistry` を使用しないため、Azure用のモジュールを依存関係に追加する必要がない。

**詳細設定**：

メトリクス連携は Java 3.0 エージェントが行うため、すべての設定は Java 3.0 エージェントが提供する方法で行う。詳細は [構成オプション](https://learn.microsoft.com/ja-jp/azure/azure-monitor/app/java-standalone-config) を参照。

> **重要**: 本アダプタ用の設定ファイル `micrometer.properties` は使用できないが、ファイルは配置しておく必要がある（内容は空でよい）。

**連携を無効にする**：

Java 3.0 エージェントを使用せずにアプリケーションを起動することで連携を無効化できる。

### StatsD で連携する

Datadog は DogStatsD (StatsD プロトコル) での連携をサポートしている。`micrometer-registry-statsd` モジュールで StatsD 経由で Datadog と連携できる。

参考：[Datadogドキュメント](https://docs.datadoghq.com/ja/agent/)

**依存関係**：

```xml
<dependency>
  <groupId>io.micrometer</groupId>
  <artifactId>micrometer-registry-statsd</artifactId>
  <version>1.13.0</version>
</dependency>
```

**レジストリファクトリ**：

**クラス**: `StatsdMeterRegistryFactory`

```xml
<component name="meterRegistry" class="nablarch.integration.micrometer.statsd.StatsdMeterRegistryFactory">
  <property name="meterBinderListProvider" ref="meterBinderListProvider" />
  <property name="applicationDisposer" ref="disposer" />
</component>
```

**設定**：

StatsD デーモン連携用の設定はデフォルト値が DogStatsD デフォルト構成と一致するため、DogStatsD をデフォルト構成でインストールしている場合は特に設定を明示しなくても動作する。

デフォルト構成以外でインストールしている場合は `StatsdConfig(外部サイト、英語)` を参照。

ポート変更例：
```
nablarch.micrometer.statsd.port=9999
```

**連携を無効にする**：

```
nablarch.micrometer.statsd.enabled=false
```

`nablarch.micrometer.statsd.enabled=false` で連携を無効化できる。環境変数で上書き可能。

### OpenTelemetry Protocol (OTLP) で連携する

多くの監視サービスが [OpenTelemetry](https://opentelemetry.io/ja) をサポートし、OpenTelemetry Protocol (OTLP) を使用してメトリクスを収集できる。`micrometer-registry-otlp` モジュールで OTLP 経由で様々な監視サービスと連携できる。

> **重要**: OpenTelemetry によるメトリクス収集では、連携方法の適性（利用可能性）は監視サービスによって異なるため、使用する監視サービスの情報を確認すること。

参考：
- [Datadog の OpenTelemetry](https://docs.datadoghq.com/ja/opentelemetry/)
- [New Relic による OpenTelemetry の紹介](https://docs.newrelic.com/jp/docs/opentelemetry/opentelemetry-introduction)
- [Prometheus | HTTP API | OTLP Receiver](https://prometheus.io/docs/prometheus/latest/querying/api/#otlp-receiver)

**依存関係**：

```xml
<dependency>
  <groupId>io.micrometer</groupId>
  <artifactId>micrometer-registry-otlp</artifactId>
  <version>1.13.0</version>
</dependency>
```

**レジストリファクトリ**：

**クラス**: `OtlpMeterRegistryFactory`

```xml
<component name="meterRegistry" class="nablarch.integration.micrometer.otlp.OtlpMeterRegistryFactory">
  <property name="meterBinderListProvider" ref="meterBinderListProvider" />
  <property name="applicationDisposer" ref="disposer" />
</component>
```

**URL設定**：

```
nablarch.micrometer.otlp.url=http://localhost:9090/api/v1/otlp/v1/metrics
```

**ヘッダ情報設定**：

認証で使用する API キー等が必要な場合：

```
nablarch.micrometer.otlp.headers=key1=value1,key2=value2
```

**連携を無効にする**：

```
nablarch.micrometer.otlp.enabled=false
```

`nablarch.micrometer.otlp.enabled=false` で連携を無効化できる。環境変数で上書き可能。

## アプリケーションの形式ごとに収集するメトリクスの例

## ウェブアプリケーションで収集するメトリクスの例

### HTTPリクエストの処理時間

計測によりURL別アクセス数・リクエスト処理時間を確認可能。パーセンタイル計測で大部分のリクエスト処理時間も確認可能。

:ref:`micrometer_timer_metrics_handler`、:ref:`micrometer_timer_metrics_handler_percentiles`

### SQLの処理時間

各SQLの処理時間確認と想定以上に時間かかるSQL検知が可能。

:ref:`micrometer_sql_time`

### ログレベルごとの出力回数

警告ログの異常検知（攻撃検知）・エラーログ検知が可能。

:ref:`micrometer_log_count`

### アプリケーションサーバやライブラリが提供するリソースの情報

スレッドプール・DBコネクションプール等のリソース状態をメトリクス化。JMXのMBeanで公開されている情報を活用し、障害時の原因特定に使用。

:ref:`micrometer_mbean_metrics`

## バッチアプリケーションで収集するメトリクスの例

### バッチの処理時間

平常時の処理時間を事前計測し、処理時間が異常値になったときに迅速に検知。:ref:`micrometer_default_metrics`で自動収集される`process.uptime`を使用。

### トランザクション単位の処理時間

マルチスレッドバッチの処理分散確認・処理時間逸脱時の異常検知が可能。

:ref:`micrometer_adaptor_batch_transaction_time`

### バッチの処理件数

バッチの進捗・想定速度での処理進行・想定件数の処理確認が可能。

:ref:`micrometer_batch_processed_count`

### SQLの処理時間

各SQLの処理時間確認と想定以上に時間かかるSQL検知が可能。

:ref:`micrometer_sql_time`

### ログレベルごとの出力回数

警告ログ・エラーログの検知が可能。

:ref:`micrometer_log_count`

### ライブラリが提供するリソースの情報

DBコネクションプール等のリソース状態をメトリクス化。JMXのMBeanで公開されている情報を活用し、障害時の原因特定に使用。

:ref:`micrometer_mbean_metrics`

## 処理時間を計測するハンドラ

## 処理時間を計測するハンドラ

`TimerMetricsHandler` をハンドラキューに設定することで、後続ハンドラの処理時間を計測し、平均処理時間や最大処理時間をメトリクスとして監視できるようになる。

`TimerMetricsHandler` には、`HandlerMetricsMetaDataBuilder` インタフェースを実装したクラスのインスタンスを設定する必要がある。`HandlerMetricsMetaDataBuilder` は、収集したメトリクスに設定する以下のメタ情報を構築する：

- メトリクスの名前
- メトリクスの説明
- メトリクスに設定するタグの一覧

### 実装例

```java
import io.micrometer.core.instrument.Tag;
import nablarch.fw.ExecutionContext;
import nablarch.integration.micrometer.instrument.handler.HandlerMetricsMetaDataBuilder;

import java.util.Arrays;
import java.util.List;

public class CustomHandlerMetricsMetaDataBuilder<TData, TResult>
    implements HandlerMetricsMetaDataBuilder<TData, TResult> {
  
    @Override
    public String getMetricsName() {
        return "metrics.name";
    }

    @Override
    public String getMetricsDescription() {
        return "Description of this metrics.";
    }

    @Override
    public List<Tag> buildTagList(TData param, ExecutionContext executionContext, TResult tResult, Throwable thrownThrowable) {
        return Arrays.asList(Tag.of("foo", "FOO"), Tag.of("bar", "BAR"));
    }
}
```

`getMetricsName()` と `getMetricsDescription()` は、メトリクスの名前と説明をそれぞれ返す。

`buildTagList()` はハンドラに渡されたパラメータ、後続ハンドラの実行結果、例外（例外なしの場合は `null`）を受け取り、必要に応じてこれらの情報を参照して、メトリクスに設定するタグ一覧を `List<io.micrometer.core.instrument.Tag>` で返す。

### ハンドラキュー設定

```xml
<component name="webFrontController"
           class="nablarch.fw.web.servlet.WebFrontController">
  <property name="handlerQueue">
    <list>
      <component class="nablarch.integration.micrometer.instrument.handler.TimerMetricsHandler">
        <property name="meterRegistry" ref="meterRegistry" />
        <property name="handlerMetricsMetaDataBuilder">
          <component class="xxx.CustomHandlerMetricsMetaDataBuilder" />
        </property>
      </component>
    </list>
  </property>
</component>
```

ハンドラキューに `TimerMetricsHandler` を追加し、`handlerMetricsMetaDataBuilder` プロパティに `HandlerMetricsMetaDataBuilder` の実装クラスを設定する。`meterRegistry` プロパティには、使用しているレジストリファクトリが生成した [MeterRegistry](https://micrometer.io/) を渡す。これにより、後続ハンドラの処理時間をメトリクスとして収集できるようになる。

Nablarchでは、`HandlerMetricsMetaDataBuilder` の実装として以下の機能を提供するクラスを用意している：

- :ref:`micrometer_adaptor_http_request_process_time_metrics`

## パーセンタイルを収集する

## パーセンタイルを収集する

`TimerMetricsHandler` にはパーセンタイル値を監視サービスに連携するための以下のプロパティが用意されている：

| プロパティ | 説明 |
|---|---|
| `percentiles` | 収集するパーセンタイル値のリスト（例：95パーセンタイルは `0.95` と指定） |
| `enablePercentileHistogram` | 監視サービスへのヒストグラムバケット連携フラグ。連携先がヒストグラムからのパーセンタイル計算非対応の場合は無視される |
| `serviceLevelObjectives` | ヒストグラムに追加するバケット値のリスト（単位：ms）。SLOに基づいて設定 |
| `minimumExpectedValue` | ヒストグラムバケットの最小値（単位：ms） |
| `maximumExpectedValue` | ヒストグラムバケットの最大値（単位：ms） |

> **注意**: これらのプロパティはデフォルトでは全て未設定のため、パーセンタイル情報は収集されない。パーセンタイル情報を収集する場合は、明示的に設定すること。

詳細は [Micrometer documentation](https://docs.micrometer.io/micrometer/reference/concepts/histogram-quantiles.html) を参照。

### 設定例

```xml
<component class="nablarch.integration.micrometer.instrument.handler.TimerMetricsHandler">
  <property name="meterRegistry" ref="meterRegistry" />
  <property name="handlerMetricsMetaDataBuilder">
    <component class="nablarch.integration.micrometer.instrument.http.HttpRequestTimeMetricsMetaDataBuilder" />
  </property>
  <property name="percentiles">
    <list>
      <value>0.98</value>
      <value>0.90</value>
      <value>0.50</value>
    </list>
  </property>
  <property name="enablePercentileHistogram" value="true" />
  <property name="serviceLevelObjectives">
    <list>
      <value>1000</value>
      <value>1500</value>
    </list>
  </property>
  <property name="minimumExpectedValue" value="500" />
  <property name="maximumExpectedValue" value="3000" />
</component>
```

### 出力例

ヒストグラムバケット対応の `MeterRegistry` を使用した場合の出力例：

```text
http_server_requests_seconds{class="com.nablarch.example.app.web.action.MetricsAction",exception="None",httpMethod="GET",method="index_nablarch.fw.web.HttpRequest_nablarch.fw.ExecutionContext",outcome="SUCCESS",status="200",quantile="0.98",} 1.475346432
http_server_requests_seconds{class="com.nablarch.example.app.web.action.MetricsAction",exception="None",httpMethod="GET",method="index_nablarch.fw.web.HttpRequest_nablarch.fw.ExecutionContext",outcome="SUCCESS",status="200",quantile="0.9",} 1.408237568
http_server_requests_seconds{class="com.nablarch.example.app.web.action.MetricsAction",exception="None",httpMethod="GET",method="index_nablarch.fw.web.HttpRequest_nablarch.fw.ExecutionContext",outcome="SUCCESS",status="200",quantile="0.5",} 0.737148928
http_server_requests_seconds_bucket{class="com.nablarch.example.app.web.action.MetricsAction",exception="None",httpMethod="GET",method="index_nablarch.fw.web.HttpRequest_nablarch.fw.ExecutionContext",outcome="SUCCESS",status="200",le="0.5",} 9.0
http_server_requests_seconds_bucket{class="com.nablarch.example.app.web.action.MetricsAction",exception="None",httpMethod="GET",method="index_nablarch.fw.web.HttpRequest_nablarch.fw.ExecutionContext",outcome="SUCCESS",status="200",le="1.0",} 18.0
http_server_requests_seconds_bucket{class="com.nablarch.example.app.web.action.MetricsAction",exception="None",httpMethod="GET",method="index_nablarch.fw.web.HttpRequest_nablarch.fw.ExecutionContext",outcome="SUCCESS",status="200",le="1.5",} 32.0
http_server_requests_seconds_bucket{class="com.nablarch.example.app.web.action.MetricsAction",exception="None",httpMethod="GET",method="index_nablarch.fw.web.HttpRequest_nablarch.fw.ExecutionContext",outcome="SUCCESS",status="200",le="3.0",} 32.0
http_server_requests_seconds_bucket{class="com.nablarch.example.app.web.action.MetricsAction",exception="None",httpMethod="GET",method="index_nablarch.fw.web.HttpRequest_nablarch.fw.ExecutionContext",outcome="SUCCESS",status="200",le="+Inf",} 32.0
```

> **補足**: 本アダプタが提供する `MeterRegistry` では `OtlpMeterRegistry` のみがヒストグラムバケットをサポートする。例では [PrometheusMeterRegistry](https://micrometer.io/micrometer/reference/) を使用しているが（[Prometheus](https://prometheus.io/) はヒストグラムによるパーセンタイル計算をサポート）、本アダプタでは提供していない。`PrometheusMeterRegistry` を試す場合は、以下のようなカスタムクラスを用意すること：

```java
package example.micrometer.prometheus;

import io.micrometer.prometheusmetrics.PrometheusConfig;
import io.micrometer.prometheusmetrics.PrometheusMeterRegistry;
import nablarch.core.repository.di.DiContainer;
import nablarch.integration.micrometer.MeterRegistryFactory;
import nablarch.integration.micrometer.MicrometerConfiguration;
import nablarch.integration.micrometer.NablarchMeterRegistryConfig;

public class PrometheusMeterRegistryFactory extends MeterRegistryFactory<PrometheusMeterRegistry> {

    @Override
    protected PrometheusMeterRegistry createMeterRegistry(MicrometerConfiguration micrometerConfiguration) {
        return new PrometheusMeterRegistry(new Config(prefix, micrometerConfiguration));
    }

    @Override
    public PrometheusMeterRegistry createObject() {
        return doCreateObject();
    }

    static class Config extends NablarchMeterRegistryConfig implements PrometheusConfig {

        public Config(String prefix, DiContainer diContainer) {
            super(prefix, diContainer);
        }

        @Override
        protected String subPrefix() {
            return "prometheus";
        }
    }
}
```

## あらかじめ用意されているHandlerMetricsMetaDataBuilderの実装

## あらかじめ用意されている HandlerMetricsMetaDataBuilder の実装

### HTTPリクエストの処理時間を収集する

`HttpRequestTimeMetricsMetaDataBuilder` は、HTTPリクエストの処理時間計測のためのメトリクスメタ情報を構築する。

メトリクスの名前は `http.server.requests` で、以下のタグを生成する：

| タグ名 | 説明 |
|---|---|
| `class` | リクエストを処理したアクションクラスの名前（`Class.getName()`）。取得できない場合は `UNKNOWN` |
| `method` | アクションメソッド名と引数型名を `_` で繋げた文字列（`Class.getCanonicalName()` 使用）。取得できない場合は `UNKNOWN` |
| `httpMethod` | HTTPメソッド（GET、POSTなど） |
| `status` | HTTPステータスコード |
| `outcome` | ステータスコード分類：1XX = `INFORMATION`、2XX = `SUCCESS`、3XX = `REDIRECTION`、4XX = `CLIENT_ERROR`、5XX = `SERVER_ERROR`、その他 = `UNKNOWN` |
| `exception` | スローされた例外の単純名。例外なしの場合は `None` |

#### ハンドラキュー設定例

```xml
<component name="webFrontController"
           class="nablarch.fw.web.servlet.WebFrontController">
  <property name="handlerQueue">
    <list>
      <component class="nablarch.integration.micrometer.instrument.handler.TimerMetricsHandler">
        <property name="meterRegistry" ref="meterRegistry" />
        <property name="handlerMetricsMetaDataBuilder">
          <component class="nablarch.integration.micrometer.instrument.http.HttpRequestTimeMetricsMetaDataBuilder" />
        </property>
      </component>
      <component class="nablarch.fw.web.handler.HttpCharacterEncodingHandler"/>
    </list>
  </property>
</component>
```

リクエスト全体の処理時間を計測するため、`TimerMetricsHandler` はハンドラキューの先頭に設定する必要がある。

#### 出力例

LoggingMeterRegistry を使用した場合の出力例：

```text
2020-10-06 13:52:10.309 [INFO ] i.m.c.i.l.LoggingMeterRegistry: http.server.requests{class=com.nablarch.example.app.web.action.AuthenticationAction,exception=None,httpMethod=POST,method=login_nablarch.fw.web.HttpRequest_nablarch.fw.ExecutionContext,outcome=REDIRECTION,status=303} throughput=0.2/s mean=0.4617585s max=0.4617585s
2020-10-06 13:52:10.309 [INFO ] i.m.c.i.l.LoggingMeterRegistry: http.server.requests{class=com.nablarch.example.app.web.action.IndustryAction,exception=None,httpMethod=GET,method=find,outcome=SUCCESS,status=200} throughput=0.2/s mean=0.103277s max=0.103277s
2020-10-06 13:52:10.310 [INFO ] i.m.c.i.l.LoggingMeterRegistry: http.server.requests{class=com.nablarch.example.app.web.action.AuthenticationAction,exception=None,httpMethod=GET,method=index_nablarch.fw.web.HttpRequest_nablarch.fw.ExecutionContext,outcome=SUCCESS,status=200} throughput=0.2/s mean=4.7409146s max=4.7409146s
2020-10-06 13:52:10.310 [INFO ] i.m.c.i.l.LoggingMeterRegistry: http.server.requests{class=com.nablarch.example.app.web.action.ProjectAction,exception=None,httpMethod=GET,method=index_nablarch.fw.web.HttpRequest_nablarch.fw.ExecutionContext,outcome=SUCCESS,status=200} throughput=0.2/s mean=0.5329547s max=0.5329547s
```

## バッチのトランザクション単位の処理時間を計測する

`BatchTransactionTimeMetricsLogger`を使用することで、バッチ処理のトランザクション単位の処理時間をメトリクスとして計測でき、平均処理時間や最大処理時間をモニタできる。

`BatchTransactionTimeMetricsLogger`は`Timer`を使って`batch.transaction.time`という名前でメトリクスを収集する。メトリクス名は`setMetricsName(String)`で変更可能。

メトリクスに付与されるタグ:

| タグ名 | 説明 |
|---|---|
| `class` | アクションのクラス名（:ref:`-requestPath <nablarch_batch-resolve_action>`から取得した値） |

設定例:

```xml
<component name="commitLogger"
           class="nablarch.core.log.app.CompositeCommitLogger">
  <property name="commitLoggerList">
    <list>
      <component class="nablarch.core.log.app.BasicCommitLogger">
        <property name="interval" value="${nablarch.commitLogger.interval}" />
      </component>
      <component class="nablarch.integration.micrometer.instrument.batch.BatchTransactionTimeMetricsLogger">
        <property name="meterRegistry" ref="meterRegistry" />
      </component>
    </list>
  </property>
</component>
```

`CompositeCommitLogger`を`commitLogger`という名前でコンポーネント定義し、`commitLoggerList`プロパティに`BasicCommitLogger`と`BatchTransactionTimeMetricsLogger`を設定する。

Nablarchバッチは:ref:`loop_handler`によってトランザクションのコミット間隔を制御している。トランザクションループ制御ハンドラは、トランザクションがコミットされるときに`CommitLogger`の`increment(long)`メソッドをコールする。`CommitLogger`の実体は`commitLogger`という名前でコンポーネント定義することで上書き可能。

`BatchTransactionTimeMetricsLogger`は`CommitLogger`インタフェースを実装し、`increment(long)`の呼び出し間隔を計測することでトランザクション単位の時間を計測する。

> **警告**: `BatchTransactionTimeMetricsLogger`をそのまま`commitLogger`として定義すると、デフォルトの`BasicCommitLogger`が動作しなくなる。複数の`CommitLogger`を組み合わせるには`CompositeCommitLogger`を使用し、`BasicCommitLogger`と`BatchTransactionTimeMetricsLogger`を併用する必要がある。

`LoggingMeterRegistry`を使用している場合、計測結果は以下のように出力される:

```
12 17, 2020 1:50:33 午後 io.micrometer.core.instrument.logging.LoggingMeterRegistry lambda$publish$5
情報: batch.transaction.time{class=MetricsTestAction} throughput=1/s mean=2.61463556s max=3.0790852s
```

## バッチの処理件数を計測する

`BatchProcessedRecordCountMetricsLogger` を使用すると、:ref:`nablarch_batch` が処理した入力データの件数を計測でき、進捗状況や処理速度の変化をモニタできます。

Counter を使用し、`batch.processed.record.count` という名前でメトリクスを収集します。`setMetricsName(String)` でメトリクス名を変更可能です。

**メトリクスに付与されるタグ**:

| タグ名 | 説明 |
|---|---|
| `class` | アクションのクラス名（:ref:`-requestPath <nablarch_batch-resolve_action>` から取得） |

**設定例**:

```xml
<!-- CommitLogger を複数組み合わせる -->
<component name="commitLogger"
           class="nablarch.core.log.app.CompositeCommitLogger">
  <property name="commitLoggerList">
    <list>
      <!-- デフォルトの CommitLogger を設定 -->
      <component class="nablarch.core.log.app.BasicCommitLogger">
        <property name="interval" value="${nablarch.commitLogger.interval}" />
      </component>

      <!-- 処理件数を計測する -->
      <component class="nablarch.integration.micrometer.instrument.batch.BatchProcessedRecordCountMetricsLogger">
        <property name="meterRegistry" ref="meterRegistry" />
      </component>
    </list>
  </property>
</component>
```

`CommitLogger` の仕組みを利用して処理件数を計測します。詳細は :ref:`micrometer_adaptor_batch_transaction_time` を参照してください。

**ログ出力例** (LoggingMeterRegistry使用時):

```
12 23, 2020 3:23:24 午後 io.micrometer.core.instrument.logging.LoggingMeterRegistry lambda$publish$4
情報: batch.processed.record.count{class=MetricsTestAction} throughput=10/s
12 23, 2020 3:23:34 午後 io.micrometer.core.instrument.logging.LoggingMeterRegistry lambda$publish$4
情報: batch.processed.record.count{class=MetricsTestAction} throughput=13/s
12 23, 2020 3:23:39 午後 io.micrometer.core.instrument.logging.LoggingMeterRegistry lambda$publish$4
情報: batch.processed.record.count{class=MetricsTestAction} throughput=13/s
```

## ログレベルごとの出力回数を計測する

`LogCountMetrics` を使用してログレベルごとの出力回数を計測します。

**計測の仕組み:**
- Counter を使用して `log.count` という名前でメトリクスを収集
- `MetricsMetaData` を受け取るコンストラクタで名前をカスタマイズ可能

**メトリクスに付与されるタグ:**

| タグ名 | 説明 |
|---|---|
| `level` | ログレベル |
| `logger` | LoggerManager からロガーを取得した際の名前 |

**LogPublisher の設定:**

`LogCountMetrics` はログ出力イベントを検知するために `LogPublisher` の仕組みを使用します。使用前に LogPublisher を設定する必要があります。詳細は :ref:`log-publisher_usage` を参照。

**カスタム DefaultMeterBinderListProvider の作成:**

`LogCountMetrics` は MeterBinder の実装です。`DefaultMeterBinderListProvider` を継承し、LogCountMetrics を含む MeterBinder リストを返すカスタムクラスを作成します。

```java
package example.micrometer.log;

import io.micrometer.core.instrument.binder.MeterBinder;
import nablarch.integration.micrometer.DefaultMeterBinderListProvider;
import nablarch.integration.micrometer.instrument.binder.logging.LogCountMetrics;

import java.util.ArrayList;
import java.util.List;

public class CustomMeterBinderListProvider extends DefaultMeterBinderListProvider {

    @Override
    protected List<MeterBinder> createMeterBinderList() {
        // デフォルトの MeterBinder リストに LogCountMetrics を追加
        List<MeterBinder> meterBinderList = new ArrayList<>(super.createMeterBinderList());
        meterBinderList.add(new LogCountMetrics());
        return meterBinderList;
    }
}
```

> **補足**: DefaultMeterBinderListProvider の説明については :ref:`micrometer_adaptor_declare_default_meter_binder_list_provider_as_component` を参照。

最後に、`MeterRegistryFactory` コンポーネントの `meterBinderListProvider` プロパティに、作成したカスタム DefaultMeterBinderListProvider を設定します。

**出力例 (LoggingMeterRegistry 使用時):**

```
2020-12-22 14:25:36.978 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: log.count{level=WARN,logger=com.nablarch.example.app.web.action.MetricsAction} throughput=0.4/s
2020-12-22 14:25:41.978 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: log.count{level=ERROR,logger=com.nablarch.example.app.web.action.MetricsAction} throughput=1.4/s
```

**集計対象のログレベル:**

デフォルトではログレベル WARN 以上のみが集計対象です。

`LogCountMetrics` のコンストラクタに `LogLevel` を渡してしきい値を変更できます。

```java
// （省略）
import nablarch.core.log.basic.LogLevel;

public class CustomMeterBinderListProvider extends DefaultMeterBinderListProvider {

    @Override
    protected List<MeterBinder> createMeterBinderList() {
        List<MeterBinder> meterBinderList = new ArrayList<>(super.createMeterBinderList());
        meterBinderList.add(new LogCountMetrics(LogLevel.INFO)); // LogLevel のしきい値を指定
        return meterBinderList;
    }
}
```

> **重要**: ログレベルのしきい値を下げすぎると、アプリケーションによっては大量のメトリクスが収集される可能性があります。監視サービスの料金体系によっては使用料金が増大する可能性があるため注意して設定してください。

## SQLの処理時間を計測する

`SqlTimeMetricsDaoContext` を使用することで、:ref:`universal_dao` を通じて実行したSQLの処理時間を計測できる。これにより、SQLごとの平均処理時間や最大処理時間をモニタできる。

`SqlTimeMetricsDaoContext` は Timer を使って `sql.process.time` という名前でメトリクスを収集する。このメトリクス名は、`SqlTimeMetricsDaoContextFactory` の `setMetricsName(String)` で変更できる。

**付与されるタグ**:

| タグ名 | 説明 |
|---|---|
| `sql.id` | `DaoContext` のメソッド引数に渡されたSQLID（SQLIDが無い場合は `"None"`) |
| `entity` | エンティティクラスの名前（`Class.getName()`) |
| `method` | 実行された `DaoContext` のメソッド名 |

**設定例**:

```xml
<component name="daoContextFactory"
           class="nablarch.integration.micrometer.instrument.dao.SqlTimeMetricsDaoContextFactory">
  <property name="delegate">
    <component class="nablarch.common.dao.BasicDaoContextFactory">
      <property name="sequenceIdGenerator">
        <component class="nablarch.common.idgenerator.SequenceIdGenerator" />
      </property>
    </component>
  </property>
  <property name="meterRegistry" ref="meterRegistry" />
</component>
```

`SqlTimeMetricsDaoContext` は `DaoContext` をラップすることで各データベースアクセスメソッドの処理時間を計測する。`SqlTimeMetricsDaoContextFactory` は、`DaoContext` をラップした `SqlTimeMetricsDaoContext` を生成するファクトリクラス。

`SqlTimeMetricsDaoContextFactory` を `daoContextFactory` という名前でコンポーネントとして定義することで、:ref:`universal_dao` が使用する `DaoContext` が `SqlTimeMetricsDaoContext` に置き換わる。

**出力例** (LoggingMeterRegistry使用時):

```
2020-12-23 15:00:25.161 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: sql.process.time{entity=com.nablarch.example.app.entity.Project,method=delete,sql.id=None} throughput=0.2/s mean=0.0005717s max=0.0005717s
2020-12-23 15:00:25.161 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: sql.process.time{entity=com.nablarch.example.app.entity.Project,method=findAllBySqlFile,sql.id=SEARCH_PROJECT} throughput=0.6/s mean=0.003364233s max=0.0043483s
2020-12-23 15:00:25.161 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: sql.process.time{entity=com.nablarch.example.app.web.dto.ProjectDto,method=findBySqlFile,sql.id=FIND_BY_PROJECT} throughput=0.2/s mean=0.000475s max=0.0060838s
2020-12-23 15:00:25.162 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: sql.process.time{entity=com.nablarch.example.app.entity.Industry,method=findAll,sql.id=None} throughput=0.8/s mean=0.00058155s max=0.0013081s
```

## 概要

`JmxGaugeMetrics` を使用することで、任意のMBeanから取得した値をメトリクスとして計測できる。これにより、アプリケーションサーバやライブラリが提供するMBeanから様々な情報を収集し、モニタできるようになる。

> **補足**: MBeanはJava Management Extensions(JMX)で定義されたJavaオブジェクトで、管理対象リソースへのアクセスAPIを提供する。Tomcatなどのアプリケーションサーバの多くは、サーバの状態（スレッドプール状態など）をMBeanで公開している。アプリケーションからこれらのMBeanにアクセスすることで、サーバの状態を取得できる。詳細は [Java Management Extensions ガイド](https://docs.oracle.com/javase/jp/17/jmx/java-management-extensions-jmx-user-guide.html) を参照。

JmxGaugeMetricsは [Gauge(外部サイト、英語)](https://javadoc.io/doc/io.micrometer/micrometer-core/1.13.0/io/micrometer/core/instrument/Gauge.html) を使用して、MBeanから取得した値を計測する。

## Tomcatのスレッドプールの状態を取得する

## 実装パターン

JmxGaugeMetricsは `MeterBinder` の実装クラスとして提供される。`DefaultMeterBinderListProvider` を継承したクラスを作成し、JmxGaugeMetricsを含むMeterBinderのリストを返すように実装する必要がある。

> **補足**: `DefaultMeterBinderListProvider` の説明については :ref:`micrometer_adaptor_declare_default_meter_binder_list_provider_as_component` を参照。

### 実装例

```java
package example.micrometer;

import io.micrometer.core.instrument.binder.MeterBinder;
import nablarch.integration.micrometer.DefaultMeterBinderListProvider;
import nablarch.integration.micrometer.instrument.binder.MetricsMetaData;
import nablarch.integration.micrometer.instrument.binder.jmx.JmxGaugeMetrics;
import nablarch.integration.micrometer.instrument.binder.jmx.MBeanAttributeCondition;

import java.util.ArrayList;
import java.util.List;

public class CustomMeterBinderListProvider extends DefaultMeterBinderListProvider {

    @Override
    protected List<MeterBinder> createMeterBinderList() {
        List<MeterBinder> meterBinderList = new ArrayList<>(super.createMeterBinderList());
        meterBinderList.add(new JmxGaugeMetrics(
            new MetricsMetaData("thread.count.current", "Current thread count."),
            new MBeanAttributeCondition("Catalina:type=ThreadPool,name=\"http-nio-8080\"", "currentThreadCount")
        ));
        return meterBinderList;
    }
}
```

### コンストラクタ引数

JmxGaugeMetricsのコンストラクタには、次の2つのクラスを渡す必要がある：

- `MetricsMetaData`: メトリクスの名前や説明、タグなどのメタ情報を指定
- `MBeanAttributeCondition`: 収集するMBeanを特定するためのオブジェクト名と属性名を指定

JmxGaugeMetricsは、MBeanAttributeConditionで指定された情報に基づいてMBeanの情報を取得し、MetricsMetaDataで指定された情報でメトリクスを構築する。

> **補足**: TomcatのMBeanのオブジェクト名・属性名はJConsoleで確認できる。JConsoleでTomcatを実行しているJVMに接続し「MBeans」タブを開くと、接続しているJVMで取得可能なMBeanの一覧が表示される。詳細は [モニタリングおよび管理ガイド](https://docs.oracle.com/javase/jp/17/management/using-jconsole.html) を参照。

### 計測結果（LoggingMeterRegistry使用時）

```
24-Dec-2020 16:20:24.467 情報 [logging-metrics-publisher] io.micrometer.core.instrument.logging.LoggingMeterRegistry.lambda$publish$3 thread.count.current{} value=10
```

## HikariCPのコネクションプールの状態を取得する

HikariCPはコネクションプールの情報をMBeanで参照できる機能を提供している。この機能を使用することで、JmxGaugeMetricsでコネクションプール情報を収集できる。

### MBean機能の有効化

MBeanによる情報公開を有効にするには、`com.zaxxer.hikari.HikariDataSource` の `registerMbeans` プロパティに `true` を設定する。

```xml
<?xml version="1.0" encoding="UTF-8"?>
<component-configuration
        xmlns="http://tis.co.jp/nablarch/component-configuration"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://tis.co.jp/nablarch/component-configuration https://nablarch.github.io/schema/component-configuration.xsd">
  <!-- 省略 -->

  <!-- データソース設定 -->
  <component name="dataSource"
            class="com.zaxxer.hikari.HikariDataSource" autowireType="None">
    <property name="driverClassName" value="${nablarch.db.jdbcDriver}"/>
    <property name="jdbcUrl"         value="${nablarch.db.url}"/>
    <property name="username"        value="${nablarch.db.user}"/>
    <property name="password"        value="${nablarch.db.password}"/>
    <property name="maximumPoolSize" value="${nablarch.db.maxPoolSize}"/>
    <!-- MBeanによる情報公開を有効にする -->
    <property name="registerMbeans"  value="true"/>
  </component>

</component-configuration>
```

### JmxGaugeMetricsの設定

HikariCPが公開するMBeanのオブジェクト名と属性名を指定したJmxGaugeMetricsを設定する。詳細は [HikariCPのドキュメント](https://github.com/brettwooldridge/HikariCP/wiki/MBean-(JMX)-Monitoring-and-Management) を参照。

```java
package com.nablarch.example.app.metrics;

import io.micrometer.core.instrument.binder.MeterBinder;
import nablarch.integration.micrometer.DefaultMeterBinderListProvider;
import nablarch.integration.micrometer.instrument.binder.MetricsMetaData;
import nablarch.integration.micrometer.instrument.binder.jmx.JmxGaugeMetrics;
import nablarch.integration.micrometer.instrument.binder.jmx.MBeanAttributeCondition;

import java.util.ArrayList;
import java.util.List;

public class CustomMeterBinderListProvider extends DefaultMeterBinderListProvider {

    @Override
    protected List<MeterBinder> createMeterBinderList() {
        List<MeterBinder> meterBinderList = new ArrayList<>(super.createMeterBinderList());
        // 最大数
        meterBinderList.add(new JmxGaugeMetrics(
            new MetricsMetaData("db.pool.total", "Total DB pool count."),
            new MBeanAttributeCondition("com.zaxxer.hikari:type=Pool (HikariPool-1)", "TotalConnections")
        ));
        // アクティブ数
        meterBinderList.add(new JmxGaugeMetrics(
            new MetricsMetaData("db.pool.active", "Active DB pool count."),
            new MBeanAttributeCondition("com.zaxxer.hikari:type=Pool (HikariPool-1)", "ActiveConnections")
        ));
        return meterBinderList;
    }
}
```

### 計測結果（LoggingMeterRegistry使用時）

```
2020-12-24 16:37:57.143 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: db.pool.active{} value=0
2020-12-24 16:37:57.143 [INFO ]      i.m.c.i.l.LoggingMeterRegistry: db.pool.total{} value=5
```

## サーバ起動時に出力される警告ログについて

## メトリクス連携方式の違い

Micrometerが監視サービスにメトリクスを連携する方法には、大きく次の2つが存在する：

- **Client pushes**: アプリケーションが監視サービスにメトリクスを送信（Datadog、CloudWatchなど）
- **Server polls**: 監視サービスがアプリケーションにメトリクスを問い合わせ（Prometheusなど）

## 警告ログが出力される原因

Client pushes方式では、`MeterRegistry` はコンポーネント生成後に一定間隔でメトリクスを送信開始する。一方、HikariCPのコネクションプールは、一番最初のデータベースアクセス時に初めて作成される仕様となっている。

このため、最初のデータベースアクセス前にメトリクス送信が実行されると、JmxGaugeMetricsは存在しないコネクションプールを参照することになり、Micrometerが以下のような警告ログを出力する：

```
24-Dec-2020 16:57:16.729 警告 [logging-metrics-publisher] io.micrometer.core.util.internal.logging.WarnThenDebugLogger.log Failed to apply the value function for the gauge 'db.pool.active'. Note that subsequent logs will be logged at debug level.
        java.lang.RuntimeException: javax.management.InstanceNotFoundException: com.zaxxer.hikari:type=Pool (HikariPool-1)
                at nablarch.integration.micrometer.instrument.binder.jmx.JmxGaugeMetrics.obtainGaugeValue(JmxGaugeMetrics.java:59)
                ...
```

コネクションプールが生成されていない間、メトリクスの値は `NaN` となる：

```
24-Dec-2020 17:01:31.443 情報 [logging-metrics-publisher] io.micrometer.core.instrument.logging.LoggingMeterRegistry.lambda$publish$3 db.pool.active{} value=NaN
24-Dec-2020 17:01:31.443 情報 [logging-metrics-publisher] io.micrometer.core.instrument.logging.LoggingMeterRegistry.lambda$publish$3 db.pool.total{} value=NaN
```

> **注意**: この警告ログは最初の一度だけ出力され、2回目以降は抑制される。データベースアクセスが実行されコネクションプールが生成されると、その後は正常にコネクションプール値が収集される。つまり、この警告ログはアプリケーションが正常な場合であってもタイミング次第で出力されるため、アプリケーション上の問題ではない。

## 警告ログの抑制

警告ログを抑制するには、`Initializable` を実装し、初期化時にコネクションを確立する。

```java
package example.micrometer;

import nablarch.core.log.Logger;
import nablarch.core.log.LoggerManager;
import nablarch.core.repository.initialization.Initializable;
import java.sql.SQLException;
import javax.sql.DataSource;
import java.sql.Connection;

public class CustomMeterBinderListProvider extends DefaultMeterBinderListProvider implements Initializable {
    private static final Logger LOGGER = LoggerManager.get(CustomMeterBinderListProvider.class);

    private DataSource dataSource;

    @Override
    protected List<MeterBinder> createMeterBinderList() {
        // 省略
    }

    public void setDataSource(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    @Override
    public void initialize() {
        try (Connection con = dataSource.getConnection()) {
            // 初期化時にコネクションを確立することで、MBeanが取れないことによる警告ログの出力を抑制する
        } catch (SQLException e) {
            LOGGER.logWarn("Failed initial connection.", e);
        }
    }
}
```

### コンポーネント定義の修正

```xml
<component name="meterBinderListProvider"
           class="example.micrometer.CustomMeterBinderListProvider">
  <!-- DataSource を設定する -->
  <property name="dataSource" ref="dataSource" />
</component>

<!-- 初期化が必要なコンポーネント -->
<component name="initializer"
           class="nablarch.core.repository.initialization.BasicApplicationInitializer">
  <property name="initializeList">
    <list>
      <!-- 省略 -->

      <!-- 初期化対象のコンポーネントとして追加 -->
      <component-ref name="meterBinderListProvider" />
    </list>
  </property>
</component>
```

> **補足**: メトリクス送信間隔はデフォルトで1分なので、たいていの場合メトリクス送信よりもコネクションプール生成が先行する。ただし、メトリクス送信間隔を非常に短い時間に設定している場合は、システムリポジトリ初期化前にメトリクス送信されて警告ログが出力される可能性があるため注意すること。
