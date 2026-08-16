import re
import sys

def resolve_file(path, merge_logic):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the conflict block
    pattern = re.compile(r'<<<<<<< HEAD\n(.*?)\n=======\n(.*?)\n>>>>>>> old_origin/feature/interview-scheduling\n', re.DOTALL)
    
    def repl(m):
        head = m.group(1)
        feat = m.group(2)
        return merge_logic(head, feat)
        
    new_content = pattern.sub(repl, content)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)

# 1. routes.py
def logic_routes(head, feat):
    return """from backend.database.models import UserRole, Candidate, Comment, JobMatch, CandidateJourney, Interview
from backend.schemas.candidate import CandidateResponse, CommentCreate, CommentResponse, JourneyCreate, JourneyUpdate, JourneyResponse
"""
resolve_file('backend/api/routes.py', logic_routes)

# 2. models.py
def logic_models(head, feat):
    return head + "\n" + feat + "\n"
resolve_file('backend/database/models.py', logic_models)

# 3. HRDashboard.tsx
def logic_dashboard(head, feat):
    return head + "\n" + feat + "\n"
resolve_file('react-frontend/src/pages/HRDashboard.tsx', logic_dashboard)

print("Conflicts resolved.")
