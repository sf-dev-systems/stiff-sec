# 🛡️ Stiff-Sec — The Hex-Stiff Hardener for OpenClaw

**Built by OniBoniBot 👹🐰 for operators who don't trust "set it and forget it."**  
**Maintained by Oni Technologies LLC**

---

## What Is This?

Stiff-Sec is a two-part security skill for OpenClaw that does what generic 
auditors don't: it actually *fixes* what it finds.

Most security tools hand you a report and wish you luck.  
Stiff-Sec backs up your config, hardens it, checksums it, and tells you 
if anything touched it while you weren't looking.

---

## The Two-Part Design

| Script | What it does |
|---|---|
| `audit.py` | Read-only scan — finds plaintext credentials, checks hardening state, verifies config integrity against SHA-256 checksum |
| `stiffen.py` | Applies 4 targeted hardening mutations, backs up first, writes a signed lockfile |

**Audit never changes anything. Stiffen never runs without a backup.**

---

## What It Hardens

| Field | Before | After | Threat Mitigated |
|---|---|---|---|
| `gateway.trustedProxies` | open | `["127.0.0.1"]` | Proxy spoofing |
| `tools.elevated.enabled` | true | `false` | Host-level command escalation |
| `tools.deny` | empty | blocks `sessions_spawn`, `sessions_send` | Agent-to-agent lateral movement |
| `gateway.nodes.denyCommands` | missing | `["canvas.eval","canvas.present"]` | Node execution surface |
| `tools.exec.ask` | off | `"on-miss"` | Unreviewed shell commands |

---

## Tamper Detection

Every time you stiffen, a SHA-256 hash of your `openclaw.json` is written 
to `.stiffened`. Run `audit.py` anytime — if a skill, update, or anything 
else has touched your config, you'll know immediately:

```
🚨 INTEGRITY ALERT: openclaw.json has been modified since last stiffening!
   Stored : 03CA38...FBB6
   Current: A91F22...CC03
```

---

## Credential Scanner

Audit v2 scans your entire config recursively for plaintext credentials — 
not just `apiKey`, but `botToken`, `auth.token`, `secret`, `password`, 
`bearer`, and any value over 20 characters that looks like a key.

```
⚠️  FOUND 1 potential plaintext credential(s):
   [channels.telegram.botToken] → value starts with: AAFNAA...ZOo
   Recommendation: replace with REDACTED or move to .env
```

---

## Usage

```bash
# Audit only (safe, read-only)
python scripts/audit.py audit

# Harden with default exec policy (on-miss)
python scripts/stiffen.py apply

# Harden with explicit exec policy
python scripts/stiffen.py apply --exec-ask always
python scripts/stiffen.py apply --exec-ask on-miss
python scripts/stiffen.py apply --exec-ask off

# Harden non-interactively (CI/automation)
python scripts/stiffen.py apply --yes --exec-ask on-miss

# Undo last hardening
python scripts/stiffen.py restore
```

---

## Governance: `exec.ask` Policy

`tools.exec.ask` controls whether the agent prompts for approval before running shell commands. Stiff-Sec does **not** hardcode this value — it's a governance decision for the config owner.

| Value | Behavior |
|:------|:---------|
| `always` | Every exec requires explicit approval — maximum control |
| `on-miss` | Prompts only when no prior approval exists — balanced |
| `off` | No prompts — use only in fully trusted automation |

Pass your choice via `--exec-ask`. If unsure, `on-miss` is the safe default.

> **Note:** `gateway.nodes.denyCommands` is intentionally **not** auto-written by Stiff-Sec. This is a schema/profile decision that varies by OpenClaw release — set it manually in your config.

---

## Backup Policy

Stiff-Sec follows **Oni Protocol** — backup before *everything*:

- Timestamped backup created in `~/.openclaw/backups/` before any change
- `.stiffened` lockfile marks the hardened state with timestamp + hash
- One command to fully restore: `stiffen.py restore`

---

## Who Is This For?

- OpenClaw operators running local or LAN-exposed gateways
- Anyone who's ever had a skill modify their config without asking
- Anyone whose ADHD moves faster than their safety checks 😅
- Anyone who wants to know *exactly* what state their install is in

---

## Built With Paranoia. Verified Against the Real Schema.

Every hardening field in Stiff-Sec was verified against the live OpenClaw 
config schema before being written. No hallucinated fields. No config 
pollution. If it's in here, it works.

---

*OniBoniBot 👹🐰*  
*© Oni Technologies LLC*
