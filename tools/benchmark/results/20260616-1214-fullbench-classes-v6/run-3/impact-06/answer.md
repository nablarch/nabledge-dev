**結論**: スケールアウト環境では **DBストア** または **Redisストア** を選択してください。HTTPセッションストアはAPサーバ毎に状態を持つためスケールアウトには不向きです。HIDDENストアはサーバ側に状態を持たないため、スケールアウトの文脈では別の意味で有効です。

**根拠**:

#### 各ストアの特徴

| ストア | 保存先 | スケールアウト適性 | 特記事項 |
|---|---|---|---|
| **DBストア** | データベース上のテーブル | ✅ 適する | APサーバ停止時もセッション復元可能。有効期限切れレコードは定期削除バッチが必要 |
| **HIDDENストア** | クライアントサイド（hiddenタグで画面間引き回し） | ✅ 適する | APサーバが状態を持たない。複数タブ操作を許容できる。ただし冗長化時は暗号化キーを明示設定する必要あり |
| **HTTPセッションストア** | APサーバのヒープ領域 | ❌ 不向き | APサーバ毎に情報を保持するため「スケールアウトを行う際に工夫が必要」 |
| **Redisストア** | Redis（外部ストア） | ✅ 適する | DBストアと特徴は同じ。有効期限はRedisの仕組みで自動削除（バッチ不要） |

**重要な追加考慮点**:

HTTPセッションストアのまま複数台APサーバを構成する場合、以下の3択となりますが、いずれも欠点があります:

1. ロードバランサーで**スティッキーセッション**を有効にする → 廃棄容易性（Twelve-Factor App）の点で劣る
2. APサーバの**セッションレプリケーション**機能を使用する → APサーバ依存
3. APサーバのHTTPセッション保存先をNoSQLにする → APサーバ依存

#### HIDDENストアを使う場合の冗長化注意点

デフォルトでは暗号化キーがAPサーバ起動ごとに自動生成されるため、複数台構成では別サーバで復号失敗します。明示的にキーを統一する必要があります:

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

#### 完全なステートレス化のために

セッションストアだけでなく、以下の機能もデフォルトでHTTPセッションに依存しているため、併せて切り替えが必要です:

- **セッションストアの有効期間**: デフォルトはHTTPセッション保存 → `DbManagedExpiration` でDB保存に変更
- **2重サブミット防止**: DBベースの実装に変更
- **スレッドコンテキスト変数管理ハンドラ**: `LanguageAttributeInHttpSession` → `LanguageAttributeInHttpCookie` 等に変更

#### 選択基準まとめ

| 用途 | 推奨ストア |
|---|---|
| 入力〜確認〜完了画面間の入力情報保持（複数タブ不可） | DBストア |
| 入力〜確認〜完了画面間の入力情報保持（複数タブ可） | HIDDENストア |
| 認証情報の保持（スケールアウト環境） | DBストアまたはRedisストア |

**注意点**: HTTPセッションストアを認証情報の保持に使う場合、スケールアウト時は上記の工夫が必要です。スケールアウトを前提とするならDBストアまたはRedisストアを最初から選ぶのが推奨です。

参照: libraries-session-store.json:s16, libraries-session-store.json:s2, libraries-stateless-web-app.json:s1, libraries-stateless-web-app.json:s2, handlers-SessionStoreHandler.json:s9, libraries-session-store.json:s17, adapters-redisstore-lettuce-adaptor.json:s15, adapters-redisstore-lettuce-adaptor.json:s6