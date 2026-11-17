"""Check the public document set without contacting a device or the network."""

from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
# N1 ← D2: raw research and device artifacts have no place in this public set.
PUBLIC_FILES = {
    "README.md", "AGENTS.md", "SPEC.md", ".gitignore",
    "docs/guide.md", "docs/components.md", "docs/devices.md", "docs/sources.md",
    "tools/check_publication.py", ".github/workflows/publication.yml",
}
actual = {
    p.relative_to(ROOT).as_posix()
    for p in ROOT.rglob("*")
    if ".git" not in p.relative_to(ROOT).parts and (p.is_file() or p.is_symlink())
}
errors = []
for name in sorted(actual - PUBLIC_FILES):
    errors.append(f"{name}: file outside public set")
for name in sorted(PUBLIC_FILES - actual):
    errors.append(f"{name}: required public file missing")

# N1 ← D2: heuristic signals; a human still reviews the staged content.
signals = {
    "local home path": r"/(?:home|Users)/[\w.-]+/|[A-Z]:\\Users\\",
    "phone-like identifier": r"(?<![\w])1[3-9]\d{9}(?![\w])",
    "MAC-like identifier": r"\b(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}\b",
    "credential-like value": r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b",
    "literal ADB target": r"\badb\s+-s\s+(?!SERIAL\b|SERIAL_NUMBER\b)[A-Za-z0-9]{8,}\b",
    # N2 ← D1: the documents stand on their own rather than referring to a local run.
    "old or private artifact dependency": r"web-original\.md|deep-research-report\.md|device_ops\.py|device-changes\.jsonl|final-device-state\.json|private-snapshot-",
    "unresolved export citation": r"|\bturn\d+(?:search|view|file)\d+\b",
}
for name in sorted(actual & PUBLIC_FILES):
    path = ROOT / name
    if path.is_symlink():
        errors.append(f"{name}: symlinks are not public artifacts")
        continue
    content = path.read_text(encoding="utf-8")
    for rule, pattern in signals.items():
        if rule in {"old or private artifact dependency", "unresolved export citation"} and not name.endswith(".md"):
            continue
        for match in re.finditer(pattern, content):
            line = content.count("\n", 0, match.start()) + 1
            errors.append(f"{name}:{line}: {rule}")
    if not name.endswith(".md"):
        continue
    if len(re.findall(r"(?m)^```", content)) % 2:
        errors.append(f"{name}: unbalanced fenced code blocks")
    definitions = dict(re.findall(r"(?m)^\[([^]\n]+)\]:\s*(\S+)", content))
    for key in re.findall(r"\]\[([^]\n]+)\]", content):
        if key not in definitions:
            errors.append(f"{name}: undefined link reference [{key}]")
    # N2 ← D1: local file links must stay inside and resolve within the public set.
    targets = re.findall(r"\[[^]\n]+\]\(([^)\n]+)\)", content)
    for target in targets + list(definitions.values()):
        url = urlsplit(target.strip("<>"))
        if url.scheme or url.netloc or not url.path:
            continue
        resolved = (path.parent / unquote(url.path)).resolve()
        if not resolved.is_relative_to(ROOT):
            errors.append(f"{name}: link escapes public repository")
        elif resolved.relative_to(ROOT).as_posix() not in PUBLIC_FILES or not resolved.is_file():
            errors.append(f"{name}: broken local link: {url.path}")

if errors:
    raise SystemExit("\n".join(errors))
print(f"Publication check passed: {len(PUBLIC_FILES)} public files; local links and heuristic privacy checks.")
