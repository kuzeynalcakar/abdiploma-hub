import json
import re
from collections import Counter, defaultdict

with open(r'C:\AlbertaPrep\questions.json\biology30_questions_final.json', encoding='utf-8') as f:
    data = json.load(f)

print('Count:', len(data))
print('Types:', dict(Counter(q.get('question_type') for q in data)))
print('Difficulties:', dict(Counter(q.get('difficulty') for q in data)))
print('Units:', dict(Counter(q.get('unit') for q in data)))

# Export compact index for review
for i, q in enumerate(data):
    qt = q.get('question_type', '')
    ans = q.get('answer', '')
    txt = q.get('question_text', '').replace('\n', ' ')[:120]
    print(f"{i}|{qt}|{q.get('difficulty')}|{q.get('outcome_code')}|{q.get('unit','')[:30]}|{txt}|{str(ans)[:60]}")
