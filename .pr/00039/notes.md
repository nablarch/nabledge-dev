# Notes

## 2026-02-19

### Decision: PR-based directory structure

User requested changing from date-based (`work/YYYYMMDD/`) to issue-based organization for better traceability. All artifacts for a specific issue/PR grouped together.

### Problem: nabledge-6 output path

Initially changed nabledge-6 skill output to `.issues/xxxxx/` but user pointed out this is user-facing and would break existing workflows. Reverted to `work/YYYYMMDD/` to avoid external impact.

### Decision: .pr/ instead of .issues/

User noted work is organized by PRs, not issues. Key reasons:
- Work unit is PR, not issue (PR always exists, issue may not)
- `.pr/` more concise than `.prs/`
- Clearer naming for development workflow

### Decision: .issues/ not gitignored

Initially added `.issues/` to gitignore thinking they're local artifacts. User clarified work logs should be version controlled, only temporary files (`.tmp/`) should be ignored. Makes sense - work logs are permanent documentation.

### Decision: Repository-local .tmp/

User suggested using repository-local `.tmp/` instead of `~/tmp` for safety. Created `.claude/rules/temporary-files.md` to document policy.

### Decision: Simplified work notes format

User pointed out current work log duplicates git commit history (changed files, what changed, etc.). New format focuses on:
- Why decisions were made
- Alternatives considered
- Problems and solutions
- Learnings
- Follow-up tasks

Renamed from generic "work-log.md" pattern to standardized `notes.md` filename.

### TODO

- Issue #40: Change nabledge-6 output to `.nabledge/YYYYMMDD/` to avoid conflicts with project `work/` directories and make gitignore easier
