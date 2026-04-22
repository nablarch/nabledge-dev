# バッチアプリケーション編

本章ではNablarchアプリケーションフレームワークを使用してバッチアプリケーションを開発するために必要となる情報を提供する。

Nablarchのバッチアプリケーションでは、以下2種類のバッチアプリケーションのフレームワークを提供している。

jsr352/index
nablarch_batch/index

どちらのフレームワークを使用してもバッチアプリケーションを構築できるが、
以下の理由により nablarch_batch/index を使用してバッチアプリケーションを作成することを推奨する。

理由
Jakarta Batchは2020年時点で情報が少なく有識者もアサインしにくいため、nablarch_batch/index を使用してバッチアプリケーションを作成することを推奨する。

> **Tip:**
> Nablarch5u15までの解説書ではJakarta Batchに準拠したバッチアプリケーションを推奨してきましたが、2020年現在の普及状況と学習コストの高さを鑑みNablarchバッチアプリケーションを推奨とするよう方針転換しました。

> **Tip:**
> Jakarta Batchに準拠したバッチアプリケーション と Nablarchバッチアプリケーション で提供している機能の違いは、 batch-functional_comparison を参照。

functional_comparison
