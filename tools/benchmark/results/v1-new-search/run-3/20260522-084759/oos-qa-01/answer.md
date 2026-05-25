Step 5: 回答を生成します。

セクション内容から回答を作成します。

**Step 6: Verify**

Nablarch固有の主張を検証します：
- 「ウェブアプリケーションはServlet APIの使用を前提」→ s1に直接記載あり ✅
- 「WebSocketアダプタは存在しない」→ アダプタ一覧に含まれていないことで裏付け ✅  
- 「WebSocketハンドラは存在しない」→ s3のハンドラ一覧に含まれていないことで裏付け ✅
- 「非同期処理はテーブルキューパターンで実現可能」→ 非同期処理ページ本文に直接記載あり ✅
- 「Jakarta WebSocketはEE仕様として存在する」→ s33の対応表に記載あり ✅

verify_result = **PASS**

---

**結論**: NablarchはWebSocketのサポート（専用ハンドラ・アダプタ）を提供していないため、Nablarchの機能としてWebSocketを使う方法はない。

**根拠**:

Nablarchのウェブアプリケーションは Servlet API の使用を前提としており、ハンドラ一覧にWebSocket関連ハンドラは含まれていない。アダプタとして提供されているのも以下のみで、WebSocketアダプタは存在しない：

> logアダプタ、ルーティングアダプタ、IBM MQアダプタ、Jakarta RESTful Web Servicesアダプタ、Domaアダプタ、JSR310アダプタ、E-mailアダプタ各種、ウェブアプリケーション Thymeleafアダプタ、Lettuceアダプタ、SLF4Jアダプタ、Micrometerアダプタ

WebSocketはJakarta EEの仕様（`Jakarta WebSocket`）として存在するが、Nablarchはこれをラップした機能を提供していない。

**バッチ進捗の非同期通知への代替アプローチ**:

Nablarchのウェブアプリケーションで非同期処理を実現するには、「テーブルをキューとして使ったメッセージング」パターンが推奨されている：

> NablarchのWebアプリケーションでは、非同期処理は「テーブルをキューとして使ったメッセージング」を組み合わることで実現可能です。
> - Webアプリはリクエストを受け付けて後続処理に必要なデータをDBに登録し、レスポンスを返却する
> - テーブルをキューとして使ったメッセージングがDBへのデータ登録を検知し、当該データの処理を行う

このパターンで非同期処理（バッチ起動）自体は実現できる。進捗状態をDBに記録してブラウザ側からポーリングする設計か、またはNablarchフレームワーク外でJakarta WebSocket APIを直接利用する方法を検討することになる（後者のNablarch側のサポートは知識ファイルの対象範囲外）。

**注意点**: NablarchはOSSを使用しないポリシーを採っており（プロダクションコードへの迅速な脆弱性対応のため）、WebSocket実装ライブラリのアダプタも提供されていない。

参照: `processing-pattern/web-application/web-application-architecture.json:s1`, `processing-pattern/web-application/web-application-architecture.json:s3`, `component/adapters/adapters-adaptors.json`, `guide/nablarch-patterns/nablarch-patterns-Nablarchでの非同期処理.json`, `about/about-nablarch/about-nablarch-policy.json:s6`, `about/migration/migration-migration.json:s33`

---