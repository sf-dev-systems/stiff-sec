# Changelog — Stiff-Sec

---

## [2.1.0] — 2026-04-09

### Changed
- `stiffen.py` now accepts `--exec-ask {always,on-miss,off}` — exec policy is a governance choice, not hardcoded
- Removed automatic mutation of `gateway.nodes.denyCommands` — schema/profile decision left to config owner
- Migrated CLI to `argparse` with `--yes` flag for non-interactive/automation use
- Lockfile now records `exec_ask` value used at stiffen time

### Added
- README governance section: `on-miss` vs `always` tradeoff documented
- Usage examples for `--exec-ask` and `--yes` flags

---

## [2.0.0] — 2026-04-09

### Added
- Placeholder filtering in `audit.py` — stops false positives on `REDACTED`, `__OPENCLAW_REDACTED__`, and common example values
- Strict `fullmatch` regex for credential values — reduces noisy partial matches
- Risk summary block at end of audit: `Risk Level: LOW|ELEVATED` + remediation steps
- Exit codes: `0` clean, `1` runtime error, `2` findings detected
- Confirmation prompt in `stiffen.py` before any config mutation
- Confirmation prompt in `restore()` before overwriting live config
- SHA-256 written to lockfile after hardening — enables accurate tamper detection

### Fixed
- Lockfile path resolution in `audit.py` was using incorrect directory traversal
- `stiffen.py` was not writing SHA-256 to lockfile, breaking integrity checks

---

## [1.0.0] — 2026-03-28

### Initial release
- `audit.py` — read-only scan for plaintext credentials, integrity check, hardening state
- `stiffen.py` — backup-first hardening: trustedProxies, elevated tools, deny list, exec.ask
- SHA-256 lockfile baseline
- `restore()` — one-command rollback to last backup
