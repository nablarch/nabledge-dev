# Nablarch OpenAPI Generator

## ツールの概要

Nablarch OpenAPI Generatorは、[OpenAPI](https://www.openapis.org/)ドキュメントからソースコードを生成する[OpenAPI Generator](https://openapi-generator.tech/)のGenerator実装。Nablarch RESTfulウェブサービス用のGeneratorを提供し、[OpenAPI GeneratorのMavenプラグイン](https://openapi-generator.tech/docs/plugins)に組み込み実行することでソースコードを生成する。

生成されたソースコードを使用することで、OpenAPIドキュメントで定義したREST APIのインターフェースに従ったアクションクラスの実装が容易となる。

## 前提条件

- Nablarch RESTfulウェブサービスのソースコード生成元となるOpenAPIドキュメントが作成されていること
- OpenAPIドキュメントは[OpenAPI 3.0.3](https://spec.openapis.org/oas/v3.0.3.html)仕様で記述されていること

## 動作概要

OpenAPIドキュメントを入力として指定することで、以下のソースコードを生成する。

- パスおよびオペレーション定義を元にした、リソース(アクション)インターフェース
- スキーマ定義を元にした、リクエスト、レスポンスに対応するモデル

> **補足**: OpenAPI Generatorの仕様上 `.openapi-generator-ignore`、`.openapi-generator/FILES`、`.openapi-generator/VERSION` が :ref:`NablarchOpenApiGeneratorConfiguration` の `output` で指定したディレクトリ配下に生成されるが、これらは使用しない。

## 運用方法

1. ウェブサービスの設計情報を元にOpenAPIドキュメントを作成する
2. Nablarch RESTfulウェブサービスのプロジェクトを作成し、MavenプラグインとしてOpenAPI Generatorおよび本ツールの設定を行う
3. プロジェクトをビルドし、リソース(アクション)インターフェースとモデルを生成する
4. 生成したリソース(アクション)インターフェースとモデルを使用して、Nablarch RESTfulウェブサービスの実装を行う

> **補足**: 本ツールはOpenAPIドキュメントの修正に合わせて繰り返し実行されることを想定している。アクションクラスは生成されたリソース(アクション)インターフェースを実装して作成するため、自動生成を再度行ってもアクションクラスの実装内容が失われることはない。

> **補足**: CLIでも使用可能。詳しくは :ref:`NablarchOpenApiGeneratorAsCli` を参照。

## Mavenプラグインの設定

**モジュール**:
```xml
<dependency>
  <groupId>com.nablarch.tool</groupId>
  <artifactId>nablarch-openapi-generator</artifactId>
  <version>1.0.0</version>
</dependency>
```

最低限必要な設定は `inputSpec`（入力OpenAPIドキュメントのファイルパス）と `generatorName`（`nablarch-jaxrs` を指定）の2つ。

設定例:
```xml
<plugin>
  <groupId>org.openapitools</groupId>
  <artifactId>openapi-generator-maven-plugin</artifactId>
  <version>7.10.0</version>
  <dependencies>
    <dependency>
      <groupId>com.nablarch.tool</groupId>
      <artifactId>nablarch-openapi-generator</artifactId>
      <version>1.0.0</version>
    </dependency>
  </dependencies>
  <executions>
    <execution>
      <goals><goal>generate</goal></goals>
      <configuration>
        <inputSpec>${project.basedir}/src/main/resources/openapi.yaml</inputSpec>
        <generatorName>nablarch-jaxrs</generatorName>
        <configOptions>
          <sourceFolder>src/gen/java</sourceFolder>
          <apiPackage>com.example.api</apiPackage>
          <modelPackage>com.example.model</modelPackage>
        </configOptions>
      </configuration>
    </execution>
  </executions>
</plugin>
```

> **補足**: 本ツールはOpenAPI Generator 7.10.0を使用して開発・テストしている。バージョンを変更する場合はプロジェクト側でテストを行い、問題ないことを確認すること。

## 実行方法

`mvn compile` で実行できる。

:ref:`NablarchOpenApiGeneratorConfiguration` の `sourceFolder` を明示的に設定した場合、`mvn compile` 時に生成されたソースコードがプロジェクトのコンパイル対象に含まれる（OpenAPI GeneratorのMavenプラグインによる動作）。

## 出力先

デフォルト出力先: `target/generated-sources/openapi/src/gen/java`

出力先を変更する場合は :ref:`NablarchOpenApiGeneratorConfiguration` の `output`（生成先ディレクトリ）と `sourceFolder`（`output` からの相対パス）を設定する。

## Generatorの設定項目

`configuration` タグ内直下に指定するOpenAPI Generatorの主要設定項目:

| 項目名 | 必須/任意 | デフォルト値 | 説明 |
|---|---|---|---|
| `inputSpec` | ○ | なし | 入力となるOpenAPIドキュメントのファイルパス |
| `generatorName` | ○ | なし | ソースコードを生成するGeneratorの名前。本ツールでは `nablarch-jarxrs` と指定すること |
| `output` | | `generated-sources/openapi` | ソースコードの生成先ディレクトリ |

`configOptions` タグ内に指定するツール固有の設定項目（すべて任意）:

| 項目名 | デフォルト値 | 説明 |
|---|---|---|
| `apiPackage` | `org.openapitools.api` | 生成するリソース(アクション)インターフェースのパッケージ |
| `modelPackage` | `org.openapitools.model` | 生成するモデルのパッケージ |
| `hideGenerationTimestamp` | `false` | `Generated` アノテーションに `date` 属性を付与するか否か。デフォルトではソースコード生成日時が出力される |
| `sourceFolder` | `src/gen/java` | ソースコードの生成先ディレクトリ（`output` からの相対パス）。指定すると `mvn compile` 時のコンパイル対象に含まれる |
| `useTags` | `false` | リソース(アクション)インターフェースの単位をパスではなくタグ単位とする。複数タグがある場合は最初のタグが有効 |
| `serializableModel` | `false` | 生成するモデルに `java.io.Serializable` インターフェースを実装する |
| `generateBuilders` | `false` | モデルに対するビルダークラスを生成する |
| `useBeanValidation` | `false` | OpenAPIドキュメントのバリデーション定義から :ref:`bean_validation` を使ったバリデーションを行うようにソースコードを生成する |
| `additionalModelTypeAnnotations` | なし | 生成するモデルのクラス宣言に追加のアノテーションを注釈する。複数指定は `;` 区切り |
| `additionalEnumTypeAnnotations` | なし | 生成するenum型に追加のアノテーションを注釈する。複数指定は `;` 区切り |
| `primitivePropertiesAsString` | `false` | モデルのプリミティブなデータ型のプロパティをすべて `String` として出力する |
| `supportConsumesMediaTypes` | `application/json,multipart/form-data` | リソース(アクション)インターフェースがリクエストを受け付けるメディアタイプ（`,` 区切り） |
| `supportProducesMediaTypes` | `application/json` | リソース(アクション)インターフェースがレスポンスとするメディアタイプ（`,` 区切り） |

## Bean Validationを使用するソースコードを生成する

`useBeanValidation=true` に設定することで :ref:`bean_validation` を使用するソースコードを生成できる。

設定例:
```xml
<configuration>
  <inputSpec>${project.basedir}/src/main/resources/openapi.yaml</inputSpec>
  <generatorName>nablarch-jaxrs</generatorName>
  <configOptions>
    <sourceFolder>src/gen/java</sourceFolder>
    <apiPackage>com.example.api</apiPackage>
    <modelPackage>com.example.model</modelPackage>
    <useBeanValidation>true</useBeanValidation>
  </configOptions>
</configuration>
```

`useBeanValidation` のデフォルト値は `false`。理由: OpenAPI仕様のバリデーション定義では業務要件を満たせないことが多く、相関バリデーションの定義も行えないため。

バリデーション機能を使用するソースコード生成の仕様や運用上の注意点は :ref:`openapi_property_to_bean_validation` を参照。

## CLIとして実行する

CLIとして実行するには、[OpenAPI Generator 7.10.0のJARファイル](https://repo1.maven.org/maven2/org/openapitools/openapi-generator-cli/7.10.0/openapi-generator-cli-7.10.0.jar)および[本ツールのJARファイル](https://repo1.maven.org/maven2/com/nablarch/tool/nablarch-openapi-generator/1.0.0/nablarch-openapi-generator-1.0.0.jar)をダウンロードしてjavaコマンドで実行する。

実行例:
```text
java -cp openapi-generator-cli-7.10.0.jar:nablarch-openapi-generator-1.0.0.jar org.openapitools.codegen.OpenAPIGenerator generate --generator-name nablarch-jaxrs --input-spec openapi.yaml --output out --additional-properties=apiPackage=com.example.api,modelPackage=com.example.model,useBeanValidation=true,hideGenerationTimestamp=true
```

- `--generator-name` には `nablarch-jaxrs` を指定する
- OpenAPI Generatorの設定項目はハイフン区切りの形式で指定する（例: `--generator-name`）
- 本ツール固有の設定項目は `--additional-properties` に `key=value` 形式で指定する。複数指定は `,` 区切り

利用可能なオプションの確認:
```text
java -jar openapi-generator-cli-7.10.0.jar help generate
```

## ソースコード生成仕様

> **重要**: Nablarch RESTfulウェブサービスはJakarta RESTful Web Servicesのすべてのアノテーションをサポートしていない。サポート対象のアノテーションは [restful_web_service_architecture](restful-web-service-architecture.md) およびルーティングアダプタの :ref:`router_adaptor_path_annotation` を参照すること。

## リソース(アクション)インターフェース生成仕様

:ref:`rest_feature_details-method_signature` に則った形で生成する。

**生成単位・型定義**:
- OpenAPIドキュメントのパスおよびオペレーション情報を元に生成
- Javaのインターフェースとして生成
- デフォルト: パスの第一階層でまとめた単位で生成
- `useTags: true` の場合: オペレーションのタグ単位で生成
- インターフェース宣言に `Path` アノテーションを注釈
- `Generated` アノテーションを注釈

**メソッド宣言に注釈するアノテーション**:

| アノテーション | 説明 |
|---|---|
| `GET` / `POST` / `PUT` / `DELETE` / `PATCH` / `HEAD` / `OPTIONS` | 対応するHTTPメソッドのオペレーションに注釈 |
| `Consumes` | リクエストのコンテンツタイプがある場合に注釈 |
| `Produces` | レスポンスのコンテンツタイプがあり、`type: string` かつ `format: binary` 以外の場合に注釈 |
| `Valid` | リクエストボディがあり、`useBeanValidation` が `true` の場合に注釈 |

> **補足**: `type: string` かつ `format: binary` はファイルダウンロードを意味し、コンテンツタイプは `HttpResponse#setContentType` で設定する。

**メソッド名生成仕様**:
- OpenAPIドキュメントの `operationId` 要素の値をメソッド名として使用
- `operationId` が未指定の場合はパスの値とHTTPメソッド名を組み合わせて生成

**メソッド引数生成仕様**:

| メソッド引数の型 | 説明 |
|---|---|
| リクエストモデルの型 | リクエストボディを受け取り、コンテンツタイプがマルチパート以外の場合に設定 |
| `JaxRsHttpRequest` | 常に生成し引数に設定 |
| `ExecutionContext` | 常に生成し引数に設定 |

> **補足**:
> - `PathParam` や `QueryParam` 等には対応していない。`parameters` 定義はメソッド引数に反映されず、 `JaxRsHttpRequest` から取得すること。
> - コンテンツタイプが `multipart/form-data` の場合はリクエストモデルの型の引数は生成されない。アップロードファイルは `JaxRsHttpRequest` から取得すること。

**メソッド戻り値生成仕様**:

| メソッド戻り値の型 | 説明 |
|---|---|
| `EntityResponse` | レスポンスがモデルの場合。型パラメータにモデルの型を反映 |
| `HttpResponse` | レスポンスがモデルでない場合またはHTTPステータスコードが `200` 以外の場合 |

## モデル生成仕様

**生成単位・型定義**:
- スキーマとして定義されたモデルに対して生成
- Javaのクラスとして生成
- `JsonTypeName` アノテーションを注釈
- `Generated` アノテーションを注釈

**プロパティ仕様**:
- スキーマに定義されたフィールドに対応するプロパティを生成
- getter/setterを生成し `JsonProperty` アノテーションを注釈
- メソッドチェーン可能なプロパティ設定メソッドを生成
- `useBeanValidation: true` かつバリデーション定義がある場合、 :ref:`bean_validation` を使用したバリデーションを有効化
- バリデーションアノテーションはNablarch固有の :ref:`bean_validation` とJakarta EE標準の `jakarta.validation.constraints` パッケージのものを使用

**その他の生成仕様**: `hashCode`、`equals`、`toString` メソッドを生成

## 生成されるソースコードが依存するモジュール

**モジュール**:
```xml
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-fw-jaxrs</artifactId>
</dependency>
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-core-validation-ee</artifactId>
</dependency>
<dependency>
  <groupId>jakarta.ws.rs</groupId>
  <artifactId>jakarta.ws.rs-api</artifactId>
</dependency>
<dependency>
  <groupId>jakarta.annotation</groupId>
  <artifactId>jakarta.annotation-api</artifactId>
</dependency>
<dependency>
  <groupId>com.fasterxml.jackson.core</groupId>
  <artifactId>jackson-annotations</artifactId>
  <version>2.17.1</version>
</dependency>
```

RESTfulウェブサービスのブランクプロジェクトにはこれらの依存関係がすべて含まれている。

## OpenAPIデータ型・フォーマットとJavaデータ型の対応

| OpenAPI type | OpenAPI format | Javaデータ型 |
|---|---|---|
| `integer` | (なし) | `java.lang.Integer` |
| `integer` | `int32` | `java.lang.Integer` |
| `integer` | `int64` | `java.lang.Long` |
| `number` | (なし) | `java.math.BigDecimal` |
| `number` | `float` | `java.lang.Float` |
| `number` | `double` | `java.lang.Double` |
| `boolean` | (なし) | `java.lang.Boolean` |
| `string` | (なし) | `java.lang.String` |
| `string` | `byte` | `byte[]` |
| `string` | `date` | `java.time.LocalDate` |
| `string` | `date-time` | `java.time.OffsetDateTime` |
| `string` | `number` | `java.math.BigDecimal` |
| `string` | `uuid` | `java.util.UUID` |
| `string` | `uri` | `java.net.URI` |
| `string` | (`enum` 指定時) | 対応するEnum型 |
| `array` | (なし) | `java.util.List` |
| `array` | (`uniqueItems: true`) | `java.util.Set` |
| `object` | (なし) | 対応するモデルの型 |
| `object` | (対応型なし) | `java.lang.Object` |

> **補足**:
> - `type: string` かつ `format: binary` は `multipart/form-data` のみ利用可能。それ以外のコンテンツタイプやレスポンスのモデル定義内で使用した場合はモデルの生成を中止する。
> - `type: string` の上記以外のフォーマットはすべて `java.lang.String` として生成する。

## OpenAPIバリデーション定義とBean Validationの対応

`useBeanValidation` のデフォルト値は `false`。`true` にした場合、以下の2方針でアノテーションを注釈する。

### OpenAPI仕様規定プロパティに対応するバリデーション

[OpenAPI仕様にて規定されているプロパティ](https://spec.openapis.org/oas/v3.0.3.html#properties) を使用した場合の対応表:

| OpenAPI type | OpenAPI format | OpenAPIプロパティ | バリデーションアノテーション |
|---|---|---|---|
| `integer` | (問わない) | `required` | `Required` |
| `integer` | (なし/`int32`/`int64`) | `minimum`/`maximum` | `NumberRange(min={minimum}, max={maximum})` |
| `number` | (問わない) | `required` | `Required` |
| `number` | (なし/`float`/`double`) | `minimum`/`maximum` | `DecimalRange(min="{minimum}", max="{maximum}")` |
| `boolean` | | `required` | `Required` |
| `string` | (問わない) | `required` | `Required` |
| `string` | | `minLength`/`maxLength` | `Length(min={minLength}, max={maxLength})` |
| `string` | | `pattern` | `Pattern(regexp="{pattern}")` |
| `array` | | `required` | `Required` |
| `array` | | `minItems`/`maxItems` | `Size(min={minItems}, max={maxItems})` |

> **補足**:
> - `multipleOf`、`exclusiveMinimum`、`exclusiveMaximum`、`minProperties`、`maxProperties` には対応していない。
> - `minimum`/`maximum`、`minLength`/`maxLength`、`minItems`/`maxItems` はどちらか片方だけでも指定可能。
> - Javaのデータ型が `java.math.BigDecimal`、`java.util.List`、`java.util.Set` またはモデルの場合は `Valid` アノテーションを注釈する。
> - `Pattern` のみJakarta Bean Validation標準のアノテーション。それ以外はNablarch固有のアノテーション。

### ドメインバリデーション

[OpenAPI仕様の拡張プロパティ](https://spec.openapis.org/oas/v3.0.3.html#specification-extensions) `x-nablarch-domain` を使用して :ref:`bean_validation-domain_validation` をサポート。値にはドメイン名を指定する。

```yaml
propertyName:
  type: string
  x-nablarch-domain: "domainName"
```

`useBeanValidation: true` でソースコードを生成すると、対象プロパティに `Domain("{domainName}")` が注釈される。

> **重要**: `x-nablarch-domain` を指定したプロパティに `minimum`、`maximum`、`minLength`、`maxLength`、`minItems`、`maxItems`、`pattern` のいずれかが指定されている場合はソースコードの生成を中止する（ドメインに含まれるバリデーションルールと重複するため）。`required` との併用は可能。

## バリデーションに関する運用上の注意点

### 項目単位・相関バリデーションが不足する場合

OpenAPI仕様で規定されているバリデーションは必須定義・長さチェック・正規表現のみで、業務アプリケーションが求める要件には不足する場合がある。自動生成ソースコードを直接修正することは望ましくないため、ドメインバリデーションを使用しても生成されたモデルに相関バリデーションを実装できない。結果として自動生成モデルと手動実装フォーム等でバリデーション定義が分散されやすい点に注意すること。

> **重要**: 本ツールがデフォルトでバリデーション用アノテーションを注釈しないのは、バリデーション定義が分散される状況が生まれやすいことを想定しているためである。

**バリデーション定義を含めない場合の実装方法** ( :ref:`bean_validation-execute_explicitly` と同様の考え方):

```java
public class ProjectAction implements ProjectsApi {
    @Override
    public EntityResponse<ProjectResponse> createProject(ProjectCreateRequest projectCreateRequest, JaxRsHttpRequest jaxRsHttpRequest, ExecutionContext context) {
        ProjectCreateForm form;
        try {
            form = ProjectValidatorUtil.validate(ProjectCreateForm.class, projectCreateRequest);
        } catch (ApplicationException e) {
            throw e;
        }
        return response;
    }
}

public final class ProjectValidatorUtil {
    public static <T> T validate(Class<T> beanClass, Object src) {
        T bean = BeanUtil.createAndCopy(beanClass, src);
        ValidatorUtil.validate(bean);
        return bean;
    }
}
```

### ドメインバリデーションを使用する場合の注意点

ドメインバリデーションを使用するとOpenAPI仕様でサポートしていないバリデーションを使用できる。ただし、OpenAPIドキュメントからバリデーション仕様が見えなくなる可能性がある点に注意すること。

## OpenAPIドキュメントのパスおよびオペレーションの定義とソースコードの生成例

## Maven設定例

```xml
<configuration>
  <inputSpec>${project.basedir}/src/main/resources/openapi.yaml</inputSpec>
  <generatorName>nablarch-jaxrs</generatorName>
  <configOptions>
    <sourceFolder>src/gen/java</sourceFolder>
    <apiPackage>com.example.api</apiPackage>
    <modelPackage>com.example.model</modelPackage>
  </configOptions>
</configuration>
```

## パスおよびオペレーション定義 → 生成インターフェース

OpenAPIドキュメント例:
```yaml
/projects:
  post:
    operationId: createProject
    requestBody:
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ProjectCreateRequest'
    responses:
      "200":
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ProjectResponse'
/projects/{id}:
  get:
    operationId: findProjectById
    parameters:
    - name: id
      in: path
      required: true
      schema:
        type: string
    responses:
      "200":
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ProjectResponse'
      "404":
        description: プロジェクトが見つからなかった場合
```

生成されるリソース(アクション)インターフェース例:
```java
@Path("/projects")
public interface ProjectsApi {
    @POST
    @Consumes({ "application/json" })
    @Produces({ "application/json" })
    EntityResponse<ProjectResponse> createProject(ProjectCreateRequest projectCreateRequest, JaxRsHttpRequest jaxRsHttpRequest, ExecutionContext context);

    @GET
    @Path("/{id}")
    @Produces({ "application/json" })
    EntityResponse<ProjectResponse> findProjectById(JaxRsHttpRequest jaxRsHttpRequest, ExecutionContext context);
}
```

## OpenAPIドキュメントのスキーマの定義とソースコードの生成例

## スキーマ定義 → 生成モデル

OpenAPIドキュメント例:
```yaml
ProjectResponse:
  type: object
  properties:
    id:
      format: uuid
      type: string
    name:
      type: string
    sales:
      format: int64
      type: integer
    startDate:
      format: date
      type: string
    endDate:
      format: date
      type: string
```

生成されるモデル例(`uuid`→`UUID`、`int64`→`Long`、`date`→`LocalDate`):
```java
@JsonTypeName("ProjectResponse")
public class ProjectResponse {
    private UUID id;
    private String name;
    private Long sales;
    private LocalDate startDate;
    private LocalDate endDate;
    // builderメソッド、getter/setterに@JsonPropertyアノテーションが付与
}
```

## Bean Validationを使用するソースコードの生成例

## Bean Validationを使用する生成例

`useBeanValidation=true`を設定:
```xml
<configOptions>
  <!-- Bean Validationを使用する場合はuseBeanValidationにtrueを指定する -->
  <useBeanValidation>true</useBeanValidation>
</configOptions>
```

- OpenAPIの`required`フィールドのgetterに`@Required`が付与される
- `maxLength`/`minLength`制約のgetterに`@Length(min=..., max=...)`が付与される
- HTTPボディでリクエストを受け取るメソッドに`@Valid`が付与される

生成されるモデル例:
```java
@JsonTypeName("ProjectCreateRequest")
public class ProjectCreateRequest {
    ...
    @JsonProperty("projectName")
    @Required @Length(min = 1, max = 100)
    public String getProjectName() { return projectName; }

    @JsonProperty("startDate")
    @Required
    public LocalDate getStartDate() { return startDate; }

    @JsonProperty("endDate")
    public LocalDate getEndDate() { return endDate; }  // requiredでないためアノテーションなし
}
```

生成されるインターフェース例:
```java
@POST
@Consumes({ "application/json" })
@Produces({ "application/json" })
@Valid
EntityResponse<ProjectResponse> createProject(ProjectCreateRequest projectCreateRequest, JaxRsHttpRequest jaxRsHttpRequest, ExecutionContext context);
```

## ドメインバリデーションを使用するソースコードの生成例

## ドメインバリデーションを使用する生成例

`useBeanValidation=true`設定で、OpenAPIの`x-nablarch-domain`拡張プロパティにドメイン名を指定すると`@Domain`アノテーションが付与される:

```yaml
properties:
  projectName:
    type: string
    x-nablarch-domain: "projectName"
```

生成されるモデル例:
```java
@JsonTypeName("ProjectCreateRequest")
public class ProjectCreateRequest {
    ...
    @JsonProperty("projectName")
    @Required @Domain("projectName")
    public String getProjectName() { return projectName; }
}
```

## ファイルアップロードの定義例

## ファイルアップロードの定義例

> **補足**: ファイルアップロードの場合、リクエストのコンテンツタイプには`multipart/form-data`を指定する。またアップロードファイルには`type: string`かつ`format: binary`を指定する。この時、スキーマに対応するモデルのソースコードは生成されない。アップロードされたファイルは`JaxRsHttpRequest`より取得する。

OpenAPIドキュメント例:
```yaml
/customers/upload:
  post:
    operationId: uploadCustomersCsvFile
    requestBody:
      content:
        multipart/form-data:
          schema:
            $ref: '#/components/schemas/CustomersCsvFileUploadRequest'
    responses:
      "200":
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CustomersCsvFileUploadResultResponse'
```

スキーマのファイルフィールド定義(`format: binary`でモデル生成対象外):
```yaml
CustomersCsvFileUploadRequest:
  properties:
    fileName:
      type: string
    file:
      type: string
      format: binary
```

生成されるインターフェース例(スキーマモデルは生成されず、JaxRsHttpRequestのみ受け取る):
```java
@POST
@Consumes({ "multipart/form-data" })
@Produces({ "application/json" })
EntityResponse<CustomersCsvFileUploadResultResponse> uploadCustomersCsvFile(JaxRsHttpRequest jaxRsHttpRequest, ExecutionContext context);
```

## ファイルダウンロードの定義例

## ファイルダウンロードの定義例

> **補足**: ファイルダウンロードではレスポンスのコンテンツタイプは任意となる。レスポンスのスキーマ定義は`type: string`かつ`format: binary`とし、ダウンロードするファイルの内容やレスポンスヘッダは`HttpResponse`を使って設定する。

OpenAPIドキュメント例:
```yaml
/customers/upload:
  get:
    operationId: downloadCustomersCsvFile
    responses:
      "200":
        content:
          text/csv:
            schema:
              type: string
              format: binary
```

生成されるインターフェース例(戻り値はHttpResponse):
```java
@GET
HttpResponse downloadCustomersCsvFile(JaxRsHttpRequest jaxRsHttpRequest, ExecutionContext context);
```
