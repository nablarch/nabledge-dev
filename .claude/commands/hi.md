---
name: hi
description: Full development workflow from issue to PR
argument-hint: [issue# or pr#]
allowed-tools: Bash, Task, AskUserQuestion, Glob, Grep, Read, Edit, Write, Skill
---

Execute full development workflow from issue/PR to review request.

# Instructions

1. Get or create issue:
   - If $ARGUMENTS provided: Use as issue number
   - If no arguments: Use AskUserQuestion to ask user
     - Question: "Do you have an existing issue number?"
     - Options: "Yes, I have issue number" / "No, create new issue"
   - If user selects "No, create new issue":
     ```bash
     # Ask user for issue details using AskUserQuestion
     # - Title (required)
     # - Situation (current state)
     # - Pain (problem description)
     # - Benefit (who benefits and how)
     # - Success criteria (list of checkboxes)

     # Create issue using gh CLI
     gh issue create \
       --title "$title" \
       --body "$(cat <<EOF
### Situation
$situation

### Pain
$pain

### Benefit
$benefit

### Success Criteria
$success_criteria
EOF
)"

     # Get created issue number
     issue_number=$(gh issue list --limit 1 --json number --jq '.[0].number')
     echo "Created issue #$issue_number"
     ```
2. Sync current branch with main if needed:
   ```bash
   current_branch=$(git branch --show-current)
   # If current branch is workX, sync with main first
   if [[ "$current_branch" =~ ^work[0-9]+$ ]]; then
     echo "Syncing $current_branch with main..."
     git fetch origin main
     git merge --ff-only origin/main
   fi
   ```
3. Fetch issue details: `gh issue view $NUMBER --json title,body`
4. Create branch if needed:
   ```bash
   # Extract first 2-3 meaningful words from issue title
   # Convert to lowercase, replace spaces/special chars with hyphens
   # Format: {issue_number}-{description}
   # Example: "Add user authentication" -> "60-add-user-auth"

   # Generate description from issue title
   description=$(echo "$issue_title" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9 ]//g' | awk '{print $1"-"$2"-"$3}' | sed 's/-$//')
   branch_name="${issue_number}-${description}"

   # Check if branch exists
   if git rev-parse --verify "$branch_name" &>/dev/null; then
     echo "Branch $branch_name already exists, checking out..."
     git checkout "$branch_name"
   else
     echo "Creating branch $branch_name..."
     git checkout -b "$branch_name"
   fi
   ```
5. Analyze requirements: Use Glob/Grep to find relevant files
6. Implement changes: Use Task tool with general-purpose agent
   - Pass full issue body, success criteria, relevant files to agent
   - Agent will read files, implement changes, ask questions if unclear
7. Run tests based on change type:

   **For source code changes:**
   - Auto-detect framework (pytest, npm test, mvn test, gradle test)
   - Run existing unit tests
   - If no tests exist: Propose test rules and create tests

   **For prompts/workflows/documentation:**
   - Execute with agent to verify functionality (simulation/actual run)
   - Verify workflow steps work as documented
   - Test example scenarios if applicable
8. Create PR: Use Skill tool - `Skill(skill: "pr", args: "create")`
9. Request review from user

# Important

- Use Glob/Grep tools for file search (not bash find/grep)
- Use Task tool for implementation (not direct edits)
- Use Skill tool for git commit and PR creation
- Never manually run git commit or gh pr create commands
- Ask questions when requirements are unclear
- Works in both main repo and worktrees (work1, work2, etc.)
- In worktrees: Creates feature branch from current workX branch
