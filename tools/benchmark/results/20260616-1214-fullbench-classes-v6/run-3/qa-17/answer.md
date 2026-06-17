**結論**: `SystemRepository.get("コンポーネント名")` を呼び出すことで、コンポーネント設定ファイル(xml)に登録済みのコンポーネントを取得できます。コンポーネントが見つからない場合は `null` が返ります。

**根拠**:

コンポーネント設定ファイルでの定義例:

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
// SystemRepository#get を使用して取得する
SampleComponent sample = SystemRepository.get("sampleComponent");

// ネストしたコンポーネントは、親の名前と自身の名前を "." で連結して取得する
Component2 component2 = SystemRepository.get("component.component2");
```

`SystemRepository.get` のシグネチャ:

```java
public static <T> T get(String name) throws ClassCastException
```

- 引数: コンポーネント名（xml の `name` 属性に設定した値）
- 戻り値: 登録されたコンポーネント。見つからない場合は `null`
- 例外: 型引数 `<T>` と登録されたコンポーネントの型が一致しない場合に `ClassCastException`

**注意点**:
- `SystemRepository.get` を呼び出す前に、DIコンテナの情報がシステムリポジトリに設定されている必要があります。この設定はNablarchが提供する `ServletContextListener` の実装クラスや独立型アプリケーションの起動クラスによって自動的に行われるため、通常は個別に実装する必要はありません。
- 取得されるインスタンスはシングルトンです（リクエストごとに新しいインスタンスが生成されるわけではありません）。

参照: libraries-repository.json:s25, libraries-repository.json:s24, javadoc-nablarch-core-repository-SystemRepository.json:s11