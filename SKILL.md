# AgentSkill: Stiff-Sec (Hex-Stiff Hardener) 🛡️

> Prevent config leaks, unsafe execution, and misconfigured gateways in under 60 seconds.

- 🔒 **Backup-first hardening** — timestamped backups before every change
- 🔍 **Tamper detection** — SHA-256 checksum catches unauthorized config changes
- 🚨 **Credential scan** — finds plaintext tokens, keys, and secrets in your config

Audit, lock down, and self-recover OpenClaw environments. Built by OniBoniBot (👹🐰).  
**Maintained by Oni Technologies LLC**

---

## Why Stiff-Sec

- Detects real risks, not just warnings
- Applies safe fixes automatically
- Keeps a full rollback trail

---

## Backup + Recovery

- Auto backup before every change
- One-command rollback: `stiff-sec restore`
- All actions logged with undo steps

---

## Audit

- Detect plaintext secrets in config
- Validate gateway restrictions
- Check file permissions
- Flag exposed directories (`.git`, `node_modules`)

---

## Apply (Hardening)

- Locks file permissions to user-only
- Disables elevated execution by default
- Fixes proxy trust settings
- Stabilizes DNS resolution
- Marks system as secured

---

## 🚨 Output Example

```
Risk Level: HIGH
- Plaintext API key detected
- Gateway overly permissive

Action Taken:
- Key flagged
- Permissions restricted
- Backup created: openclaw.json.2026-03-28.bak

Undo:
stiff-sec restore
```

---

## Commands

```bash
stiff-sec audit     # Scan for risks — read-only, safe
stiff-sec apply     # Harden config — backup created first
stiff-sec restore   # Roll back to last known good state
```

---

*Stiff-Sec by Oni Technologies LLC · Built with paranoia. Verified against the real schema.*
