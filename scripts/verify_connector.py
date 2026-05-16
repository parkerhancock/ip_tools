#!/usr/bin/env python3
"""verify_connector — gate for new and modified connectors.

Runs the five quality bars a connector must clear before merge:

  1. ruff check (lint)
  2. ruff format --check
  3. ty check (zero diagnostics)
  4. pytest --cov  (≥80% line coverage on each affected package)
  5. doc updates  (CHANGELOG [Unreleased] entry; optional --jurisdiction
     enforces README + CLAUDE.md mention of the display name)

Usage:

    uv run python scripts/verify_connector.py \\
        --jurisdiction "IP Australia" \\
        ip_australia_patents ip_australia_trademarks \\
        ip_australia_designs ip_australia_bulk

Positional arguments are Python package names under
``src/patent_client_agents/``. The script resolves each to its
library package, its test package (``tests/<name>/``), and any
sibling MCP-tool module at ``src/patent_client_agents/mcp/tools/<name>.py``.

Exit code is 0 on success, non-zero on any failure. Use the output
verbatim in the connector PR's evidence section.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_ROOT = REPO_ROOT / "src" / "patent_client_agents"
MCP_TOOLS = SRC_ROOT / "mcp" / "tools"
TESTS_ROOT = REPO_ROOT / "tests"

COVERAGE_THRESHOLD = 80.0


@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: list[str] = field(default_factory=list)


@dataclass
class ConnectorPaths:
    package: str
    src_path: Path
    test_path: Path | None
    mcp_path: Path | None

    @classmethod
    def resolve(cls, package: str) -> ConnectorPaths:
        src = SRC_ROOT / package
        if not src.is_dir():
            raise SystemExit(
                f"package not found: {src.relative_to(REPO_ROOT)} (does it exist on this branch?)"
            )
        test = TESTS_ROOT / package
        mcp = MCP_TOOLS / f"{package}.py"
        return cls(
            package=package,
            src_path=src,
            test_path=test if test.is_dir() else None,
            mcp_path=mcp if mcp.is_file() else None,
        )

    def all_lint_paths(self) -> list[Path]:
        paths: list[Path] = [self.src_path]
        if self.test_path is not None:
            paths.append(self.test_path)
        if self.mcp_path is not None:
            paths.append(self.mcp_path)
        return paths

    def files_under_coverage(self) -> list[str]:
        """Return the file paths whose coverage counts for this package.

        Includes everything under ``src/patent_client_agents/<package>/``
        plus the sibling ``src/patent_client_agents/mcp/tools/<package>.py``
        when present.
        """
        out: list[str] = []
        for path in sorted(self.src_path.rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            out.append(str(path.relative_to(REPO_ROOT)))
        if self.mcp_path is not None:
            out.append(str(self.mcp_path.relative_to(REPO_ROOT)))
        return out


def _run(cmd: list[str]) -> tuple[int, str]:
    """Run ``cmd`` from REPO_ROOT, capturing stdout+stderr; return (rc, output)."""
    proc = subprocess.run(  # noqa: S603 — internal tool, args are constructed
        cmd,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def check_ruff_lint(paths: list[Path]) -> CheckResult:
    cmd = ["uv", "run", "ruff", "check", *[str(p) for p in paths]]
    rc, out = _run(cmd)
    if rc == 0:
        return CheckResult("ruff check", passed=True)
    return CheckResult("ruff check", passed=False, detail=out.strip().splitlines())


def check_ruff_format(paths: list[Path]) -> CheckResult:
    cmd = ["uv", "run", "ruff", "format", "--check", *[str(p) for p in paths]]
    rc, out = _run(cmd)
    if rc == 0:
        return CheckResult("ruff format --check", passed=True)
    return CheckResult("ruff format --check", passed=False, detail=out.strip().splitlines())


def check_ty(paths: list[Path]) -> CheckResult:
    cmd = ["uv", "run", "ty", "check", *[str(p) for p in paths]]
    rc, out = _run(cmd)
    if rc == 0:
        return CheckResult("ty check", passed=True)
    diag_lines = [line for line in out.splitlines() if line.strip().startswith("error[")]
    summary = diag_lines or out.strip().splitlines()[-15:]
    return CheckResult("ty check", passed=False, detail=summary)


_COV_LINE_RE = re.compile(r"^\s*(?P<path>src/[^\s]+\.py)\s+\d+\s+\d+\s+(?P<pct>\d+(?:\.\d+)?)%")
_COV_TOTAL_RE = re.compile(r"^\s*TOTAL\s+\d+\s+\d+\s+(?P<pct>\d+(?:\.\d+)?)%")


def check_coverage(connectors: list[ConnectorPaths]) -> CheckResult:
    test_paths = [str(c.test_path) for c in connectors if c.test_path is not None]
    if not test_paths:
        return CheckResult(
            "pytest --cov",
            passed=False,
            detail=["no test directories found for any package — write tests first"],
        )

    relevant_files: set[str] = set()
    for c in connectors:
        relevant_files.update(c.files_under_coverage())

    # Path-based `--cov` against the source root avoids importing dotted
    # `mcp.tools.*` modules through the coverage tracer, which trips a
    # beartype/coverage import-hook circular import. The broad source
    # captures everything; we filter to ``relevant_files`` for the report.
    cmd = [
        "uv",
        "run",
        "pytest",
        "-q",
        "-p",
        "no:beartype",
        "--cov=src/patent_client_agents",
        "--cov-report=term",
        *test_paths,
    ]
    rc, out = _run(cmd)

    if "ImportError" in out and "passed" not in out:
        return CheckResult(
            "pytest --cov",
            passed=False,
            detail=["pytest failed to start:", *out.strip().splitlines()[-15:]],
        )

    per_file: dict[str, float] = {}
    for line in out.splitlines():
        m_file = _COV_LINE_RE.match(line)
        if m_file:
            per_file[m_file.group("path")] = float(m_file.group("pct"))

    measured: dict[str, float] = {p: pct for p, pct in per_file.items() if p in relevant_files}

    if not measured:
        return CheckResult(
            "pytest --cov",
            passed=False,
            detail=[
                "could not match any relevant file in coverage output",
                f"expected files: {sorted(relevant_files)[:5]} ...",
            ],
        )

    total_statements = 0
    total_missed = 0
    for path, pct in measured.items():
        for line in out.splitlines():
            if line.startswith(path):
                parts = line.split()
                try:
                    stmts = int(parts[1])
                    missed = int(parts[2])
                    total_statements += stmts
                    total_missed += missed
                except (IndexError, ValueError):
                    pass
                break
        del pct  # ruff B007 silencer; pct already captured in `measured`

    covered_pct = (
        100.0 * (total_statements - total_missed) / total_statements if total_statements else 0.0
    )
    failing_files = sorted(
        ((p, pct) for p, pct in measured.items() if pct < COVERAGE_THRESHOLD),
        key=lambda x: x[1],
    )
    tests_passed = "failed" not in out.lower() or "0 failed" in out

    passed = tests_passed and rc == 0 and covered_pct >= COVERAGE_THRESHOLD and not failing_files

    detail: list[str] = [
        f"aggregate coverage on connector files: {covered_pct:.1f}% "
        f"(target ≥ {COVERAGE_THRESHOLD:.0f}%)",
        f"files measured: {len(measured)}",
    ]
    if failing_files:
        detail.append("per-file < threshold:")
        for path, pct in failing_files:
            detail.append(f"  {path}: {pct:.0f}%")
    if rc != 0 and tests_passed:
        detail.append(f"pytest exit code: {rc}")
    if not tests_passed:
        detail.append("test output (tail):")
        detail.extend(out.strip().splitlines()[-15:])

    return CheckResult("pytest --cov", passed=passed, detail=detail)


_UNRELEASED_HEADER_RE = re.compile(r"^##\s+\[Unreleased\]", re.MULTILINE)


def check_docs(connectors: list[ConnectorPaths], jurisdiction: str | None) -> CheckResult:
    changelog = REPO_ROOT / "CHANGELOG.md"
    readme = REPO_ROOT / "README.md"
    claude_md = REPO_ROOT / "CLAUDE.md"

    package_names = [c.package for c in connectors]

    detail: list[str] = []
    all_ok = True

    changelog_text = changelog.read_text() if changelog.is_file() else ""
    unreleased_match = _UNRELEASED_HEADER_RE.search(changelog_text)
    if not unreleased_match:
        detail.append("CHANGELOG.md: missing `## [Unreleased]` header")
        all_ok = False
    else:
        unreleased_section = changelog_text[unreleased_match.start() :].split("\n## ", 1)[0]
        mentioned = [p for p in package_names if p in unreleased_section]
        if not mentioned:
            detail.append(
                f"CHANGELOG.md [Unreleased]: no mention of any package ({', '.join(package_names)})"
            )
            all_ok = False
        else:
            detail.append(f"CHANGELOG.md: ✓ mentions {', '.join(mentioned)}")

    if jurisdiction:
        readme_text = readme.read_text() if readme.is_file() else ""
        if jurisdiction not in readme_text:
            detail.append(f"README.md: missing mention of `{jurisdiction}`")
            all_ok = False
        else:
            detail.append(f"README.md: ✓ mentions `{jurisdiction}`")

        claude_text = claude_md.read_text() if claude_md.is_file() else ""
        has_jur = jurisdiction in claude_text
        has_pkg = any(p in claude_text for p in package_names)
        if has_jur or has_pkg:
            label = jurisdiction if has_jur else "package name"
            detail.append(f"CLAUDE.md: ✓ mentions `{label}`")
        else:
            detail.append(
                f"CLAUDE.md: missing mention of `{jurisdiction}` or any package "
                f"({', '.join(package_names)})"
            )
            all_ok = False
    else:
        detail.append("(README + CLAUDE.md checks skipped — pass --jurisdiction to enforce)")

    return CheckResult("doc updates", passed=all_ok, detail=detail)


def format_report(connectors: list[ConnectorPaths], checks: list[CheckResult]) -> str:
    pkgs = ", ".join(c.package for c in connectors)
    lines = [
        "verify_connector — patent-client-agents",
        f"  packages: {pkgs}",
        "",
    ]
    for idx, check in enumerate(checks, start=1):
        status = "PASS" if check.passed else "FAIL"
        lines.append(f"[{idx}/{len(checks)}] {check.name:<28s} ........... {status}")
        for line in check.detail:
            lines.append(f"       {line}")
    lines.append("")
    if all(c.passed for c in checks):
        lines.append("VERDICT: PASS — all five bars cleared.")
    else:
        failing = [c.name for c in checks if not c.passed]
        lines.append(f"VERDICT: FAIL — fix: {', '.join(failing)}.")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "packages",
        nargs="+",
        help="Package names under src/patent_client_agents/ (e.g. ip_australia_patents).",
    )
    parser.add_argument(
        "--jurisdiction",
        help=(
            "Display name (e.g. 'IP Australia') for README + CLAUDE.md mention "
            "check. When omitted those doc checks are skipped with a note."
        ),
    )
    args = parser.parse_args()

    connectors = [ConnectorPaths.resolve(p) for p in args.packages]

    all_paths: list[Path] = []
    for c in connectors:
        all_paths.extend(c.all_lint_paths())

    checks = [
        check_ruff_lint(all_paths),
        check_ruff_format(all_paths),
        check_ty(all_paths),
        check_coverage(connectors),
        check_docs(connectors, args.jurisdiction),
    ]

    print(format_report(connectors, checks))
    return 0 if all(c.passed for c in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
