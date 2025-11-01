import requests

leads = [
    "Electric SUV under 40k ASAP",
    "Cheap sedan, budget 20k, no rush",
    "Luxury EV, 100k+ budget"
]

for msg in leads:
    resp = requests.post("http://localhost:5000/submit_lead", json={"message": msg})
    print(resp.json())