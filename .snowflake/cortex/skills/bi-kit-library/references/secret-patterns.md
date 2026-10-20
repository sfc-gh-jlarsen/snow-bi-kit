# Secret and risky-setting patterns

Grep the whole project (skip `.git/`, `.venv/`, `node_modules/`) with each pattern. Ignore lines that are clearly placeholders (`<your-password>`, `example`, `changeme`) or comments explaining what not to do. A finding here can't be cleared by opinion; only by removing it.

| Finding | Severity | Regex | Why it matters | Fix |
|---|---|---|---|---|
| Password in code | fix_now | `(?i)\b(password\|passwd\|pwd)\b['"]?\s*[:=]\s*['"][^'"\s]{4,}['"]` | Anyone who can read the code can log in as you | Delete it, change the password, use the app's Snowflake connection |
| Token or key in code | fix_now | `(?i)\b(token\|api[_-]?key\|secret\|pat\|access[_-]?key)\b['"]?\s*[:=]\s*['"][A-Za-z0-9_\-\.=+/]{16,}['"]` | Same as a password | Remove and rotate it; use Snowflake secrets |
| Private key | fix_now | `-----BEGIN (RSA \|ENCRYPTED \|EC )?PRIVATE KEY-----` | Full login for whoever has it | Remove the file; rotate the key |
| AWS access key | fix_now | `\bAKIA[0-9A-Z]{16}\b` | Cloud account access | Remove and rotate |
| Connection string with password | fix_now | `(?i)snowflake://[^:/\s]+:[^@\s]+@` | Password in plain text | Use the app's connection |
| Admin role in code | fix_now | `(?i)(use\s+role\s+\|role['"]?\s*[:=]\s*['"])(accountadmin\|securityadmin\|sysadmin\|orgadmin)\b` | Every viewer effectively gets admin-level data access | Use the shared-app role from standards |
| Named user in code | consider | `(?i)['"]user['"]\s*:\s*['"][^'"<{$]+['"]` | Tied to one person's login; breaks when they leave | Use the app's own connection |
| Browser login in app | consider | `(?i)authenticator\s*[:=]\s*['"]externalbrowser['"]` | Only works on your laptop | Deployed apps use their Snowflake connection |
| `.env` file | consider | file name matches `(^\|/)\.env(\..*)?$` | Usually holds credentials; easy to share by accident | Keep it out of what you share |

(In the table, `\|` is an escaped `|`; use a plain `|` when grepping.)
