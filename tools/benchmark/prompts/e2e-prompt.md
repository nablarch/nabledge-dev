以下のワークフローに従って質問に回答してください。

## ワークフロー
{workflow}

## 質問
{question}

## ワークフローに加えてやって欲しいこと

質問テキストに `処理方式:` と `目的:` が含まれている場合、hearing_answer は確定済みです。Step 1 と Step 2 はスキップし、Step 3 から開始してください。

Step 8 で final_answer を出力した後、以下を出力してください。

## Workflow Details
{
  "hearing": {
    "processing_type": "<Step 1 で確定した処理方式、または質問テキストの `処理方式:` の値。null 可>",
    "purpose": "<Step 1 で確定した目的、または質問テキストの `目的:` の値>"
  },
  "stage2_sections": [
    {"file": "<ファイルパス>", "section_id": "<sN>", "relevance": "<high|partial>"}
  ],
  "read_sections": [
    "<Step 4 で read-sections.sh に渡した section ID（file.json:sN 形式）>"
  ],
  "answer_sections": {
    "used": [
      {"ref": "<file.json:sN>", "reason": "<この section を回答で使った理由（1文）>"}
    ],
    "unused": [
      {"ref": "<file.json:sN>", "reason": "<読んだが回答で使わなかった理由（1文）>"}
    ]
  }
}
