from database import db
from collections import Counter

def check_counts():
    leads = db.fetch_leads()
    counts = Counter([l.get('status') for l in leads])
    print("Pipeline Counts:")
    for status, count in counts.items():
        print(f"  {status}: {count}")

if __name__ == "__main__":
    check_counts()
