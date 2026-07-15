"""Fix remaining audit gaps in production content (no schema/ID changes)."""
import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "albertaprep.db"
BACKUP = Path(__file__).resolve().parents[1] / "backups" / f"albertaprep_pre_audit_fix_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.db"
shutil.copy2(DB, BACKUP)

conn = sqlite3.connect(DB)
conn.execute(
    """
    UPDATE questions SET
      explanation = ?,
      common_mistake = ?
    WHERE id = 414
    """,
    (
        "Ovulation occurs on day 14. The luteal phase lasts 14 days, so menstruation "
        "begins on day 14 + 14 = 28 when pregnancy does not occur. Record as two digits: 28.",
        "Students answer 14 (luteal phase length only) instead of adding ovulation day and luteal phase.",
    ),
)
conn.execute(
    """
    UPDATE questions SET
      answer = ?
    WHERE id = 268
    """,
    (
        "x = 4. Verify: sqrt(4 + 5) = 3 and x - 1 = 3, so the root is valid.",
    ),
)
conn.commit()
conn.close()
print(f"Backup: {BACKUP}")
print("Updated Q414 explanation, Q268 model answer")
