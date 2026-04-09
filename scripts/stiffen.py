import argparse, os, sys, json, io, shutil, time, hashlib

# Force UTF-8 for console output on Windows
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

CONFIG_PATH   = os.path.expanduser("~/.openclaw/openclaw.json")
BACKUP_DIR    = os.path.expanduser("~/.openclaw/backups")
LOCKFILE_PATH = os.path.expanduser("~/.openclaw/.stiffened")

EXEC_ASK_VALUES = {"always", "on-miss", "off"}


def confirm(prompt: str, yes: bool = False) -> bool:
    if yes:
        print(f"  [--yes] Auto-confirmed: {prompt}")
        return True
    print(f"\n⚠️  {prompt}")
    answer = input("   Type 'yes' to continue, anything else to abort: ").strip().lower()
    return answer == "yes"


def stiffen(exec_ask: str = "on-miss", yes: bool = False) -> int:
    print("👹 OniBoniBot Stiffener v2.1: Always Backup First...")

    if not os.path.exists(CONFIG_PATH):
        print("❌ Error: No openclaw.json to stiffen.")
        return 1

    if not confirm("This will modify ~/.openclaw/openclaw.json and create a backup. Proceed?", yes):
        print("   Aborted.")
        return 0

    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"openclaw.json.{timestamp}.bak")
    shutil.copy2(CONFIG_PATH, backup_path)
    print(f"✅ Backup created: {backup_path}")

    print("👹 Hardening the Vault...")
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
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

        # exec.ask — governance choice, not hardcoded
        config['tools'].setdefault('exec', {})['ask'] = exec_ask
        print(f"🔒 Exec: Set tools.exec.ask to '{exec_ask}' (policy choice).")

        # NOTE: gateway.nodes.denyCommands intentionally NOT auto-written.
        # This is a schema/profile decision for the config owner, not Stiff-Sec.

        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        print("✅ Config stiffened.")

    except Exception as e:
        print(f"❌ Error during stiffen: {e}")
        return 1

    # Write lockfile with SHA-256
    with open(CONFIG_PATH, 'rb') as f:
        sha = hashlib.sha256(f.read()).hexdigest().upper()

    with open(LOCKFILE_PATH, "w", encoding='utf-8') as f:
        f.write(f"stiffened_at: {timestamp}\n")
        f.write(f"sha256: {sha}\n")
        f.write(f"backup: {backup_path}\n")
        f.write(f"exec_ask: {exec_ask}\n")

    print(f"🔒 Lockfile written: {LOCKFILE_PATH}")
    print(f"   SHA-256: {sha[:16]}...")
    print(f"👹 Done. UNDO: python scripts/stiffen.py restore")
    return 0


def restore(yes: bool = False) -> int:
    print("👹 OniBoniBot: Reversing the Hex-Stiff...")

    if not os.path.exists(BACKUP_DIR):
        print("❌ No backups found.")
        return 1

    backups = sorted(
        [f for f in os.listdir(BACKUP_DIR) if f.startswith("openclaw.json")],
        reverse=True
    )
    if not backups:
        print("❌ No openclaw.json backups found.")
        return 1

    latest = os.path.join(BACKUP_DIR, backups[0])
    if not confirm(f"This will restore {latest} → {CONFIG_PATH}. Proceed?", yes):
        print("   Aborted.")
        return 0

    shutil.copy2(latest, CONFIG_PATH)
    print(f"✅ Restored from: {latest}")
    return 0


def main():
    parser = argparse.ArgumentParser(
        prog="stiffen.py",
        description="Stiff-Sec: OpenClaw config hardener"
    )
    sub = parser.add_subparsers(dest="command")

    apply_p = sub.add_parser("apply", help="Harden openclaw.json")
    apply_p.add_argument(
        "--exec-ask",
        choices=list(EXEC_ASK_VALUES),
        default="on-miss",
        help="Value for tools.exec.ask (governance choice, default: on-miss)"
    )
    apply_p.add_argument("--yes", action="store_true", help="Skip confirmation prompt")

    restore_p = sub.add_parser("restore", help="Restore last backup")
    restore_p.add_argument("--yes", action="store_true", help="Skip confirmation prompt")

    args = parser.parse_args()

    if args.command == "apply":
        sys.exit(stiffen(exec_ask=args.exec_ask, yes=args.yes))
    elif args.command == "restore":
        sys.exit(restore(yes=args.yes))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
