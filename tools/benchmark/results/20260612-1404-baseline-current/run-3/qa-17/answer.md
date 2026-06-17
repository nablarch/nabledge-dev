**結論**: `SystemRepository.get("コンポーネント名")` を呼び出すことで、コンポーネント設定ファイル（XML）に `name` 属性で登録されたコンポーネントをシステムリポジトリから取得できます。

**根拠**:

コンポーネント設定ファイル（XML）で以下のように `name` 属性を付けてコンポーネントを定義します。

```xml
<component name="sampleComponent" class="sample.SampleComponent" />

<component name="component" class="sample.Component" >
  <property name="component2">
    <component name="component2" class="sample.Component2" />
  </property>
</component>
```

Javaコードからは `SystemRepository.get(名前)` でオブジェクトを取得します。

```java
// SystemRepository#getを使用して取得する。
SampleComponent sample = SystemRepository.get("sampleComponent");

// ネストしたcomponentは、親の名前と自身の名前を"."で連結し取得する。
Component2 component2 = SystemRepository.get("component.component2");
```

ネストして定義したコンポーネントも取得可能で、その場合は `"親名.子名"` のように `.` で連結した名前で指定します。

**注意点**:
- `SystemRepository.get()` を呼ぶ前に、DIコンテナの情報がシステムリポジトリに設定されている必要があります。この初期化処理は通常 `ServletContextListener` の実装クラス（ウェブアプリ）や独立型アプリケーションの起動クラス（バッチ）が行うため、個別に実装することは基本的にありません。
- DIコンテナで管理されるオブジェクトはすべて **シングルトン** です。インスタンスが取得の度に新しく生成されるわけではないため、コンポーネントへの状態変更には十分注意してください。

参照: libraries-repository.json:s25, libraries-repository.json:s24