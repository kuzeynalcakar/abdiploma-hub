import json
from pathlib import Path

QDIR = Path(__file__).resolve().parents[2] / "questions.json"
p1 = QDIR / "science10_questions_final.json"
p2 = QDIR / "course_questions_final.json"

RW = {
    r"A 4.0 kg object moves at 3.0 m/s. Calculate its kinetic energy in joules using $E_k = \frac{1}{2}mv^2$. Record as an integer.":
        r"A 4.0 kg cart rolls at 3.0 m/s. Determine its kinetic energy in joules with $E_k = \frac{1}{2}mv^2$. Record as an integer.",
    r"A 2.0 kg object is lifted 5.0 m vertically above a reference level. Using $g = 9.8\ \text{m/s}^2$, calculate gravitational potential energy in joules. Record to one decimal place.":
        r"A student raises a 2.0 kg textbook 5.0 m onto a high shelf. Using $g = 9.8\ \text{m/s}^2$, find the gravitational potential energy gained in joules. Record to one decimal place.",
    r"A device receives 750 J of energy and produces 300 J of useful output. What is the efficiency as a percentage? Record to one decimal place.":
        r"An appliance draws 750 J of energy and delivers 300 J of useful output. Calculate its efficiency as a percentage. Record to one decimal place.",
    r"A microscope specimen is 0.05 mm wide and its image measures 2.0 mm wide. What is the magnification (image size ÷ actual size)?":
        r"Under a microscope, a 0.05 mm wide specimen forms an image 2.0 mm across. Determine the magnification (image size ÷ actual size).",
    "How much thermal energy in joules is required to raise the temperature of 1.0 kg of water by 5\u00b0C? Use $c = 4200$ J/(kg\u00b7\u00b0C) and $Q = mc\\Delta T$.":
        "Determine the thermal energy in joules needed to warm 1.0 kg of water by 5\u00b0C. Use $c = 4200$ J/(kg\u00b7\u00b0C) and $Q = mc\\Delta T$.",
}

d = json.loads(p1.read_text(encoding="utf-8"))
n = 0
for q in d:
    if q["question_text"] in RW:
        q["question_text"] = RW[q["question_text"]]
        n += 1
p1.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
p2.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
print("reworded", n)
