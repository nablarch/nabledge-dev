**結論**: Nablarch 1.3では、クライアント側（JavaScript）とサーバ側（トークン）の2つの方法を**併用**して二重サブミットを防止します。

1. JSP: `<n:form useToken="true">`
2. Action: `@OnDoubleSubmission(path = "forward://RW11AC0201")`
3. XML: interceptorsOrderにnablarch.common.web.token.OnDoubleSubmissionを設定
4. doubleSubmissionHandlerコンポーネント設定

参照: `component/libraries/libraries-07_SubmitTag.json#s3`
