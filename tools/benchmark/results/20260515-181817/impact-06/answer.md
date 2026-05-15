**結論**: APサーバをスケールアウトする場合、**DBストア**または**Redisストア**を選択してください。HTTPセッションストアはスケールアウト時に追加対処が必要です。HIDDENストアはサーバ側で状態を持たないため本質的にスケールアウト可能ですが、複数タブを許容する用途向けです。

**根拠**:

各ストアの特徴は以下の通りです。

| ストア | 保存先 | スケールアウト | 特徴 |
|--------|--------|--------------|------|
| **DBストア** | データベース上のテーブル | ◎ 問題なし | ヒープを圧迫しない。ローリングメンテナンス時もセッション復元可能。 |
| **HIDDENストア** | クライアントサイド (hidden タグ) | ◎ 問題なし (※注意あり) | 複数タブ操作を許容できる。ヒープを圧迫しない。 |
| **HTTPセッションストア** | APサーバのヒープ領域 | △ 工夫が必要 | APサーバごとに状態を持つため、そのままではスケールアウト不可。 |
| **Redisストア (Lettuce)** | Redis | ◎ 問題なし | DBストアと同等の特徴。テーブル作成・有効期限バッチが不要。 |

**HTTPセッションストアでスケールアウトする場合の対処方法** (いずれも制約あり):
1. ロードバランサーでスティッキーセッションを有効にする
2. APサーバのセッションレプリケーション機能を使用する
3. APサーバのHTTPセッション保存先をNoSQLにする

※ 1・2はTwelve-Factor Appの廃棄容易性の観点で劣り、2・3はAPサーバ依存になります。

**Redisストアを使う場合**、本番環境ではSentinelを使ったMaster-Replica構成またはCluster構成を使用できます。

**注意点**:

- **HIDDENストアを使う場合**: APサーバが冗長化されているとき、各サーバがそれぞれ異なる暗号化キーを自動生成するため、**復号に失敗するケースがある**。全APサーバで共通の暗号化キー（`key`・`iv`）を明示的に設定する必要があります。

  ```xml
  <component class="nablarch.common.web.session.store.HiddenStore">
    <property name="encryptor">
      <component class="nablarch.common.encryption.AesEncryptor">
        <property name="base64Key">
          <component class="nablarch.common.encryption.Base64Key">
            <property name="key" value="OwYMOWbnLyYy93P8oIayeg==" />
            <property name="iv" value="NOj5OUN+GlyGYTc6FM0+nw==" />
          </component>
        </property>
      </component>
    </property>
  </component>
  ```

- **HTTPセッションストアのスケールアウト対応をする場合**: 2重サブミット防止・スレッドコンテキスト変数管理ハンドラ・HTTPリライトハンドラ等もHTTPセッションに依存しているため、それらも合わせてHTTPセッション非依存の設定に切り替える必要があります。

- セッションの有効期間管理: デフォルトではHTTPセッションに保存されます。DBストアを使う場合でも、`expiration` プロパティを `DbManagedExpiration` に変更することでデータベース管理に切り替えられます。

参照: component/libraries/libraries-session-store.json#s16, component/libraries/libraries-session-store.json#s2, component/libraries/libraries-stateless-web-app.json#s1, component/libraries/libraries-session-store.json#s12, component/adapters/adapters-redisstore-lettuce-adaptor.json#s5