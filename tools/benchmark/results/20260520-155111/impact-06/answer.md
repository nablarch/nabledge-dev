**結論**: スケールアウト構成では、DBストアまたはRedisストアを選択する。HTTPセッションストアはAPサーバごとにデータを保持するためスケールアウト時に追加の工夫が必要であり、避けるべきストアです。

**根拠**:

Nablarchが提供するセッション変数の保存先は以下の3種類＋Redisアダプタです。

**DBストア（推奨：スケールアウト対応）**
- 保存先: データベース上のテーブル（`USER_SESSION`テーブル）
- APサーバが停止してもセッション変数の復元が可能
- APサーバのヒープ領域を圧迫しない
- 同一セッションの処理が複数スレッドで実行された場合は後勝ち
- 期限切れのセッション情報を定期的に削除するバッチが必要

**Redisストア（Lettuceアダプタ）（推奨：スケールアウト対応）**
- 保存先: Redis（外部サービス）
- DBストアと同等の特徴を持つ
- DBストートと比較したメリット:
  - セッション情報を保存するテーブルを事前に用意不要
  - 有効期限切れのセッション情報はRedisが自動削除するため、削除バッチが不要
- Sentinel（Master-Replica）やCluster構成にも対応:

```properties
# 単一インスタンス（デフォルト）
nablarch.lettuce.clientType=simple
# Master-Replica
nablarch.lettuce.clientType=masterReplica
# Cluster
nablarch.lettuce.clientType=cluster
```

**HIDDENストア（スケールアウトに問題なし：特定用途向け）**
- 保存先: クライアントサイド（hiddenタグで画面間を引き回す）
- APサーバのヒープ領域を圧迫しない
- 複数タブでの画面操作を許容できる
- ただし、APサーバ冗長化時は**共通の暗号化キー**を明示設定が必要

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
デフォルトではAPサーバごとに異なるキーが自動生成されるため、複数台構成では上記のように明示指定しないと復号に失敗します。

**HTTPセッションストア（スケールアウト時に注意）**
- 保存先: APサーバのヒープ領域
- **APサーバごとに情報を保持するため、スケールアウト時に工夫が必要**
- 大量データ保存でヒープを圧迫する恐れあり

**選択基準まとめ**:

| 用途 | スケールアウト対応 | 推奨ストア |
|------|-------------------|----------|
| 認証情報の保持 | ○ | DBストアまたはHTTPセッションストア（DBストア推奨） |
| 入力～確認画面の保持（複数タブ不要） | ○ | DBストア |
| 入力～確認画面の保持（複数タブ許容） | ○ | HIDDENストア（キー明示設定必須） |
| 高スループット・テーブル管理不要 | ○ | Redisストア |

**注意点**:
- HIDDENストアを冗長化APサーバで使う場合は必ず暗号化キーを明示設定すること。自動生成キーではAPサーバをまたぐリクエストで復号エラーが発生します。
- DBストアでは、期限切れセッションの削除バッチが別途必要です。
- Redisストアはその手間を省けますが、外部Redisインフラの管理コストが生じます。

参照: `component/libraries/libraries-session-store.json:s16`, `component/libraries/libraries-session-store.json:s12`, `component/adapters/adapters-redisstore-lettuce-adaptor.json:s5`, `component/adapters/adapters-redisstore-lettuce-adaptor.json:s6`, `component/adapters/adapters-redisstore-lettuce-adaptor.json:s15`