"""Quick verify results/weakness/daily-practice API responses."""
import json, random, urllib.request

BASE = "http://127.0.0.1:8000/api/v1"
email = f"bio.verify.{random.randint(100000,999999)}@example.com"
req = urllib.request.Request(
    BASE + "/auth/register",
    data=json.dumps({"name": "V", "email": email, "password": "testpass123"}).encode(),
    headers={"Content-Type": "application/json"},
    method="POST",
)
token = json.loads(urllib.request.urlopen(req).read())["token"]
h = {"Authorization": f"Bearer {token}"}

courses = json.loads(urllib.request.urlopen(urllib.request.Request(BASE + "/courses", headers=h)).read())
bio = next(c for c in courses["courses"] if c["code"] == "BIO30")
cid = bio["id"]

quiz = json.loads(
    urllib.request.urlopen(
        urllib.request.Request(BASE + f"/quiz/questions?course_id={cid}&count=10", headers=h)
    ).read()
)
aid = quiz["quiz_attempt_id"]
types = {}
for q in quiz["questions"]:
    types[q["question_type"]] = types.get(q["question_type"], 0) + 1
    body = {"quiz_attempt_id": aid, "question_id": q["id"]}
    if q["question_type"] == "multiple_choice":
        body["answer_choice_id"] = q["choices"][0]["id"]
    elif q["question_type"] == "numerical_response":
        body["response_text"] = "0"
    else:
        body["response_text"] = "Test written response."
    urllib.request.urlopen(
        urllib.request.Request(
            BASE + "/quiz/answer",
            data=json.dumps(body).encode(),
            headers={**h, "Content-Type": "application/json"},
            method="POST",
        )
    )

results = json.loads(
    urllib.request.urlopen(urllib.request.Request(BASE + f"/quiz/attempt/{aid}/results", headers=h)).read()
)
wm = json.loads(
    urllib.request.urlopen(urllib.request.Request(BASE + f"/weakness-map?course_id={cid}", headers=h)).read()
)
dp = json.loads(
    urllib.request.urlopen(urllib.request.Request(BASE + f"/daily-practice?course_id={cid}", headers=h)).read()
)

print("Quiz types:", types)
print("Results:", json.dumps(results, indent=2))
print("Weakness map keys:", list(wm.keys()))
print("Daily practice keys:", list(dp.keys()), "target_areas:", dp.get("target_areas"))
