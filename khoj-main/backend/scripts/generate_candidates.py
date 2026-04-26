import json
import random
import os

# Get directory of current script and go up one level to find data/
current_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(current_dir, "..", "data", "candidates.json")

first_names = ["Priya", "Rahul", "Ananya", "Siddharth", "Ishita", "Arjun", "Kavya", "Varun", "Sneha", "Aditya", 
               "Zoya", "Rohan", "Meera", "Vikram", "Tara", "Kabir", "Riya", "Aman", "Sanya", "Neil"]
last_names = ["Sharma", "Verma", "Gupta", "Malhotra", "Reddy", "Iyer", "Khan", "Kapoor", "Singh", "Joshi", 
              "Mehta", "Bose", "Patel", "Nair", "Das", "Choudhury", "Pillai", "Rao", "Mishra", "Dubey"]

skills_pool = [
    "React", "Node.js", "Python", "FastAPI", "PostgreSQL", "MongoDB", "TypeScript", 
    "AWS", "Docker", "Kubernetes", "Tailwind CSS", "Next.js", "Java", "Spring Boot", 
    "Machine Learning", "Data Analysis", "GraphQL", "Redis", "Solidity", "Rust"
]

roles = ["Frontend Developer", "Backend Developer", "Full Stack Engineer", "DevOps Engineer", "Data Scientist", "Blockchain Developer"]
locations = ["Bangalore", "Hyderabad", "Pune", "Mumbai", "Delhi", "Remote"]

candidates = []

for i in range(1, 51):
    name = f"{random.choice(first_names)} {random.choice(last_names)}"
    
    # For the first 10 candidates, force them to be good matches for web roles
    if i <= 10:
        candidate_skills = ["React", "Node.js", "TypeScript"] + random.sample(["Tailwind CSS", "PostgreSQL", "AWS", "Docker", "Next.js"], 2)
        role = random.choice(["Full Stack Engineer", "Frontend Developer", "Backend Developer"])
        experience = random.randint(4, 8)
    else:
        candidate_skills = random.sample(skills_pool, random.randint(3, 7))
        role = random.choice(roles)
        experience = random.randint(1, 12)

    location = random.choice(locations)
    ctc = f"{random.randint(10, 50)} LPA"
    
    candidates.append({
        "id": i,
        "name": name,
        "skills": candidate_skills,
        "experience_years": experience,
        "current_role": role,
        "location": location,
        "open_to_work": random.choice([True, True, False]), # More likely to be open
        "expected_ctc": ctc,
        "email": f"{name.lower().replace(' ', '.')}@example.com",
        "bio": f"Experienced {role} with a focus on {candidate_skills[0]} and {candidate_skills[1]}."
    })

with open(output_path, "w") as f:
    json.dump(candidates, f, indent=2)

print(f"Generated 50 candidates in {output_path}")
