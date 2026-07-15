"""Re-run PHYS30 post-import verification without re-importing."""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.import_phys30_production import (
    PROD_DB,
    REPORT_PATH,
    build_report,
    snapshot_existing,
    verify_api_endpoints,
    verify_existing_ids_preserved,
    verify_orphans,
    verify_phys30_counts,
)

BACKUP = Path(__file__).resolve().parents[1] / "backups" / "albertaprep_pre_phys30_import_20260713_232304.db"


def main() -> int:
    conn = sqlite3.connect(PROD_DB)
    after = snapshot_existing(conn)
    issues = []
    issues.extend(verify_orphans(conn))
    issues.extend(verify_phys30_counts(conn))
    api_issues, api_details = verify_api_endpoints(conn)
    issues.extend(api_issues)
    conn.close()

    before = dict(after)
    before["phys30_count"] = 0
    report = build_report(
        backup_path=BACKUP,
        before=before,
        after=after,
        issues=issues,
        api_details=api_details,
    )
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Status: {report['status']}")
    if issues:
        for i in issues:
            print(f"FAIL: {i}")
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
