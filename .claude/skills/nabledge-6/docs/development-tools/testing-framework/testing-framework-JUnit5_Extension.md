# JUnit 5用拡張機能

## 概要

JUnit 5で書かれたテストの中で自動テストフレームワークを使用するための拡張機能。パラメータ化テストなどJUnit 5が提供する機能と自動テストフレームワークを組み合わせて使用できる。

> **補足**: 本拡張機能を導入してもJUnit 4で書かれた既存テストを修正する必要はない。JUnit Vintageを使うことで既存のJUnit 4テストはJUnit 5上で引き続き実行可能（:ref:`run_ntf_on_junit5_with_vintage_engine` 参照）。既存テストはJUnit 4のままにしておき、新規テストのみJUnit 5で実装できる。

## 前提条件

- maven-surefire-plugin 2.22.0以上

## モジュール一覧

**モジュール**:
```xml
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-testing-junit5</artifactId>
  <scope>test</scope>
</dependency>
```

## 基本的な使い方

各自動テストフレームワーククラスに対応するExtensionクラスと合成アノテーションを提供。使い方:

1. 対応する合成アノテーション（例: `NablarchTest`）をテストクラスに設定する
2. 使用するクラス（例: `TestSupport`）のインスタンスフィールドをテストクラスに宣言する（可視性は任意）
3. 拡張機能がテスト実行前にインスタンスを生成し、代入可能なフィールドへ自動インジェクションする

```java
@NablarchTest
class YourTest {
    TestSupport support;

    @Test
    void test() {
        Map<String, String> map = support.getMap(sheetName, id);
    }
}
```

> **警告**: インジェクション対象フィールドがnullでない場合、拡張機能はエラー終了するので値は設定しないこと。

## Extensionクラスと合成アノテーションの一覧

| 自動テストフレームワークが提供するクラス | Extensionクラス | 合成アノテーション |
|---|---|---|
| `TestSupport` | `TestSupportExtension` | `NablarchTest` |
| `BatchRequestTestSupport` | `BatchRequestTestExtension` | `BatchRequestTest` |
| `DbAccessTestSupport` | `DbAccessTestExtension` | `DbAccessTest` |
| `EntityTestSupport` | `EntityTestExtension` | `EntityTest` |
| `BasicHttpRequestTestTemplate` | `BasicHttpRequestTestExtension` | `BasicHttpRequestTest` |
| `HttpRequestTestSupport` | `HttpRequestTestExtension` | `HttpRequestTest` |
| `RestTestSupport` | `RestTestExtension` | `RestTest` |
| `SimpleRestTestSupport` | `SimpleRestTestExtension` | `SimpleRestTest` |
| `IntegrationTestSupport` | `IntegrationTestExtension` | `IntegrationTest` |
| `MessagingReceiveTestSupport` | `MessagingReceiveTestExtension` | `MessagingReceiveTest` |
| `MessagingRequestTestSupport` | `MessagingRequestTestExtension` | `MessagingRequestTest` |

## BasicHttpRequestTestの補足

`BasicHttpRequestTest` 使用時は `baseUri` パラメータの指定が必要。この値は `AbstractHttpRequestTestTemplate` の `getBaseUri()` の戻り値に対応する。

```java
@BasicHttpRequestTest(baseUri = "/test/")
class YourTestClass {
    BasicHttpRequestTestTemplate support;

    @Test
    void test() {
        support.execute();
    }
}
```

## 独自の拡張を加える

独自の拡張を追加する手順:

1. 自動テストフレームワークのクラスを継承し、独自拡張クラスを作成する
2. 継承元クラスに対応するExtensionクラスを継承した独自拡張用Extensionを作成し、独自拡張クラスのインスタンスを生成するように実装する
3. `@ExtendWith`アノテーションで独自ExtensionクラスをテストクラスにApplyする

**独自拡張クラスの作成**: フレームワーク提供クラスはインスタンス生成時にテストクラスの`Class`オブジェクトを渡す必要がある。独自拡張クラスにはテストクラスの`Class`オブジェクトを受け取るコンストラクタを定義すること。

> **補足**: `SimpleRestTestSupport` は、テストクラスの`Class`オブジェクトをコンストラクタで渡さなくても使用できる。

`TestSupport` を継承した場合の例:

```java
public class CustomTestSupport extends TestSupport {
    public CustomTestSupport(Class<?> testClass) {
        super(testClass);
    }
}
```

**独自拡張用Extensionの作成**: 継承元クラスに対応するExtensionクラスを継承する。`TestSupport` を継承した場合、対応Extensionは `TestSupportExtension` となる。

> **補足**: `AbstractHttpRequestTestTemplate` を直接継承した場合、対応Extensionとして `BasicHttpRequestTestExtension` が使用できる。

