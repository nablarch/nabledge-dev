sections_contentが取得できました。全ファイル読み込み完了。Step 5: 回答を生成します。

---

Step 5: 回答生成（sections_contentをもとに）

---

## REST APIでJSONを受け取ってDBに登録する処理の仕組み

Nablarchでは、**Jakarta RESTful Web Servicesサポート**という機能を使ってRESTful APIを作成します。以下に、JSONを受け取ってDBに登録するまでの全体的な仕組みと動作を解説します。

---

### 全体の処理の流れ

リクエスト到着からレスポンス返却まで、以下のようにハンドラキューを通じて処理されます。

1. WebフロントコントローラがPOSTリクエストを受信
2. **ルーティングアダプタ** (`PathOptionsProviderRoutesMapping`) が `@Path` / `@POST` アノテーションを元に呼び出すアクションクラスを決定
3. **リクエストボディ変換ハンドラ** (`BodyConvertHandler`) がJSON文字列をフォームクラス（Java Bean）に変換
4. **Bean Validationハンドラ** (`JaxRsBeanValidationHandler`) が変換されたフォームに対して `@Valid` を使いバリデーション実行
5. アクションクラスのメソッドが呼ばれ、`UniversalDao.insert()` でDBに登録
6. `HttpResponse` を返却し、**JaxRsResponseHandler** がレスポンスをクライアントに書き込む

---

### 最小ハンドラ構成

RESTful APIに必要なハンドラの順序は以下のとおりです。

| No. | ハンドラ | 役割 |
|-----|---------|------|
| 1 | グローバルエラーハンドラ | 実行時例外のログ出力 |
| 2 | JaxRsResponseHandler | レスポンス書き込み・エラーレスポンス生成 |
| 3 | データベース接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクション開始・コミット・ロールバック |
| 5 | ルーティングアダプタ | URIからアクションメソッドを決定 |
| 6 | リクエストボディ変換ハンドラ | JSONボディ → Formクラス変換 |
| 7 | Bean Validationハンドラ | Formクラスへのバリデーション実行 |

> **Tip:** Jakarta RESTful Web Servicesアダプタ（`JerseyJaxRsHandlerListFactory` または `ResteasyJaxRsHandlerListFactory`）を使うと、6番と7番のハンドラが自動でハンドラキューに追加されます。

---

### 各コンポーネントの仕組み

#### 1. ルーティング設定（`@Path` アノテーション）

`PathOptionsProviderRoutesMapping` を使うと、Javaのアノテーションでルーティングを定義できます。

```java
@Path("/projects")
public class ProjectAction {
    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    @Valid
    public HttpResponse save(ProjectForm project) {
        // ...
    }
}
```

`@Path("/projects")` でURLパスを定義し、`@POST` でHTTPメソッドを指定します。

#### 2. JSONボディの変換（`BodyConvertHandler` + `Jackson2BodyConverter`）

`BodyConvertHandler` はリクエストボディをアクションで受け取るFormクラスに変換します。JSON変換には `Jackson2BodyConverter` が使用されます。

```xml
<component class="nablarch.fw.jaxrs.BodyConvertHandler">
  <property name="bodyConverters">
    <list>
      <component class="nablarch.integration.jaxrs.jackson.Jackson2BodyConverter"/>
    </list>
  </property>
</component>
```

アクション側では `@Consumes(MediaType.APPLICATION_JSON)` を指定することで、このコンバータが機能します。

> **Tip:** `JerseyJaxRsHandlerListFactory` を使った場合、`Jackson2BodyConverter` はJSON/XMLコンバータも含めて自動設定されます。

#### 3. バリデーション（`JaxRsBeanValidationHandler` + `@Valid`）

変換後のFormに対してバリデーションを実行するには、アクションメソッドに `@Valid` アノテーションを付けます。

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

`@Valid` があるメソッドに対して、`JaxRsBeanValidationHandler` がBean Validationを実行します。バリデーションエラーが発生すると、後続処理には進まず `ApplicationException` が送出されます。

#### 4. DBへの登録（`UniversalDao`）

