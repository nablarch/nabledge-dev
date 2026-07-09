**結論**: `SystemRepository.get("コンポーネント名")` を使用して、コンポーネント設定ファイルで定義したコンポーネントを取得できます。

**根拠**:

コンポーネント設定ファイル（XML）でコンポーネントを定義します。

```xml
<component name="sampleComponent" class="sample.SampleComponent" />

<component name="component" class="sample.Component" >
  <property name="component2">
    <component name="component2" class="sample.Component2" />
  </property>
</component>
```

アプリケーションコードからは `SystemRepository.get()` で取得します。

```java
// SystemRepository#getを使用して取得する。
SampleComponent sample = SystemRepository.get("sampleComponent");

// ネストしたcomponentは、親の名前と自身の名前を"."で連結し取得する。
Component2 component2 = SystemRepository.get("component.component2");
```

**注意点**:
- `SystemRepository.get()` を呼び出す前に、DIコンテナの情報をシステムリポジトリにロードしておく必要があります（`SystemRepository.load(new DiContainer(loader))`）。この処理は通常 Nablarch が提供する `ServletContextListener` や起動クラスが担うため、個別実装は不要です。
- コンポーネントはシングルトンとして管理されます。取得のたびに新しいインスタンスが生成されるわけではありません。

参照:
- システムリポジトリ
  .claude/skills/nabledge-6/docs/component/libraries/libraries-repository.md
  システムリポジトリからオブジェクトを取得する
  DIコンテナの情報をシステムリポジトリに設定する