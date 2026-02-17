# Permission Settings

Permissions are controlled by `.claude/settings.json`.

## Policy

- **allow**: Frequently used commands (git, npm, pytest, etc.)
- **deny**: Security exceptions within allowed commands
- **ask**: Everything else (default)

## Security Restrictions

Commands in `allow` have specific `deny` exceptions:

**Network protection:**
- Deny `git clone http*`, `git clone git@*` (prevent malicious code download)

**Confidential data:**
- Deny `.env`, `.aws`, `.ssh` in Read/Edit/Write operations

**Host protection (WSL):**
- Deny `/mnt/*`, `*.exe` access (prevent Windows host access)

**System protection:**
- Deny `rm -rf /`, `rm -rf /*` (prevent root deletion)

Destructive commands not in `allow` (`sudo`, `dd`, `curl`, `reboot`) automatically require user confirmation.
