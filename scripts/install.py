"""Install this curated skill globally without replacing a different version."""
import argparse
import hashlib
from pathlib import Path
import shutil

from audit_release import ROOT, SKILL_FILES, audit_folder


def hashes(folder):
    return {p.relative_to(folder).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in folder.rglob("*") if p.is_file() and "__pycache__" not in p.parts}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dest", type=Path,
                        default=Path.home() / ".agents/skills/cq-jizhang",
                        help="Final global cq-jizhang directory recognized by your agent")
    args = parser.parse_args()
    audit_folder()
    source = ROOT / "cq-jizhang"
    target = args.dest.expanduser().absolute()
    if target.is_symlink():
        raise SystemExit("Destination is a symlink; inspect it before installing")
    expected = {name: hashlib.sha256((source / name).read_bytes()).hexdigest() for name in SKILL_FILES}
    if target.exists():
        if target.is_dir() and hashes(target) == expected:
            print(f"Already installed and verified: {len(expected)} skill files")
            return
        raise SystemExit("A different installation exists. Preserve it and review changes before updating.")
    target.mkdir(parents=True, exist_ok=False)
    for name in SKILL_FILES:
        output = target / name
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / name, output)
    if hashes(target) != expected:
        raise SystemExit("Installed files failed verification; setup has not started")
    print(f"Installed and verified {len(expected)} skill files. Refresh agent skills, then invoke cq-jizhang.")


if __name__ == "__main__":
    main()
