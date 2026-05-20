**結論**: スケールアウト環境では **DBストア**（またはRedisストア）を第一候補とし、入力フォーム画面間の引き回しに限り **HIDDENストア** も選択肢になります。**HTTPセッションストア** はスケールアウト時に追加の工夫が必要です。

**根拠**:

Nablarchが標準で提供するストアは3種類＋アダプタ1種類です。

**DBストア**（保存先：データベーステーブル）
- APサーバが複数台になっても同じDBを参照するため、スケールアウトに対応できます。
- ローリングメンテナンス等でAPサーバが停止してもセッション変数を復元できます。
- APサーバのヒープ領域を圧迫しません。
- 期限切れセッションが残るため、定期削除バッチが必要です。

**HIDDENストア**（保存先：クライアントサイド）
- セッション変数をhiddenタグで画面間に引き回すため、APサーバにステートを持ちません。スケールアウトに問題なく対応できます。
- **注意**: APサーバが冗長化されている場合、サーバごとに異なる暗号化キーが自動生成され、復号に失敗するケースがあります。この場合は明示的にキーを固定する必要があります。

```xml
<component class="nablarch.common.web.session.store.HiddenStore">
  <property name="encryptor">
    <component class="nablarch.common.encryption.AesEncryptor">
      <property name="base64Key">
        <component class="nablarch.common.encryption.Base64Key">
          <property name="key" value="OwYMOWbnLyYy93P8oIayeg==" />
          <property name="iv"  value="NOj5OUN+GlyGYTc6FM0+nw==" />
        </component>
      </property>
    </component>
  </property>
</component>
```

**HTTPセッションストア**（保存先：APサーバのヒープ）
- APサーバごとにデータを保持するため、スケールアウト時に次のいずれかが必要になります。
  1. ロードバランサーのスティッキーセッションを有効にする
  2. APサーバのセッションレプリケーション機能を使用する
  3. APサーバのHTTPセッション保存先をNoSQLにする
- なお、1・2はTwelve-Factor Appの廃棄容易性の観点で劣り、2・3はAPサーバ依存になります。

**Redisストア**（Lettuceアダプタ使用）
- 保存先がRedisになるだけで特徴はDBストアと同じです。
- DBストアと比べ、セッション情報用テーブルを事前に準備する必要がなく、有効期限切れのセッションもRedisが自動削除するためバッチも不要です。
- `nablarch.lettuce.clientType` の設定値で単一インスタンス・Master-Replica・Cluster構成を切り替えられます。

**選択基準まとめ**:

| 用途 | 推奨ストア |
|------|-----------|
| 認証情報の保持（スケールアウト対応） | DBストア / Redisストア |
| 入力～確認～完了画面間（複数タブ不許可） | DBストア |
| 入力～確認～完了画面間（複数タブ許可） | HIDDENストア（暗号化キーを明示的に設定） |
| HTTPセッション依存なしにしたい | セッションストアの有効期間保存先をDBに変更 |

**注意点**:
- HIDDENストアを冗長構成で使う場合、全APサーバで同じ暗号化キー・IVを設定しなければ復号エラーになります。
- HTTPセッション非依存にするには、セッションストアの有効期間保存先もDBに変更する必要があります。
- HTTPセッションの誤生成を防ぐために、`WebFrontController` の `preventSessionCreation` を `true` にすることも推奨されます。

参照: component/libraries/libraries-session-store.json:s2, s12, s16, s17, component/adapters/adapters-redisstore-lettuce-adaptor.json:s5, s6, s7, s14, s15, component/libraries/libraries-stateless-web-app.json:s1, s2