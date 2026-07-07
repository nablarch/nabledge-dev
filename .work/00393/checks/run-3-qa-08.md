# qa-08 — run-3

## 質問

メッセージやラベルを日本語と英語で切り替えたい。多言語化の方法を教えてほしい

## 回答

**結論**: メッセージの多言語化は、言語ごとのプロパティファイル（`messages.properties`、`messages_en.properties` 等）を用意し、`PropertiesStringResourceLoader` にサポート言語を設定することで実現する。使用言語は `ThreadContext` の言語情報に基づいて自動切り替えされる。

**根拠**:

**① プロパティファイルの準備**

デフォルト言語（日本語）と英語の2ファイルを作成する：

```none
main/resources/messages.properties       # デフォルト（日本語）
               messages_en.properties    # 英語用
```

```properties
# messages.properties（日本語）
label.user.register.title=ユーザ登録画面
errors.login=ログインに失敗しました。
```

```properties
# messages_en.properties（英語）
label.user.register.title=User Registration
errors.login=Login failed.
```

**② コンポーネント定義**

`PropertiesStringResourceLoader` にサポート言語を設定する：

```xml
<component class="nablarch.core.cache.BasicStaticDataCache" name="messageCache">
  <property name="loader">
    <component class="nablarch.core.message.PropertiesStringResourceLoader">
      <!-- サポートする言語 -->
      <property name="locales">
        <list>
          <value>en</value>
        </list>
      </property>
      <!-- デフォルトの言語（必須） -->
      <property name="defaultLocale" value="ja" />
    </component>
  </property>
</component>

<component name="stringResourceHolder" class="nablarch.core.message.StringResourceHolder">
  <property name="stringResourceCache" ref="messageCache" />
</component>

<component name="initializer"
           class="nablarch.core.repository.initialization.BasicApplicationInitializer">
  <property name="initializeList">
    <list>
      <component-ref name="messageCache" />
    </list>
  </property>
</component>
```

**③ 言語切り替えの設定（ユーザが選択できる場合）**

ユーザが言語を選択できるようにするには、`LanguageAttributeInHttpCookie` を使用する：

```xml
<!-- コンポーネント名を "languageAttribute" にすること -->
<component name="languageAttribute"
           class="nablarch.common.web.handler.threadcontext.LanguageAttributeInHttpCookie">
  <property name="defaultLanguage" value="ja" />
  <property name="supportedLanguages" value="ja,en" />
</component>
```

ハンドラで選択言語をクッキーに保持する：

```java
// LanguageAttributeInHttpUtil.keepLanguage でクッキーとスレッドコンテキストの両方に設定
LanguageAttributeInHttpUtil.keepLanguage(request, context, language);
```

**④ JSP でのメッセージ出力**

`n:message` タグを使うと、現在の `ThreadContext` 言語に対応したメッセージが自動表示される：

```jsp
<n:message messageId="label.user.register.title" />
```

**注意点**:
- `defaultLocale` は必ず明示的に設定すること。未設定の場合 `Locale.getDefault().getLanguage()` が使用され、実行環境依存で障害の原因になる。
- `messages.properties`（デフォルト言語ファイル）が存在しない場合はエラーになる。

参照: libraries-message.json:s8, handlers-thread-context-handler.json:s7, handlers-thread-context-handler.json:s4

## 参照ナレッジ

- [多言語化対応](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-message.md#多言語化対応) (s8)
- [ユーザが言語を選択する画面を作る](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-thread-context-handler.md#ユーザが言語を選択する画面を作る) (s7)
- [リクエスト毎にスレッドコンテキストの初期化を行う](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-thread-context-handler.md#リクエスト毎にスレッドコンテキストの初期化を行う) (s4)
- [プロパティファイルにメッセージを定義する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-message.md#プロパティファイルにメッセージを定義する) (s7)
- [言語毎のコンテンツパスの切り替え](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-http-response-handler.md#言語毎のコンテンツパスの切り替え) (s7)
- [名称の多言語化対応](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-code.md#名称の多言語化対応) (s8)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The expected output contains two key facts: (1) preparing property files for each language, and (2) setting supported languages in the 'locales' property. The actual output explicitly covers both facts — it demonstrates creating language-specific property files (messages.properties, messages_en.properties) and shows the XML configuration with the 'locales' property in PropertiesStringResourceLoader. Both expected facts are fully covered. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is perfectly relevant to the input, directly addressing the question about how to switch messages and labels between Japanese and English for multilingual support. No irrelevant statements were found! |
| faithfulness | 0.99 | 0.95 | NG | The score is 0.95 because the actual output incorrectly implies that 'defaultLocale' is a mandatory or required setting, whereas the retrieval context states that it is optional — if not configured, the system falls back to Locale.getDefault().getLanguage(). Additionally, the retrieval context clarifies that the default locale does not need to be added to the supported languages list, suggesting the actual output may have misrepresented this behavior. |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「言語ごとのプロパティファイルを用意しサポートする言語をlocalesに設定する」は回答の「①プロパティファイルの準備」でmessages.properties / messages_en.propertiesを用意し、「②コンポーネント定義」でPropertiesStringResourceLoaderのlocalesプロパティにenを設定する例として明示されている |
| answer_relevancy | NG | 回答末尾の「参照: libraries-message.json:s8, handlers-thread-context-handler.json:s7, handlers-thread-context-handler.json:s4」はシステム内部のJSON参照記法であり、ユーザー向け回答に含めるべき情報ではない |
| faithfulness | OK | DeepEvalはdefaultLocaleを「任意設定」と誤判定しているが、ナレッジ（libraries-message.md「多言語化対応」節）には「必ずデフォルトの言語を設定すること」と明記されており、回答の「defaultLocaleは必ず明示的に設定すること」はナレッジと完全に一致する。矛盾なし |

### 参照事実（expected_facts）

- 言語ごとのプロパティファイルを用意しサポートする言語をlocalesに設定する
