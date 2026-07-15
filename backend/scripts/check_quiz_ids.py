import json
import random
import urllib.request

BASE = "http://127.0.0.1:8000/api/v1"
email = f"x.{random.randint(1, 999999)}@e.com"
token = json.loads(
    urllib.request.urlopen(
        urllib.request.Request(
            BASE + "/auth/register",
            data=json.dumps({"name": "x", "email": email, "password": "testpass123"}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
    ).read()
)["access_token"]
h = {"Authorization": f"Bearer {token}"}
bio = next(
    c
    for c in json.loads(
        urllib.request.urlopen(urllib.request.Request(BASE + "/courses", headers=h)).read()
    )["courses"]
    if c["code"] == "BIO30"
)
for topic_id in [42, 43, 44, 45, 46]:
    quiz = json.loads(
        urllib.request.urlopen(
            urllib.request.Request(
                BASE + f"/quiz/questions?course_id={bio['id']}&topic_id={topic_id}&count=8",
                headers=h,
            )
        ).read()
    )
    ids = [q["id"] for q in quiz["questions"]]
    print(topic_id, ids, "max", max(ids), "min", min(ids))
