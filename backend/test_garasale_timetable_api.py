import requests
from app.core.security import create_access_token

token = create_access_token(
    subject=1,
    claims={
        'roles': ['ADMIN'],
        'institution_code': 'SOM-SCH-0002',
        'database_name': 'somroyal_garasale_primary_school'
    }
)

headers = {
    'Authorization': f'Bearer {token}',
    'X-Institution-Code': 'SOM-SCH-0002'
}

base = 'http://127.0.0.1:8000'

endpoints = [
    ('Dashboard', '/api/v1/admin/dashboard'),
    ('Timetable Summary', '/api/v1/timetable/summary?academic_year=2026/2027'),
    ('Timetable Settings', '/api/v1/timetable/settings?academic_year=2026/2027'),
    ('Class Overview (Class 1)', '/api/v1/timetable/class-overview/1?academic_year=2026/2027'),
    ('Teacher Availability Matrix', '/api/v1/timetable/teacher-availability/matrix?academic_year=2026/2027'),
    ('Classes', '/api/v1/classes?academic_year=2026/2027'),
    ('Teachers', '/api/v1/teachers'),
    ('Subjects', '/api/v1/subjects'),
]

for name, path in endpoints:
    resp = requests.get(f"{base}{path}", headers=headers)
    print(f"[{name}] {path} -> HTTP {resp.status_code}")
    if resp.status_code != 200:
        print("  Error:", resp.text)
    else:
        data = resp.json()
        print("  Success! Items/Keys:", list(data.keys()) if isinstance(data, dict) else len(data))
