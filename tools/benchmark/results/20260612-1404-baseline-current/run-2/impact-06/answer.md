**結論**: スケールアウト構成では **DBストアまたはRedisストア** を選ぶ。HTTPセッションストアはAPサーバごとに状態を持つためスケールアウトに不向きで、HIDDENストアはクライアントサイド保存なので追加設定（暗号化キーの共有）が必要。

**根拠**:

Nablarchが標準で提供するセッション変数の保存先は以下の4種類。

| ストア | 保存先 | スケールアウト適性 |
|--------|--------|-------------------|
| DBストア | データベース上のテーブル | ◎ 問題なし |
| HIDDENストア | クライアントサイド（hiddenタグ） | △ 暗号化キーの共有設定が必要 |
| HTTPセッションストア | APサーバのヒープ領域 | ✕ APサーバ毎に状態を持つ |
| Redisストア (Lettuceアダプタ) | Redis | ◎ 問題なし |

**各ストアの特徴**:

**DBストア**
- APサーバのヒープ領域を圧迫しない
- ローリングメンテナンス等でAPサーバが停止した場合でもセッション変数の復元が可能
- 同一セッションの処理が複数スレッドで実行された場合は後勝ち（先に保存されたデータは消失）
- 期限切れセッションを削除するバッチの実装が必要

**HIDDENストア**
- クライアントサイド（hiddenタグ）に保存するためAPサーバに状態を持たない
- 複数タブでの画面操作を許容できる
- **スケールアウト時の注意**: APサーバ冗長化構成では、各サーバが異なる暗号化キーを自動生成するため復号に失敗するケースがある。明示的に暗号化キーを統一する設定が必要:

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

**HTTPセッションストア**
- APサーバのヒープ領域に保存するため、APサーバごとに状態を持つ
- そのままではスケールアウトできず、以下のいずれかの対処が必要（いずれも制約あり）:
  1. ロードバランサーでスティッキーセッションを有効にする
  2. APサーバのセッションレプリケーション機能を使用する
  3. APサーバのHTTPセッション保存先をNoSQLにする
- 上記の 1・2 はTwelve-Factor Appの廃棄容易性の点で劣り、2・3 はAPサーバ依存となる

**Redisストア (Lettuceアダプタ)**
- セッション情報を保存するためのテーブルを事前に用意する必要がない
- 有効期限が切れたセッション情報は自動的に削除される（バッチ不要）
- Sentinelを使用したMaster-Replica構成やCluster構成にも対応
- 特徴はDBストアと同じ

**スケールアウト時の推奨構成**:
DBストアまたはRedisストアを使い、セッション有効期間の保存先もHTTPセッションからデータベースまたはRedisに変更することでAPサーバを完全にステートレスにできる。

**注意点**:
- HTTPセッションストアをそのまま使う場合、スケールアウトには必ず追加の工夫（スティッキーセッション等）が必要
- HIDDENストアはクライアントに全データを持ち回るため、大量データの保存に向かない
- Redisストアを使う場合はアダプタ (`nablarch-integration-redisstore-lettuce`) の追加と設定が必要

参照: libraries-session-store.json:s2, libraries-session-store.json:s12, libraries-session-store.json:s16, libraries-session-store.json:s17, libraries-stateless-web-app.json:s1, libraries-stateless-web-app.json:s2, libraries-stateless-web-app.json:s4, adapters-redisstore-lettuce-adaptor.json