`UniversalDao.insert()` を使うと、SQLを書かずにEntityをDBに登録できます。

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(ProjectForm project) {
    // BeanUtilでフォームをEntityに変換してからinsert
    UniversalDao.insert(BeanUtil.createAndCopy(Project.class, project));
    return new HttpResponse(HttpResponse.Status.CREATED.getStatusCode());
}
```

通常、受け取るFormクラス（バリデーション用）を一度`BeanUtil.createAndCopy()`でEntityクラス（DB登録用）に変換してから `insert()` します。

#### 5. トランザクション制御（`TransactionManagementHandler`）

`TransactionManagementHandler` はリクエスト処理の開始時にトランザクションを開始し、正常終了時はコミット、例外発生時はロールバックします。設定例：

```xml
<component class="nablarch.common.handler.TransactionManagementHandler">
  <property name="transactionFactory" ref="databaseTransactionFactory" />
</component>
```

---

### 完全な実装例（まとめ）

```java
@Path("/projects")
public class ProjectAction {

    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    @Valid
    public HttpResponse save(ProjectForm project) {
        UniversalDao.insert(BeanUtil.createAndCopy(Project.class, project));
        return new HttpResponse(HttpResponse.Status.CREATED.getStatusCode());
    }
}
```

- `@Path("/projects")` + `@POST` → POSTリクエストをこのメソッドにルーティング
- `@Consumes(MediaType.APPLICATION_JSON)` → リクエストボディをJSONとして受け取る
- `@Valid` → Formクラスに対してBean Validationを実行
- `BeanUtil.createAndCopy()` → FormクラスをEntityクラスに変換
- `UniversalDao.insert()` → EntityをDBにINSERT
- `HttpResponse(201)` → 登録成功を示す201レスポンスを返却

---

Step 6: verify実行

回答の主張をsections_contentと照合します。

- `@Consumes(MediaType.APPLICATION_JSON)` でJSONを受け取る → handlers-body-convert-handler.json#s5, getting-started-create#s1 に記載あり ✅
- `@Valid` でBean Validation → handlers-jaxrs-bean-validation-handler.json#s4 に記載あり ✅
- `UniversalDao.insert()` でDB登録 → libraries-universal-dao.json#s2 に記載あり ✅
- `BeanUtil.createAndCopy()` でForm→Entity変換 → getting-started-create#s1 に記載あり ✅
- `JerseyJaxRsHandlerListFactory` が自動設定 → adapters-jaxrs-adaptor.json#s2 に記載あり ✅
- 最小ハンドラ構成テーブル → restful-web-service-architecture.json#s4 に記載あり ✅
- `HttpResponse(201)` → getting-started-create#s1 に `HttpResponse.Status.CREATED.getStatusCode()` が明示されている ✅
- `TransactionManagementHandler` のXML設定例 → handlers-transaction-management-handler.json#s4 に記載あり ✅
- `PathOptionsProviderRoutesMapping` でアノテーションルーティング → adapters-router-adaptor.json#s7/s8 に記載あり ✅

**verify結果: PASS**

Step 7: PASSのため、final_answer = 上記の回答。

Step 8: 出力。

---

REST APIでJSONを受け取ってDBに登録する処理の仕組みを解説します。

## REST APIでJSONを受け取ってDBに登録する処理の仕組み

Nablarchでは、**Jakarta RESTful Web Servicesサポート**という機能でRESTful APIを実装します。

---

### 全体の処理の流れ

POSTリクエスト到着からDBへの登録・レスポンス返却まで、以下の順でハンドラキューを経由します。

1. WebフロントコントローラがPOSTリクエストを受信
2. **ルーティングアダプタ** が `@Path` / `@POST` アノテーションを元に呼び出すアクションメソッドを決定
3. **リクエストボディ変換ハンドラ** (`BodyConvertHandler`) がJSON文字列をフォームクラス（Java Bean）に変換
4. **Bean Validationハンドラ** (`JaxRsBeanValidationHandler`) が `@Valid` アノテーションのあるメソッドに対してバリデーションを実行
5. アクションクラスのメソッドが呼ばれ、`UniversalDao.insert()` でDBに登録
6. `JaxRsResponseHandler` がレスポンスをクライアントに書き込む

---

### 最小ハンドラ構成

RESTful APIを動かすために必要なハンドラの順序です。

| No. | ハンドラ | 役割 |
|-----|---------|------|
| 1 | グローバルエラーハンドラ | 実行時例外のログ出力 |
| 2 | JaxRsResponseHandler | レスポンス書き込み・エラーレスポンス生成 |
| 3 | データベース接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクション開始・コミット・ロールバック |
| 5 | ルーティングアダプタ | URIからアクションメソッドを決定 |
| 6 | リクエストボディ変換ハンドラ | JSONボディ → Formクラス変換 |
| 7 | Bean Validationハンドラ | Formクラスへのバリデーション実行 |

> **Tip:** `JerseyJaxRsHandlerListFactory`（または `ResteasyJaxRsHandlerListFactory`）を使うと、6番・7番のハンドラが自動でハンドラキューに追加されます。

---

### 各コンポーネントの仕組み

#### 1. ルーティング（`@Path` アノテーション）

`PathOptionsProviderRoutesMapping` を使うと、Javaアノテーションでルーティングを定義できます。

```java
@Path("/projects")
public class ProjectAction {
    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    @Valid
    public HttpResponse save(ProjectForm project) {
        // ...
    }
}
```

`@Path` でURLパスを、`@POST` でHTTPメソッドを指定します。

#### 2. JSONボディの変換（`BodyConvertHandler` + `Jackson2BodyConverter`）

`BodyConvertHandler` はリクエストボディをFormクラスに変換します。JSON変換には `Jackson2BodyConverter` が使われます。

```xml
<component class="nablarch.fw.jaxrs.BodyConvertHandler">
  <property name="bodyConverters">
    <list>
      <component class="nablarch.integration.jaxrs.jackson.Jackson2BodyConverter"/>
    </list>
  </property>
