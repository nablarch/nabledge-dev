十分な情報が取得できました。回答を生成します。

---

**結論**: スケールアウト環境では、**DBストア**または**Redisストア(Lettuce)アダプタ**を選択してください。HTTPセッションストアはAPサーバごとに状態を持つため、スケールアウトには工夫が必要です。HIDDENストアは複数タブ許容の入力フローに特化しており、認証情報や横断的なセッション管理には向きません。

---

**根拠**: 各ストアの特徴を以下に整理します。

### DBストア（データベース）

**保存先**: データベース上のテーブル（`USER_SESSION` テーブル）

- ローリングメンテナンス等でAPサーバが停止しても、セッション変数を復元できる
- APサーバのヒープ領域を圧迫しない
- スケールアウト時に全サーバが同じDBを参照するため、スティッキーセッション不要
- **注意**: 同一セッションを複数スレッドで同時処理した場合は後勝ちとなる（先に保存されたデータは消失）
- 期限切れセッションを定期的に削除するバッチが必要

### HIDDENストア（クライアントサイド）

**保存先**: HTMLの `hidden` タグを使って画面間で引き回す

- 複数タブでの画面操作を許容できる
- APサーバがヒープを消費しない
- **スケールアウト時の注意**: APサーバが冗長化されている場合、サーバごとに異なる暗号化キーが自動生成されるため、別サーバに振られると復号が失敗する。共通の暗号化キーを明示的に設定する必要がある

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

### HTTPセッションストア（APサーバのヒープ）

**保存先**: APサーバのヒープ領域

- **APサーバ毎に情報を保持するため、スケールアウトを行う際に工夫が必要**
- スケールアウトするには以下のいずれかの対処が必要（いずれも制約あり）：
  1. ロードバランサーでスティッキーセッションを有効にする（廃棄容易性の点で劣る）
  2. APサーバのセッションレプリケーション機能を使用する（APサーバ依存）
  3. APサーバのHTTPセッション保存先をNoSQLにする（APサーバ依存）
- 大量データを保存するとヒープ領域を圧迫する恐れがある

### Redisストア（Lettuce アダプタ）

**保存先**: Redis（外部キーバリューストア）

- 特徴はDBストアと同じ（保存先が異なるだけ）
- テーブルを事前に作成する必要がない
- 有効期限が切れたセッション情報はRedisが自動削除するため、削除バッチが不要
- Sentinel（Master-Replica）構成やCluster構成にも対応

---

### 選択基準のまとめ

| 用途 | 推奨ストア |
|---|---|
| 認証情報の保持（スケールアウト環境） | **DBストア** または **Redisストア** |
| 入力～確認～完了画面間の入力情報保持（複数タブ不要） | DBストア |
| 入力～確認～完了画面間の入力情報保持（複数タブ許容） | HIDDENストア（共通暗号化キーの設定が必要） |
| スケールアウト + 運用負荷を下げたい | **Redisストア**（有効期限自動管理、DBテーブル不要） |

---

**注意点**:
- セッションの有効期間はデフォルトではHTTPセッションに保存されます。DBストアを使用してAPサーバをステートレスにする場合は、有効期間の保存先もデータベースに変更する必要があります（`DbManagedExpiration` を設定）
- Redisストアを使用する場合は有効期限管理がRedis側で完結するため、この設定変更は不要です

参照: libraries-session-store.json:s16, libraries-session-store.json:s2, libraries-session-store.json:s12, libraries-session-store.json:s17, adapters-redisstore-lettuce-adaptor.json:s5, adapters-redisstore-lettuce-adaptor.json:s6, adapters-redisstore-lettuce-adaptor.json:s15, libraries-stateless-web-app.json:s1

---