"""Audit the explicit public manifest and optional distributable ZIP."""
import argparse
import json
from pathlib import Path
import re
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
SKILL_FILES = (
    "SKILL.md", "LICENSE", "agents/openai.yaml",
    "assets/agent-prompt.md", "assets/公开教程.md",
    "assets/setup-state.example.json", "assets/ledger-fields.json",
    "references/onboarding.md", "references/credentials.md",
    "references/verification.md", "references/income.md",
    "references/automation.md", "references/ocr-fallback.md",
    "references/agent-cli.md", "references/blank-ledger.md",
    "references/shortcut-build.md",
    "scripts/weekly_summary.py", "scripts/ocr_repair.py", "scripts/lark_adapter.py",
)
PUBLIC_FILES = (
    ".gitattributes", ".gitignore", "AGENTS.md", "README.md", "INSTALL.md",
    "LICENSE", "PRIVACY.md", "scripts/audit_release.py",
    "scripts/install.py", "scripts/package_release.py",
    "tests/test_lark_adapter.py", "tests/test_ocr_repair.py", "tests/test_weekly_summary.py",
) + tuple("cq-jizhang/" + name for name in SKILL_FILES)
PATTERNS = {
    "personal filesystem path": re.compile(r"[A-Za-z]:[\\/]Users[\\/][A-Za-z0-9_.-]+|/(?:Users|home)/[A-Za-z0-9_.-]+/"),
    "email address": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "phone number": re.compile(r"(?<!\w)1[3-9][0-9]{9}(?!\w)"),
    "real user or chat identifier": re.compile(r"\b(?:ou|oc)_[A-Za-z0-9]{12,}\b"),
    "private Feishu resource URL": re.compile(r"https?://[A-Za-z0-9-]+\.feishu\.cn/(?:base|wiki|docx)/[A-Za-z0-9]+"),
    "private shortcut share": re.compile(r"icloud\.com/shortcuts/[A-Za-z0-9]+"),
    "credential-like value": re.compile(r"\b(?:sk-[A-Za-z0-9_-]{20,}|gh[oprs]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[A-Z0-9]{16}|cli_[A-Za-z0-9]{12,})\b"),
}


def audit_text(name, payload):
    content = payload.decode("utf-8")
    for label, pattern in PATTERNS.items():
        if pattern.search(content):
            raise ValueError(f"{name}: detected {label}; matched value withheld")
    if name.endswith(".md"):
        for target in re.findall(r"\]\(([^)]+)\)", content):
            if target.startswith(("https://", "http://", "#")):
                continue
            resolved = (ROOT / name).parent.joinpath(target.split("#", 1)[0]).resolve()
            if not resolved.is_relative_to(ROOT) or not resolved.is_file():
                raise ValueError(f"{name}: broken or escaping relative link")
            if resolved.relative_to(ROOT).as_posix() not in PUBLIC_FILES:
                raise ValueError(f"{name}: linked resource omitted from manifest")


def audit_state():
    state = json.loads((ROOT / "cq-jizhang/assets/setup-state.example.json").read_text(encoding="utf-8"))
    for key in ("owner_ref", "base_url", "app_token", "table_id", "settings_ref",
                "weekly_budget", "notification_target_ref", "task_id", "conversation_ref",
                "next_run_at", "last_verified_at", "budget_effective_week_start"):
        if state.get(key) is not None:
            raise ValueError(f"Populated private example field: {key}")
    if any(state["checkpoints"].values()) or state["credential_configured"]:
        raise ValueError("Example contains completed setup")
    if any(state[key] for key in ("excluded_test_record_ids", "last_sent_report_keys", "budget_history")):
        raise ValueError("Example contains account history")
    fallback = state["ocr_fallback"]
    if fallback["enabled"] or fallback["repair_state"] or fallback["extra_task_id"] is not None:
        raise ValueError("Example contains active fallback state")
    runtime = state["agent_runtime"]
    for key in ("host", "cli_version", "credential_profile_ref", "bridge_ref",
                "scheduler_owner_ref", "expected_account_ref", "account_check_method"):
        if runtime.get(key) is not None:
            raise ValueError(f"Example contains runtime identity: {key}")
    if any(runtime[key] for key in ("cli_verified", "auth_verified", "bridge_verified", "previous_task_stopped_verified")):
        raise ValueError("Example contains verified runtime state")


def audit_folder():
    actual = set()
    for path in ROOT.rglob("*"):
        relative = path.relative_to(ROOT)
        if any(part in (".git", "__pycache__", "dist") for part in relative.parts):
            continue
        if path.is_symlink():
            raise ValueError("Symlink in public tree")
        if path.is_file():
            actual.add(relative.as_posix())
    if actual != set(PUBLIC_FILES):
        raise ValueError("Public files differ from the explicit manifest")
    for name in PUBLIC_FILES:
        audit_text(name, (ROOT / name).read_bytes())
    audit_state()


def audit_zip(path):
    expected = {"cq-jizhang/" + name for name in SKILL_FILES}
    with ZipFile(path) as archive:
        if archive.testzip() or archive.comment:
            raise ValueError("Invalid archive or unexpected comment")
        if len(archive.namelist()) != len(expected) or set(archive.namelist()) != expected:
            raise ValueError("ZIP manifest differs from curated skill files")
        for entry in archive.infolist():
            if entry.comment or archive.read(entry) != (ROOT / entry.filename).read_bytes():
                raise ValueError("ZIP payload or metadata differs from source")
            audit_text(entry.filename, archive.read(entry))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip", type=Path)
    args = parser.parse_args()
    audit_folder()
    if args.zip:
        audit_zip(args.zip)
    print(json.dumps({"privacy_check": "passed", "public_files": len(PUBLIC_FILES),
                      "skill_files": len(SKILL_FILES), "zip_verified": bool(args.zip)}))


if __name__ == "__main__":
    main()