</component>
```

アクション側で `@Consumes(MediaType.APPLICATION_JSON)` を指定することで、このコンバータが機能します。

#### 3. バリデーション（`@Valid` + `JaxRsBeanValidationHandler`）

アクションメソッドに `@Valid` を付けると、変換後のFormに対してBean Validationが実行されます。バリデーションエラーが発生した場合は `ApplicationException` が送出され、後続処理には進みません。

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

#### 4. DBへの登録（`UniversalDao`）

`UniversalDao.insert()` を使うと、SQLを書かずにEntityをDBに登録できます。Formクラスをそのまま渡す場合と、`BeanUtil.createAndCopy()` でEntityに変換してから渡す場合があります。

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(ProjectForm project) {
    // FormクラスをEntityクラスに変換してからinsert
    UniversalDao.insert(BeanUtil.createAndCopy(Project.class, project));
    return new HttpResponse(HttpResponse.Status.CREATED.getStatusCode());
}
```

#### 5. トランザクション制御（`TransactionManagementHandler`）

`TransactionManagementHandler` はリクエスト処理の開始時にトランザクションを開始し、正常終了時はコミット、例外発生時はロールバックします。

```xml
<component class="nablarch.common.handler.TransactionManagementHandler">
  <property name="transactionFactory" ref="databaseTransactionFactory" />
</component>
```

---

### まとめ：完全な実装例

```java
@Path("/projects")
public class ProjectAction {

    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    @Valid
    public HttpResponse save(ProjectForm project) {
        UniversalDao.insert(BeanUtil.createAndCopy(Project.class, project));
        return new HttpResponse(HttpResponse.Status.CREATED.getStatusCode());
    }
}
```

| アノテーション/クラス | 役割 |
|---|---|
| `@Path` + `@POST` | POSTリクエストのルーティング |
| `@Consumes(APPLICATION_JSON)` | JSONリクエストボディの受け取り |
| `@Valid` | フォームのBean Validationを起動 |
| `BeanUtil.createAndCopy()` | FormクラスをEntityクラスに変換 |
| `UniversalDao.insert()` | EntityをDBにINSERT（SQLなし） |
| `new HttpResponse(201)` | 201 Createdレスポンスを返却 |

---

参照:
- [アーキテクチャ概要](processing-pattern/restful-web-service/restful-web-service-architecture.json)
- [登録機能の作成](processing-pattern/restful-web-service/restful-web-service-getting-started-create.json)
- [リクエストボディ変換ハンドラ](component/handlers/handlers-body-convert-handler.json)
- [Jakarta RESTful Web Services Bean Validationハンドラ](component/handlers/handlers-jaxrs-bean-validation-handler.json)
- [ユニバーサルDAO](component/libraries/libraries-universal-dao.json)
- [Jakarta RESTful Web Servicesアダプタ](component/adapters/adapters-jaxrs-adaptor.json)
- [ルーティングアダプタ](component/adapters/adapters-router-adaptor.json)