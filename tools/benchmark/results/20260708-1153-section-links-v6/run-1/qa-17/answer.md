**結論**: `SystemRepository.get("コンポーネント名")` を使用して、コンポーネント設定ファイルの `name` 属性に設定した名前を指定することで登録済みコンポーネントを取得できます。

**根拠**:

コンポーネント定義（XML）:

```xml
<component name="sampleComponent" class="sample.SampleComponent" />

<component name="component" class="sample.Component" >
  <property name="component2">
    <component name="component2" class="sample.Component2" />
  </property>
</component>
```

取得例:

```java
// SystemRepository#getを使用して取得する。
SampleComponent sample = SystemRepository.get("sampleComponent");

// ネストしたcomponentは、親の名前と自身の名前を"."で連結し取得する。
Component2 component2 = SystemRepository.get("component.component2");
```

**注意点**:
- `SystemRepository.get()` を呼び出す前に、DIコンテナの情報がシステムリポジトリに設定されている必要があります。この初期化は通常 `ServletContextListener` の実装クラスや独立型アプリケーションの起動クラスによって行われるため、個別に実装することは基本的にありません。
- コンポーネント名の指定には `component` 要素の `name` 属性に設定した値を使用します。`name` 属性が設定されていないコンポーネントは名前での取得ができないため注意してください。

参照:
- システムリポジトリ
  .claude/skills/nabledge-6/docs/component/libraries/libraries-repository.md
  システムリポジトリからオブジェクトを取得する
  DIコンテナの情報をシステムリポジトリに設定する
  Java Beansオブジェクトを設定する