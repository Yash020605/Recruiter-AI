from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load model once
model = SentenceTransformer("all-MiniLM-L6-v2")


def calculate_match_score(job_description: str, resume_text: str):
    """
    Returns semantic similarity score (0-100)
    """

    jd_embedding = model.encode(job_description, convert_to_numpy=True)
    resume_embedding = model.encode(resume_text, convert_to_numpy=True)

    similarity = cosine_similarity(
        [jd_embedding],
        [resume_embedding]
    )[0][0]

    return round(similarity * 100, 2)


def get_top_matching_skills(job_description: str, candidate_skills: list):
    """
    Finds which candidate skills are semantically closest
    to the job description.
    """

    if not candidate_skills:
        return []

    jd_embedding = model.encode(job_description, convert_to_numpy=True)
    skill_embeddings = model.encode(candidate_skills, convert_to_numpy=True)

    similarities = cosine_similarity(
        [jd_embedding],
        skill_embeddings
    )[0]

    ranked = sorted(
        zip(candidate_skills, similarities),
        key=lambda x: x[1],
        reverse=True
    )

    return ranked
