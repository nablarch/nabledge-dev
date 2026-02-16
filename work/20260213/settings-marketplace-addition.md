# Added Anthropic Skills Marketplace to settings.json

**Date**: 2026-02-13

## Summary

Added `extraKnownMarketplaces` configuration to `.claude/settings.json` to automatically prompt users to install the Anthropic Skills marketplace when they open the project.

## Changes Made

### 1. Updated `.claude/settings.json`

Added marketplace configuration:

```json
{
  "extraKnownMarketplaces": {
    "anthropic-agent-skills": {
      "source": {
        "source": "github",
        "repo": "anthropics/skills"
      }
    }
  }
}
```

### 2. Updated INSTALL-SKILL-CREATOR.md

Added "Automatic Marketplace Setup" section explaining:
- Marketplace is pre-configured in settings.json
- Claude Code will prompt on first project open
- Users just need to approve and then install the plugin

### 3. Updated README.md

Updated two sections:
- "Generate New Scenario" section (lines 108-114)
- "skill-creator Integration > Installation" section (lines 495-511)

Both now mention:
- Marketplace is pre-configured
- Automatic installation prompt
- Simplified installation steps

## How It Works

### User Experience Flow

1. **User opens project for the first time**
   - Claude Code reads `.claude/settings.json`
   - Detects `extraKnownMarketplaces` configuration
   - **Prompts user to install "anthropic-agent-skills" marketplace**

2. **User approves marketplace installation**
   - Claude Code downloads marketplace catalog
   - Marketplace appears in `/plugin install` browser

3. **User installs plugin**
   ```
   /plugin install example-skills@anthropic-agent-skills
   ```

4. **skill-creator is now available**
   - Can be used in `nabledge-6-test generate-scenario`

### What Is NOT Automatic

- ❌ Plugin installation (user must run `/plugin install`)
- ❌ skill-creator activation (automatic after plugin install)

### What IS Automatic

- ✅ Marketplace registration prompt
- ✅ Marketplace catalog download (after user approval)
- ✅ Marketplace appears in plugin browser

## Benefits

### Before This Change

User had to:
1. Manually run `/plugin marketplace add anthropics/skills`
2. Then run `/plugin install example-skills@anthropic-agent-skills`
3. Remember these commands or find them in documentation

### After This Change

User only needs to:
1. **Approve the installation prompt** (automatic on project open)
2. Run `/plugin install example-skills@anthropic-agent-skills`

**One less command to remember!**

## Settings.json Configuration Details

### extraKnownMarketplaces

**Purpose**: Define project-specific plugin marketplaces

**Format**:
```json
{
  "extraKnownMarketplaces": {
    "<marketplace-id>": {
      "source": {
        "source": "github",
        "repo": "<owner>/<repo>"
      }
    }
  }
}
```

**Behavior**:
- When project is opened/trusted, Claude Code prompts to install listed marketplaces
- After approval, marketplace catalog is downloaded
- Plugins from marketplace become installable via `/plugin install <plugin>@<marketplace-id>`

**Does NOT**:
- Automatically install plugins
- Require plugins to be installed
- Block functionality if user declines

### Alternative: strictKnownMarketplaces

**Not used** because:
- Only available in Managed settings (enterprise)
- Enforces whitelist (too restrictive for our use case)
- We want optional, not mandatory

## Comparison with Other Approaches

### Approach 1: No settings.json configuration (previous)

**Pros**:
- No assumptions about user preferences
- Complete user control

**Cons**:
- Users must remember/find installation commands
- Extra step in onboarding
- Higher barrier to use skill-creator integration

### Approach 2: extraKnownMarketplaces (current) ✅

**Pros**:
- Automatic prompt on project open
- One less command to remember
- Clear onboarding experience
- Still requires user approval (not forced)

**Cons**:
- Users who don't want marketplace see a prompt (can decline)

### Approach 3: enabledPlugins

**Why not used**:
- Only controls **already installed** plugins
- Doesn't install or prompt for installation
- Would require plugins to be installed first

## Testing

To test this change:

1. **Clone the repository** to a new location (or remove marketplace if already added)
2. **Open project in Claude Code**
3. **Verify prompt appears**: "Install marketplace 'anthropic-agent-skills'?"
4. **Approve installation**
5. **Verify marketplace is available**:
   ```
   /plugin install
   → Browse plugins
   → Should see "anthropic-agent-skills"
   ```
6. **Install example-skills**:
   ```
   /plugin install example-skills@anthropic-agent-skills
   ```
7. **Verify skill-creator is available**:
   ```bash
   ls ~/.claude/plugins/*/skills/skill-creator/
   ```

## Documentation Updated

- ✅ `.claude/settings.json` - Added marketplace configuration
- ✅ `INSTALL-SKILL-CREATOR.md` - Added "Automatic Marketplace Setup" section
- ✅ `README.md` - Updated installation instructions in two places

## Related Issues

- Issue #15: skill-creator integration requirement
- This change makes skill-creator installation easier for users

## Future Enhancements

Potential improvements:
1. **Session start hook**: Check if skill-creator is installed, show helper message if not
2. **README badge**: Add badge showing "Anthropic Skills Marketplace Configured"
3. **Auto-detection in nabledge-6-test**: Detect if skill-creator is available before offering standalone skill generation

## References

- [Claude Code settings.json schema](https://json.schemastore.org/claude-code-settings.json)
- [Plugin Marketplaces Documentation](https://code.claude.com/docs/en/plugin-marketplaces.md)
- [Anthropic Skills Repository](https://github.com/anthropics/skills)
- Research agent output: agentId a6d01f1
