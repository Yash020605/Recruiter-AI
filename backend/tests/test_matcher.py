from backend.ml.candidate_matcher import calculate_match_score

job_description = """
We are looking for a Python Developer with experience in FastAPI,
Machine Learning, SQL, REST APIs, and Git.
"""

resume = """
Experienced Python developer with 2 years of experience.
Worked on FastAPI, SQL, Machine Learning, TensorFlow,
GitHub, and REST API development.
"""

score = calculate_match_score(job_description, resume)

print(f"Match Score: {score}%")
