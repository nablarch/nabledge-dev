# Issue #150: Phase C不合格の根本原因修正

## 方針転換
元のIssue: 3ファイルの個別修正。
実際: 根本原因対応（セクションID連番化、processing_patterns廃止、Phase G廃止、biz_samplesリマップ）。
同時解決: #149, #151, #166。

## レビュー指摘修正
- P1: splitリネーム失敗 → title_to_section_id復元で旧ファイル名を再構築
- P2: skill JSON cross-fileリンクパス欠落 → 相対パス計算
- P4: verify_integrity.pyチェック欠落 → V2/V4/V5/V6/V16/V17追加
