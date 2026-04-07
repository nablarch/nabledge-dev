**結論**: 
Nablarch 5では二重サブミット防止をクライアント側とサーバ側の両方で実装します。クライアント側ではJavaScriptでボタン無効化を行い、サーバ側ではトークンチェックで実現します。

**根拠**: 
二重サブミット防止はデータベースコミットを伴う処理でクライアント側とサーバ側の両方を併用する必要があります。

1. **クライアント側の実装（JSP）**:
   - `n:submit`、`n:button`、`n:submitLink`などのカスタムタグに`allowDoubleSubmission="false"`を指定
   - 1回目のサブミット時にボタンのonclick属性を書き換え、disabled属性を設定して2回目以降をサーバに送信しない

   実装例:
   ```jsp
   <n:submit type="button" name="register" value="登録" uri="./register"
             allowDoubleSubmission="false" />
   ```

2. **サーバ側の実装（JSP）**:
   - `n:form`タグの`useToken="true"`属性を指定してトークンを発行
   - サーバ側で一意なトークンをセッションとhiddenタグに保持
   
   実装例:
   ```jsp
   <n:form useToken="true">
   ```

3. **トークンチェック設定**:
   - `OnDoubleSubmission`インターセプタを使用してトークン突合を実行
   - `BasicDoubleSubmissionHandler`でデフォルト値（遷移先、エラーメッセージ、ステータスコード）を設定
