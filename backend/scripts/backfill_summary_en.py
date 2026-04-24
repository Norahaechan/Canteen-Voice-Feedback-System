from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.db.init_db import backfill_analysis_summary_en
from app.db.session import SessionLocal


def main() -> None:
    with SessionLocal() as db:
        backfill_analysis_summary_en(db)
        db.commit()
    print("summary_en backfill completed.")


if __name__ == "__main__":
    main()
