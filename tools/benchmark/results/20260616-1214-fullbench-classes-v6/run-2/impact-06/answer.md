**結論**: APサーバを複数台にスケールアウトする場合、HTTPセッションストアはAPサーバごとに情報を持つためそのままでは使用できません。スケールアウトに対応するには **DBストア**、**HIDDENストア**、または **Redisストア（Lettuceアダプタ）** を選択します。

---

**根拠**:

## 各ストアの特徴

### DBストア（スケールアウト推奨）
**保存先**: データベース上のテーブル

| 特徴 | 内容 |
|---|---|
| スケールアウト | APサーバに状態を持たないため、そのまま対応可能 |
| 耐障害性 | ローリングメンテナンス等でサーバが停止しても復元可能 |
| メモリ | APサーバのヒープを圧迫しない |
| 注意点 | 同一セッションが複数スレッドで実行された場合、後勝ち（先に保存されたデータは消失） |
| その他 | 有効期限切れのセッション情報を削除するバッチが必要 |

### HIDDENストア
**保存先**: クライアントサイド（hiddenタグで画面間引き回し）

| 特徴 | 内容 |
|---|---|
| スケールアウト | クライアントに情報を持つためAPサーバ側は完全ステートレス |
| 複数タブ | 複数タブでの画面操作を許容できる |
| メモリ | APサーバのヒープを圧迫しない |
| 注意点 | **アプリケーションサーバが冗長化されている場合、暗号化キーをサーバ間で統一する必要がある** |

冗長化時の暗号化キー設定（必須）:

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

デフォルトでは各APサーバが個別にキーを自動生成するため、他サーバで復号できずエラーになります。

### HTTPセッションストア
**保存先**: APサーバのヒープ領域

| 特徴 | 内容 |
|---|---|
| スケールアウト | **APサーバ毎に情報を保持するため、スケールアウトを行う際に工夫が必要** |
| 用途 | 認証情報のような頻繁にアクセスする情報の保持に適している |

→ スケールアウト構成では**単独での使用は不向き**（スティッキーセッション等の追加設定が必要）。

### Redisストア（Lettuceアダプタ）
**保存先**: Redis

DBストアと同じ特徴を持ち、さらに以下のメリットがある:

| 特徴 | 内容 |
|---|---|
| スケールアウト | DBストアと同様にAPサーバ非依存 |
| テーブル不要 | セッション情報保存用テーブルの事前作成不要 |
| 自動削除 | 有効期限切れのセッション情報をRedisが自動削除（削除バッチ不要） |
| 構成対応 | 単一／Master-Replica（Sentinel）／Cluster に対応 |

基本設定（環境設定値）:
```properties
nablarch.sessionManager.defaultStoreName=redis
nablarch.lettuce.clientType=simple   # simple / masterReplica / cluster
```

## 選択基準まとめ

| 用途 | 推奨ストア |
|---|---|
| 入力〜確認〜完了画面間のデータ保持（複数タブ不要） | DBストア または Redisストア |
| 入力〜確認〜完了画面間のデータ保持（複数タブ許容） | HIDDENストア |
| 認証情報の保持 | DBストア または Redisストア |

## スケールアウト時のHTTPセッション非依存化

有効期間はデフォルトではHTTPセッションに保存されます。スケールアウト時は有効期間もHTTPセッションから切り離す必要があります（`セッション変数保存ハンドラ` の設定で有効期間をDBに保存可能）。

**注意点**:
- DBストアで複数スレッドが同一セッションを並行処理した場合は後勝ちになるため、設計時に考慮が必要です
- HTTPセッションストアはデフォルトでセッション有効期間の保存先としても使用されるため、DBストア/Redisストアに切り替えた場合は有効期間の保存先も変更することを検討してください

参照: component/libraries/libraries-session-store.json:s16, component/libraries/libraries-session-store.json:s2, component/libraries/libraries-session-store.json:s12, component/libraries/libraries-session-store.json:s17, component/adapters/adapters-redisstore-lettuce-adaptor.json:s5, component/adapters/adapters-redisstore-lettuce-adaptor.json:s6, component/adapters/adapters-redisstore-lettuce-adaptor.json:s14, component/adapters/adapters-redisstore-lettuce-adaptor.json:s15, component/libraries/libraries-stateless-web-app.json:s1, component/libraries/libraries-stateless-web-app.json:s4