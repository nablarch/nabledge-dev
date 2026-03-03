.. _sample-label:

サンプルハンドラ
==========================================

概要
-----

サンプルハンドラは、データベース接続を管理するハンドラである。

.. important::
   本ハンドラはハンドラキューの先頭付近に配置すること。

詳細は :ref:`thread_context_handler` を参照。また、:ref:`データベース接続 <database_connection>` の設定も必要。

関連ドキュメントは :doc:`../configuration/database` を参照。

設定ファイルのサンプルは :download:`sample.xml <sample.xml>` を参照。

**クラス**: :java:extdoc:`SampleHandler <nablarch.sample.SampleHandler>`、:java:extdoc:`nablarch.core.ThreadContext`

外部ライブラリ: `Jackson(外部サイト、英語) <https://github.com/FasterXML/jackson>`_

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
