.. _sample-label:

サンプルハンドラ
==========================================

概要
-----

サンプルハンドラは、データベース接続を管理するハンドラである。

.. important::
   本ハンドラはハンドラキューの先頭付近に配置すること。

**クラス**: `nablarch.sample.SampleHandler`

モジュール一覧
---------------

.. code-block:: xml

   <dependency>
     <groupId>com.nablarch.framework</groupId>
     <artifactId>nablarch-sample</artifactId>
   </dependency>

.. list-table::
   :header-rows: 1

   * - プロパティ名
     - 型
     - 必須
     - デフォルト値
     - 説明
   * - sampleProperty
     - String
     - ○
     -
     - サンプルプロパティ
   * - timeout
     - int
     -
     - 30
     - タイムアウト(秒)
