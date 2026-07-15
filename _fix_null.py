from pathlib import Path

p = Path(r"C:\AlbertaPrep\frontend\src\pages\Quiz.jsx")
t = p.read_text(encoding="utf-8")
old = "    } else if (availableCount < questionCount) {"
new = "    } else if (availableCount != null && availableCount < questionCount) {"
count = t.count(old)
print("count", count)
if count >= 1:
    t = t.replace(old, new, 1)
    p.write_text(t, encoding="utf-8")
    print("fixed")
