"""Measure cold and warm registry-cache scans with the checkout's CLI."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import perf_counter


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "testdata" / "live"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path,
                        default=[FIXTURES / "package-lock.json", FIXTURES / "uv.lock"])
    args = parser.parse_args()
    paths = [str(path.resolve()) for path in args.paths]

    with TemporaryDirectory(prefix="unripe-bench-") as directory:
        scratch = Path(directory)
        config = scratch / "unripe.toml"
        config.touch()
        env = dict(os.environ, UNRIPE_CACHE=str(scratch / "cache"),
                   PYTHONPATH=str(ROOT / "src"))
        as_of = datetime.now(timezone.utc).isoformat()
        command = [sys.executable, "-m", "unripe", "check", "--config", str(config),
                   "--format", "json", "--verbose", "--no-suggest", "--as-of", as_of, *paths]
        cold = None
        for phase in ("cold", "warm"):
            started = perf_counter()
            run = subprocess.run(command, cwd=scratch, env=env, capture_output=True, text=True,
                                 encoding="utf-8", errors="replace")
            elapsed = perf_counter() - started
            if run.returncode not in (0, 1):
                raise SystemExit(run.stderr.strip() or f"unripe exited with {run.returncode}")
            report = json.loads(run.stdout)
            requests = re.search(r" and (\d+) requests$", run.stderr, re.MULTILINE)
            if requests is None or report["summary"]["unknown"] or not report["findings"]:
                raise SystemExit(f"{phase} scan did not resolve all dependencies:\n{run.stderr.strip()}")
            findings = report["findings"]
            snapshot = [(row["ecosystem"], row["name"], row["version"], row["state"],
                         row["published"]) for row in findings]
            if cold is None:
                cold = snapshot
            elif snapshot != cold:
                raise SystemExit("warm scan returned different dependency results")
            print(f"{phase}: {elapsed:.3f}s, {requests[1]} requests, {len(findings)} findings")


if __name__ == "__main__":
    main()
