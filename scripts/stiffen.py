import os, sys, json, io, stat, shutil, time, hashlib

# Force UTF-8 for console output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def confirm(prompt: str) -> bool:
    """Require explicit user confirmation before destructive changes."""
    print(f"\n⚠️  {prompt}")
    answer = input("   Type 'yes' to continue, anything else to abort: ").strip().lower()
    return answer == "yes"

def stiffen():
    print("👹 OniBoniBot Stiffener v2: Always Backup First...")

    config_path = os.path.expanduser("~/.openclaw/openclaw.json")
    backup_dir = os.path.expanduser("~/.openclaw/backups")
    os.makedirs(backup_dir, exist_ok=True)

    if not os.path.exists(config_path):
        print("❌ Error: No openclaw.json to stiffen.")
        sys.exit(1)

    # Require confirmation before making changes
    if not confirm("This will modify ~/.openclaw/openclaw.json and create a backup. Proceed?"):
        print("   Aborted.")
        sys.exit(0)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, f"openclaw.json.{timestamp}.bak")
    shutil.copy2(config_path, backup_path)
    print(f"✅ Backup created: {backup_path}")

    print("👹 Hardening the Vault...")
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)

        # Lock trusted proxies
        config.setdefault('gateway', {})['trustedProxies'] = ["127.0.0.1"]
        print("🔒 Network: Locked trustedProxies to localhost.")

        # Harden tool policy
        config.setdefault('tools', {})['elevated'] = {"enabled": False}
        deny = config['tools'].setdefault('deny', [])
        for t in ["sessions_spawn", "sessions_send"]:
            if t not in deny:
                deny.append(t)
        print("🔒 Tools: Set elevated=false, deny list updated.")

        # exec.ask
        config['tools'].setdefault('exec', {})['ask'] = "on-miss"
        print("🔒 Exec: Set tools.exec.ask to 'on-miss'.")

        # Valid node deny commands only
        config['gateway'].setdefault('nodes', {})['denyCommands'] = [
            "canvas.eval", "canvas.present"
        ]
        print("🔒 Nodes: Applied strict denyCommands.")

        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print("✅ Config stiffened.")

    except Exception as e:
        print(f"❌ Error during stiffen: {e}")
        sys.exit(1)

    # Write lockfile with SHA-256
    with open(config_path, 'rb') as f:
        sha = hashlib.sha256(f.read()).hexdigest().upper()

    lockfile_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        ".stiffened"
    )
    with open(lockfile_path, "w") as f:
        f.write(f"stiffened_at: {timestamp}\n")
        f.write(f"sha256: {sha}\n")
        f.write(f"backup: {backup_path}\n")

    print(f"🔒 Lockfile written with SHA-256: {sha[:16]}...")
    print(f"👹 Done. UNDO: python scripts/stiffen.py restore")
    sys.exit(0)

def restore():
    print("👹 OniBoniBot: Reversing the Hex-Stiff...")

    backup_dir = os.path.expanduser("~/.openclaw/backups")
    if not os.path.exists(backup_dir):
        print("❌ No backups found.")
        sys.exit(1)

    backups = sorted([f for f in os.listdir(backup_dir) if f.startswith("openclaw.json")], reverse=True)
    if not backups:
        print("❌ No openclaw.json backups found.")
        sys.exit(1)

    latest_backup = os.path.join(backup_dir, backups[0])
    config_path = os.path.expanduser("~/.openclaw/openclaw.json")

    if not confirm(f"This will restore {latest_backup} → {config_path}. Proceed?"):
        print("   Aborted.")
        sys.exit(0)

    shutil.copy2(latest_backup, config_path)
    print(f"✅ Restored from: {latest_backup}")
    sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "apply":
            stiffen()
        elif sys.argv[1] == "restore":
            restore()
        else:
            print(f"Unknown command: {sys.argv[1]}")
            print("Usage: python stiffen.py [apply|restore]")
            sys.exit(1)
    else:
        print("Usage: python stiffen.py [apply|restore]")
        sys.exit(1)
