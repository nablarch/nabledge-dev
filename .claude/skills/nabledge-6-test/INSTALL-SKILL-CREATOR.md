# Installing skill-creator

To enable dynamic skill generation in nabledge-6-test, you need to install the **skill-creator** skill from Anthropic's official skills repository.

## Automatic Marketplace Setup (Recommended)

This repository's `.claude/settings.json` already includes the Anthropic Skills marketplace configuration.

**When you open this project for the first time**, Claude Code will prompt you to install the marketplace. Simply approve it.

After marketplace installation, proceed to Step 2 below.

## Manual Installation Steps

If the automatic prompt doesn't appear, follow these steps:

### 1. Add the Anthropic Skills Marketplace

In Claude Code, run:
```
/plugin marketplace add anthropics/skills
```

### 2. Install example-skills Plugin

The skill-creator is included in the example-skills plugin. Install it:
```
/plugin install example-skills@anthropic-agent-skills
```

Or, via the interactive installer:
1. Run: `/plugin install`
2. Select: `Browse and install plugins`
3. Select: `anthropic-agent-skills`
4. Select: `example-skills`
5. Select: `Install now`

### 3. Verify Installation

Check that skill-creator is available:
```
ls ~/.claude/plugins/*/skills/skill-creator/
```

You should see:
```
SKILL.md
scripts/
  init_skill.py
  package_skill.py
```

## What skill-creator Provides

**Purpose**: Create and update skills that extend Claude's capabilities

**Features**:
- **Skill initialization**: `init_skill.py` - Generate skill template
- **Skill packaging**: `package_skill.py` - Package skill as .skill file
- **Design guidance**: Best practices for token efficiency and reusability

**6-step process**:
1. Understand concrete examples
2. Plan reusable content
3. Initialize skill
4. Edit skill
5. Package skill
6. Iterate and improve

## Integration with nabledge-6-test

Once installed, nabledge-6-test Workflow 4 (generate-scenario) will use skill-creator to:

1. Generate test-specific skills dynamically
2. Create reusable test scenario runners
3. Package scenarios as standalone skills

**Example**:
```
nabledge-6-test generate-scenario
→ Creates handlers-006 scenario
→ Uses skill-creator to generate test-handlers-006 skill
→ Packages as standalone skill
→ User can run: /test-handlers-006
```

## Manual Installation (Alternative)

If you prefer manual installation:

1. Clone the repository:
   ```bash
   git clone https://github.com/anthropics/skills.git /tmp/anthropic-skills
   ```

2. Copy skill-creator to your skills directory:
   ```bash
   cp -r /tmp/anthropic-skills/skills/skill-creator ~/.claude/skills/
   ```

3. Verify:
   ```bash
   ls ~/.claude/skills/skill-creator/
   ```

## Troubleshooting

### Plugin marketplace not found

If `/plugin marketplace add` fails:
- Ensure you're running Claude Code (not Claude.ai)
- Check Claude Code version (skill-creator requires recent version)
- Try updating Claude Code

### skill-creator not available after install

- Restart Claude Code session
- Check plugin status: `/plugin list`
- Verify installation directory: `~/.claude/plugins/`

## Next Steps

After installation:
1. Verify skill-creator works: Ask Claude "Use skill-creator to help me create a new skill"
2. Proceed with nabledge-6-test integration (Task #8)
3. Test dynamic scenario skill generation

## References

- [anthropics/skills GitHub Repository](https://github.com/anthropics/skills)
- [skill-creator Source](https://github.com/anthropics/skills/tree/main/skills/skill-creator)
- [Claude Skills Documentation](https://support.claude.com/en/articles/12512198-creating-custom-skills)
