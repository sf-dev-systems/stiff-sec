import os, sys, json, io, re, hashlib

# Force UTF-8 for console output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Patterns that indicate a live credential field
CREDENTIAL_FIELDS = re.compile(
    r'(apikey|api_key|bottoken|bot_token|auth\.token|token|secret|password|bearer|credential)',
    re.IGNORECASE
)

# Strict match: 20+ char alphanumeric (fullmatch to reduce noise)
CREDENTIAL_VALUE = re.compile(r'^[A-Za-z0-9_\-]{20,}$')

# Known placeholder values — skip these to avoid false positives
PLACEHOLDER_VALUES = {
    "REDACTED", "YOUR_TOKEN_HERE", "YOUR_API_KEY", "EXAMPLE_TOKEN",
    "SAMPLE_KEY", "PLACEHOLDER", "INSERT_TOKEN", "ADD_KEY_HERE",
    "__OPENCLAW_REDACTED__"
}

def is_placeholder_secret(value: str) -> bool:
    if not isinstance(value, str):
        return True
    v = value.strip().upper()
    if v in {p.upper() for p in PLACEHOLDER_VALUES}:
        return True
    if "example" in v.lower() or "sample" in v.lower() or "your_" in v.lower():
        return True
    return False

def scan_for_secrets(obj, path=""):
    """Recursively scan a parsed JSON object for likely plaintext credentials."""
    findings = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            current_path = f"{path}.{k}" if path else k
            if CREDENTIAL_FIELDS.search(k):
                if isinstance(v, str) and CREDENTIAL_VALUE.fullmatch(v) and not is_placeholder_secret(v):
                    findings.append((current_path, v[:6] + "..." + v[-4:]))
            findings.extend(scan_for_secrets(v, current_path))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            findings.extend(scan_for_secrets(item, f"{path}[{i}]"))
    return findings

def verify_checksum(config_path):
    """Check openclaw.json SHA-256 against .stiffened lockfile."""
    stiffened_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
        ".stiffened"
    )
    if not os.path.exists(stiffened_path):
        print("⚠️  No .stiffened lockfile found — integrity check skipped.")
        return

    with open(config_path, 'rb') as f:
        current_hash = hashlib.sha256(f.read()).hexdigest().upper()

    with open(stiffened_path, 'r') as f:
        content = f.read()

    stored = None
    for line in content.splitlines():
        if line.startswith("sha256:"):
            stored = line.split(":", 1)[1].strip().upper()
            break

    if stored is None:
        print("⚠️  No SHA-256 found in .stiffened — run stiffen.py apply to set baseline.")
    elif current_hash == stored:
        print("✅ Integrity check PASSED — config matches stored hash.")
    else:
        print("🚨 INTEGRITY ALERT: openclaw.json has been modified since last stiffening!")
        print(f"   Stored : {stored[:16]}...{stored[-4:]}")
        print(f"   Current: {current_hash[:16]}...{current_hash[-4:]}")
        print("   Action : Review changes or run stiffen.py apply to re-baseline.")

def audit():
    print("🛡️  OniBoniBot Stiff-Sec Audit v2...")
    print()

    config_path = os.path.expanduser("~/.openclaw/openclaw.json")

    if not os.path.exists(config_path):
        print(f"❓ openclaw.json not found at {config_path}")
        sys.exit(1)

    print(f"✅ Found openclaw.json at {config_path}")

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ ERROR: Could not parse openclaw.json: {e}")
        sys.exit(1)

    # --- Secret scan ---
    print()
    print("🔍 Scanning for plaintext credentials...")
    findings = scan_for_secrets(config)
    if findings:
        print(f"⚠️  FOUND {len(findings)} potential plaintext credential(s):")
        for path, preview in findings:
            print(f"   [{path}] → value starts with: {preview}")
        print("   Recommendation: replace with REDACTED or move to .env")
    else:
        print("✅ No plaintext credentials detected.")

    # --- Integrity check ---
    print()
    print("🔒 Checking config integrity against .stiffened lockfile...")
    verify_checksum(config_path)

    # --- Hardening state check ---
    print()
    print("🔧 Checking hardening state...")

    checks = [
        ("gateway.trustedProxies = [127.0.0.1]", lambda c: c.get("gateway", {}).get("trustedProxies") == ["127.0.0.1"]),
        ("tools.elevated.enabled = false",        lambda c: c.get("tools", {}).get("elevated", {}).get("enabled") == False),
        ("tools.exec.ask = on-miss|always",       lambda c: c.get("tools", {}).get("exec", {}).get("ask") in ["on-miss", "always"]),
        ("tools.deny includes sessions_spawn",    lambda c: "sessions_spawn" in c.get("tools", {}).get("deny", [])),
    ]

    issues = 0
    for label, check_fn in checks:
        try:
            ok = check_fn(config)
        except Exception:
            ok = False
        status = "✅" if ok else "⚠️  MISSING"
        if not ok:
            issues += 1
        print(f"   {status}  {label}")

    # --- Risk summary ---
    print()
    total_issues = len(findings) + issues
    if total_issues == 0:
        print("✅ Risk Level: LOW — no findings.")
    else:
        print(f"⚠️  Risk Level: ELEVATED — {total_issues} finding(s).")
        print("   Remediation:")
        if findings:
            print("   • Replace plaintext credentials with REDACTED or move to .env")
        if issues:
            print("   • Run: python scripts/stiffen.py apply")

    print()
    print("🛡️  Audit complete.")
    sys.exit(2 if total_issues > 0 else 0)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "audit":
        audit()
    else:
        print("Usage: python audit.py audit")
        sys.exit(1)
