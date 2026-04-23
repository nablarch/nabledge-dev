**結論**: RESTfulウェブサービスでのJSON入力値検証には Bean Validation（`@Valid` アノテーション）を使用し、エラーレスポンスは `ErrorResponseBuilder` をカスタマイズして返すのが推奨パターン。

**根拠**:

1. **バリデーションの設定方法**: リソースクラスのメソッドまたはFormクラスを受け取るパラメータに `@Valid` アノテーションを付与することで、受信したJSONのBean Validationが自動実行される。
   ```java
   @Path("/sample")
   public class SampleResource {
       @POST
       public void register(@Valid SampleForm form) { ... }
   }
   ```
   (`component/libraries/libraries-bean_validation.json:s14`)

   ハンドラ側の設定では以下のように `@Valid` をメソッドに付与する場合もある。
   ```java
   @POST
   @Consumes(MediaType.APPLICATION_JSON)
   @Valid
   public HttpResponse save(Person person) { ... }
   ```
   (`component/handlers/handlers-jaxrs_bean_validation_handler.json:s4`)

2. **エラーレスポンスのカスタマイズ**: バリデーションエラー時にJSONボディ付きのエラーレスポンスを返すには、`ErrorResponseBuilder` を継承したクラスを作成し、`ApplicationException` を検知して HTTP 400 + JSONボディを返すよう実装する。(`component/handlers/handlers-jaxrs_response_handler.json:s7`)

3. **ErrorResponseBuilder の登録**: 作成したカスタム実装は `JaxRsResponseHandler` の `errorResponseBuilder` プロパティに設定する。
   ```xml
   <component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
     <property name="errorResponseBuilder">
       <component class="sample.SampleErrorResponseBuilder" />
     </property>
   </component>
   ```
   (`component/handlers/handlers-jaxrs_response_handler.json:s5`)

**注意点**:
- `ErrorResponseBuilder` のカスタマイズ実装内で例外が発生すると、クライアントにレスポンスを返せなくなる。実装中に例外が発生しないよう注意すること。フレームワークはこの場合 WARN ログを出力し、ステータスコード 500 のレスポンスを生成して継続する。(`component/handlers/handlers-jaxrs_response_handler.json:s5`)
- デフォルトの `ErrorResponseBuilder` でプロジェクト要件を満たせない場合のみカスタマイズが必要。

参照: component/libraries/libraries-bean_validation.json:s14, component/handlers/handlers-jaxrs_bean_validation_handler.json:s4, component/handlers/handlers-jaxrs_response_handler.json:s7, component/handlers/handlers-jaxrs_response_handler.json:s5