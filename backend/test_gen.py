import sys
sys.path.insert(0, '.')
from app.auto_collector import generate_large_dataset

jobs = generate_large_dataset(9000)
print(f"Generated {len(jobs)} jobs")
titles = set(j["title"] for j in jobs)
print(f"Unique titles: {len(titles)}")
interns = sum(1 for j in jobs if 'intern' in j['job_type'].lower() or 'intern' in j['title'].lower())
freshers = sum(1 for j in jobs if 'fresher' in j['title'].lower() or 'trainee' in j['title'].lower())
print(f"Internships: {interns} ({interns*100//len(jobs)}%)")
print(f"Fresher roles: {freshers} ({freshers*100//len(jobs)}%)")
print(f"Total entry-level: {(interns+freshers)*100//len(jobs)}%")
