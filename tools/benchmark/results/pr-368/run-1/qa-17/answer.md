**結論**: `SystemRepository.get(String name)` メソッドを使用して、コンポーネント設定ファイル(xml)で定義したname属性の値を指定してコンポーネントを取得できます。

**根拠**:

コンポーネント設定ファイル(xml)でコンポーネントを定義します:

```xml
<component name="sampleComponent" class="sample.SampleComponent" />

<component name="component" class="sample.Component" >
  <property name="component2">
    <component name="component2" class="sample.Component2" />
  </property>
</component>
```

`SystemRepository.get()` でコンポーネントを取得します:

```java
// SystemRepository#getを使用して取得する。
SampleComponent sample = SystemRepository.get("sampleComponent");

// ネストしたcomponentは、親の名前と自身の名前を"."で連結し取得する。
Component2 component2 = SystemRepository.get("component.component2");
```

`get` メソッドのシグネチャ:

```java
public static <T> T get(String name) throws ClassCastException
```

- `name`: コンポーネント名（xml の name 属性値）
- 戻り値: 登録されたコンポーネント。コンポーネントが見つからなかった場合は `null` を返す

**注意点**:
- 取得するコンポーネントの型と型引数 `<T>` が一致しない場合は `ClassCastException` がスローされます
- システムリポジトリには事前にDIコンテナの情報が設定されている必要があります（通常は `ServletContextListener` の実装クラスや独立型アプリケーションの起動クラスがNablarch側で行うため、個別実装は不要です）
- DIコンテナで管理されるコンポーネントはシングルトンです。取得のたびに新しいインスタンスが生成されるわけではありません

参照: libraries-repository.json:s25, libraries-repository.json:s24, javadoc-nablarch-core-repository-SystemRepository.json:s11