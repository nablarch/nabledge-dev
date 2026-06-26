## APサーバスケールアウト時のセッションストア選択

**結論**: APサーバを複数台にスケールアウトする場合は **DBストア** または **HIDDENストア** を選択する。HTTPセッションストアはAPサーバごとにセッションデータを保持する仕組みのため、スケールアウト時に別途工夫が必要になる。

---

### 各ストアの特長

**DBストア**（保存先: データベース上のテーブル）

| 特長 | 内容 |
|---|---|
| スケールアウト適性 | ◎ |
| APサーバ停止時 | ローリングメンテナンス等でAPサーバが停止した場合でもセッション変数の復元が可能 |
| ヒープ領域 | APサーバのヒープ領域を圧迫しない |
| 複数スレッド | 後勝ち（先に保存されたセッションのデータは消失する） |

---

**HIDDENストア**（保存先: クライアントサイドの `hidden` タグ）

| 特長 | 内容 |
|---|---|
| スケールアウト適性 | ○（ただし冗長化時は暗号化キーの設定が必要）|
| 複数タブ | 複数タブでの画面操作を許容できる |
| ヒープ領域 | APサーバのヒープ領域を圧迫しない |
| 複数スレッド | セッションのデータはそれぞれのスレッドに紐付けて保存される |

---

**HTTPセッションストア**（保存先: APサーバのヒープ領域）

| 特長 | 内容 |
|---|---|
| スケールアウト適性 | △（APサーバごとに情報を保持するため、スケールアウトを行う際に工夫が必要） |
| 向いている用途 | 認証情報のようなアプリケーション全体で頻繁に使用する情報の保持 |
| ヒープ領域 | 大量データを保存するとヒープ領域を圧迫する恐れがある |
| 複数スレッド | 後勝ち（先に保存されたセッションのデータは消失する） |

---

### 選択基準

| 用途 | 推奨ストア |
|---|---|
| 入力～確認～完了画面間で入力情報を保持（複数タブ不可） | DBストア |
| 入力～確認～完了画面間で入力情報を保持（複数タブ可） | HIDDENストア |
| 認証情報の保持 | DBストア または HTTPセッションストア |

---

### 注意点

- **HIDDENストアを冗長化環境で使用する場合**: デフォルトでは暗号化キーはAPサーバごとに自動生成されるため、サーバをまたいだリクエストで復号に失敗するケースがある。`AesEncryptor` を使用して明示的に暗号化/復号のキーを設定すること。

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

- **Redisを使用する場合**: Redisストア(Lettuce)アダプタを使用することでRedisを保存先にできる。特徴はDBストアと同じ。

参照: libraries-session-store.json:s2, libraries-session-store.json:s16, libraries-session-store.json:s12