`createSupport()`をオーバーライドして独自拡張クラスのインスタンスを返す。生成したインスタンスは `TestEventDispatcherExtension` の`support`フィールド（`protected`の `TestEventDispatcher` 型）に保存される。サブクラスから参照可能。

```java
public class CustomTestSupportExtension extends TestSupportExtension {
    @Override
    protected TestEventDispatcher createSupport(Object testInstance, ExtensionContext context) {
        return new CustomTestSupport(testInstance.getClass());
    }
}
```

**@ExtendWithでテストクラスに適用する**:

```java
@ExtendWith(CustomTestSupportExtension.class)
class YourTest {
    CustomTestSupport support;

    @Test
    void test() {
        support.customMethod();
    }
}
```

**BasicHttpRequestTestTemplateを拡張する場合**: `BasicHttpRequestTestTemplate` または `AbstractHttpRequestTestTemplate` を拡張する場合、`baseUri`を独自拡張クラスのインスタンスに連携する必要がある。`@ExtendWith`ではパラメータの連携ができないため、合成アノテーションも独自に作成する必要がある。

独自拡張クラス（`baseUri`をコンストラクタで受け取る）:

```java
public class CustomHttpRequestTestSupport extends BasicHttpRequestTestTemplate {
    private final String baseUri;

    public CustomHttpRequestTestSupport(Class<?> testClass, String baseUri) {
        super(testClass);
        this.baseUri = baseUri;
    }

    @Override
    protected String getBaseUri() {
        return baseUri;
    }
}
```

合成アノテーション（`@ExtendWith`で独自Extensionを指定し、`baseUri`をパラメータとして宣言）:

```java
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.TYPE)
@ExtendWith(CustomHttpRequestTestExtension.class)
public @interface CustomHttpRequestTest {
    String baseUri();
}
```

独自拡張用Extension（`findAnnotation(Object, Class)`でアノテーション情報を取得して`baseUri`を連携）:

```java
public class CustomHttpRequestTestExtension extends BasicHttpRequestTestExtension {
    @Override
    protected TestEventDispatcher createSupport(Object testInstance, ExtensionContext context) {
        CustomHttpRequestTest annotation = findAnnotation(testInstance, CustomHttpRequestTest.class);
        return new CustomHttpRequestTestSupport(testInstance.getClass(), annotation.baseUri());
    }
}
```

使用例:

```java
@CustomHttpRequestTest(baseUri = "/custom/")
class YourTest {
    CustomHttpRequestTestSupport support;

    @Test
    void test() {
        support.customMethod();
    }
}
```

**事前処理・事後処理の実装**: 独自拡張用Extensionで以下のメソッドをオーバーライドすることで事前・事後処理を実装できる:

- `beforeAll` / `afterAll`: テストクラス全体の事前・事後処理
- `beforeEach` / `afterEach`: テストメソッドごとの事前・事後処理

> **重要**: オーバーライド時は必ず最初に親クラスの同メソッドを呼び出すこと。呼び出さない場合、親クラスで定義された事前・事後処理が実行されなくなる。

```java
@Override
public void beforeAll(ExtensionContext context) {
    super.beforeAll(context);
    // 独自の事前処理
}
```

**JUnit 4のTestRuleを再現する**: 独自拡張クラス内でJUnit 4の`TestRule`（`@Rule`付き）を使用している場合、`resolveTestRules()`をオーバーライドしてリストに追加することでJUnit 5上でも再現できる。

> **重要**: `resolveTestRules()`オーバーライド時は、必ず`super.resolveTestRules()`の結果をベースにすること。そうしない場合、親クラスで登録している`TestRule`が再現されなくなる。

```java
public class CustomTestSupportExtension extends TestSupportExtension {
    @Override
    protected TestEventDispatcher createSupport(Object testInstance, ExtensionContext context) {
        return new CustomTestSupport(testInstance.getClass());
    }

    @Override
    protected List<TestRule> resolveTestRules() {
        List<TestRule> rules = new ArrayList<>(super.resolveTestRules());
        rules.add(((CustomTestSupport) support).timeout);
        return rules;
    }
}
```

## RegisterExtensionで使用する

RegisterExtensionを使用してExtensionのインスタンスを手続き的に生成してテストクラスに適用できる。

> **重要**: RegisterExtensionを使用する場合は必ず`static`フィールドで使用すること。インスタンスフィールドで使用した場合、`beforeAll`や`afterAll`などの処理が実行されず、Extensionが正常に動作しなくなる。

```java
class YourTest {
    @RegisterExtension
    static TestSupportExtension extension = new TestSupportExtension();

    TestSupport support;

    @Test
    void test() {
        // support を使用
    }
}
```

> **補足**: RegisterExtensionについては、[公式ガイドの「5.2.2. Programmatic Extension Registration」](https://junit.org/junit5/docs/5.11.0/user-guide/#extensions-registration-programmatic)を参照のこと。
