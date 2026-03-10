# スレッドコンテキスト変数削除ハンドラ

**公式ドキュメント**: [1](https://nablarch.github.io/docs/LATEST/doc/application_framework/application_framework/handlers/common/thread_context_clear_handler.html) [2](https://nablarch.github.io/docs/LATEST/javadoc/nablarch/common/handler/threadcontext/ThreadContextClearHandler.html)

## ハンドラクラス名

**クラス名**: `nablarch.common.handler.threadcontext.ThreadContextClearHandler`

*キーワード: ThreadContextClearHandler, nablarch.common.handler.threadcontext.ThreadContextClearHandler, スレッドコンテキスト変数削除ハンドラ, ハンドラクラス*

## モジュール一覧

**モジュール**:
```xml
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-fw</artifactId>
</dependency>
```

*キーワード: nablarch-fw, com.nablarch.framework, モジュール依存関係, Maven依存設定*

## 制約

> **重要**: 本ハンドラは極力手前側に配置すること。復路処理では、本ハンドラより手前のハンドラはスレッドコンテキストにアクセスできなくなる。

*キーワード: ハンドラ配置順序, スレッドコンテキストアクセス制約, 復路処理, ハンドラキュー配置*

## スレッドコンテキストの削除処理

`ThreadContextHandler` でスレッドローカル上に設定した値を全て削除する。

*キーワード: スレッドコンテキスト削除, スレッドローカル変数削除, ThreadContextHandler, 変数クリア*
