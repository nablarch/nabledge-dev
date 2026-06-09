**結論**: NablarchにはCSRF対策機能（`CsrfTokenVerificationHandler`）があり、ハンドラ構成に1つのコンポーネントを追加するだけで、全リクエストに対してCSRFトークンの生成・検証が自動的に適用されます。

**根拠**:

**仕組み**: 一意なトークン（デフォルトはUUID v4）をセッションストアに格納し、POSTなどのリクエスト時にHTTPリクエストヘッダ（`X-CSRF-TOKEN`）またはパラメータ（`csrf-token`）の値とセッションのトークンを照合します。検証に失敗した場合は400（BadRequest）を返します。GETなどのリードオンリーなHTTPメソッドは検証対象外です。

**モジュール依存関係**:
```xml
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-fw-web</artifactId>
</dependency>
```

**基本設定**（JakartaServer Pagesカスタムタグを使う場合）:
```xml
<!-- ハンドラ構成 -->
<component name="webFrontController" class="nablarch.fw.web.servlet.WebFrontController">
  <property name="handlerQueue">
    <list>
      <!-- 他のハンドラは省略 -->

      <!-- セッションストアハンドラ -->
      <component-ref name="sessionStoreHandler" />

      <!-- Nablarchカスタムタグ制御ハンドラ -->
      <component-ref name="nablarchTagHandler"/>

      <!-- CSRFトークン検証ハンドラ -->
      <component-ref name="csrfTokenVerificationHandler"/>
    </list>
  </property>
</component>

<component name="csrfTokenVerificationHandler"
           class="nablarch.fw.web.handler.CsrfTokenVerificationHandler" />
```

**注意点**:

1. **ハンドラの配置順序**: `CsrfTokenVerificationHandler`は以下の順序を守ること。
   - `セッション変数保存ハンドラ（SessionStoreHandler）`より後ろに配置（CSRFトークンをセッションストアに格納するため）
   - JakartaServer Pagesカスタムタグを使う場合は `NablarchTagHandler` より後ろに配置（タグがCSRFトークンをhiddenとして出力するため）
   - ファイルアップロードでファイル保存前にCSRFを検証したい場合は、マルチパートリクエストハンドラより前に本ハンドラと`SessionStoreHandler`を配置

2. **ログイン時のCSRFトークン再生成**: ログイン時にセッションストアそのものを破棄しない実装（セッションIDの再生成のみ）の場合は、`CsrfTokenUtil.regenerateCsrfToken`メソッドを呼び出してCSRFトークンも再生成すること。セッションストアを破棄・再生成するならこのメソッドは不要です。

3. **テスト時の無効化**: リクエスト単体テスト時はCSRFトークンの検証が失敗するため、テスト設定でハンドラを`NopHandler`に差し替えて無効化する。
   ```xml
   <!-- CSRF対策の無効化（テスト設定） -->
   <component name="csrfTokenVerificationHandler" class="nablarch.test.NopHandler" />
   ```

4. **二重サブミット防止との関係**: データベースを使った二重サブミット防止機能はCSRF対策に対応していないため、CSRF対策には必ず本機能を使用すること。

参照: security-check-2.チェックリスト.json:s6, handlers-csrf-token-verification-handler.json:s2, handlers-csrf-token-verification-handler.json:s3, handlers-csrf-token-verification-handler.json:s4, handlers-csrf-token-verification-handler.json:s5