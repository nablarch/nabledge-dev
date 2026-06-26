**結論**: `SystemRepository.get(String name)` メソッドを使用して、コンポーネント設定ファイルで `name` 属性に設定した名前を指定することで登録済みコンポーネントを取得できます。

**根拠**:

コンポーネント設定ファイルで以下のように定義されたコンポーネントを:

```xml
<component name="sampleComponent" class="sample.SampleComponent" />

<component name="component" class="sample.Component" >
  <property name="component2">
    <component name="component2" class="sample.Component2" />
  </property>
</component>
```

次のように取得します:

```java
// SystemRepository#getを使用して取得する。
SampleComponent sample = SystemRepository.get("sampleComponent");

// ネストしたcomponentは、親の名前と自身の名前を"."で連結し取得する。
Component2 component2 = SystemRepository.get("component.component2");
```

**注意点**:
- 取得前にシステムリポジトリへDIコンテナの情報を設定しておく必要があります。ただし、この処理は通常Nablarchが提供するServletContextListenerの実装クラスや独立型アプリケーションの起動クラスが行うため、個別に実装することは基本的にありません。

参照: libraries-repository.json:s25, libraries-repository.json:s24