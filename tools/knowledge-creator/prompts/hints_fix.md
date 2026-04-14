# Hints Fix Prompt

You are a fixer for hints in a Nablarch knowledge file section.
Add the missing terms listed in the findings below.

## Finding(s) to fix

```json
{FINDINGS_JSON}
```

## Current Section Text (for reference, DO NOT modify)

```
{SECTION_TEXT}
```

## Current Hints

```json
{CURRENT_HINTS}
```

## Instructions

Add the missing terms to the hints array. Keep all existing hints.
Do not remove or rename any existing hint.

Respond with ONLY a JSON object:
```json
{"hints": ["existing_hint_1", "existing_hint_2", "new_hint", ...]}
```
