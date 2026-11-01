"""Build a deterministic skill-only ZIP and SHA-256 checksum."""
import argparse
import hashlib
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

from audit_release import ROOT, SKILL_FILES, audit_folder, audit_zip


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", default="3.7.1")
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    if not args.version or any(c not in "0123456789.-" for c in args.version):
        raise SystemExit("Use a numeric release version")
    audit_folder()
    args.output.mkdir(parents=True, exist_ok=True)
    path = args.output / f"cq-jizhang-v{args.version}.zip"
    with ZipFile(path, "w", ZIP_DEFLATED) as archive:
        for name in sorted(SKILL_FILES):
            info = ZipInfo("cq-jizhang/" + name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = ZIP_DEFLATED
            archive.writestr(info, (ROOT / "cq-jizhang" / name).read_bytes())
    audit_zip(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    (args.output / "SHA256SUMS.txt").write_text(f"{digest}  {path.name}\n", encoding="utf-8", newline="\n")
    print(f"Packaged and verified {len(SKILL_FILES)} files: {path.name}")
    print(f"SHA-256: {digest}")


if __name__ == "__main__":
    main()
