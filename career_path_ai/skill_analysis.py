import json
import os
from typing import List, Dict, Tuple

ROLES_FILE = "data/roles.json"

def load_roles() -> Dict:
    """Load roles and required skills from JSON file"""
    if not os.path.exists(ROLES_FILE):
        return {}
    
    try:
        with open(ROLES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def get_required_skills(target_role: str) -> List[str]:
    """Get required skills for a specific role"""
    roles = load_roles()
    
    # Find exact match
    if target_role in roles:
        return roles[target_role].get('required_skills', [])
    
    # Try case-insensitive match
    for role_name, role_data in roles.items():
        if role_name.lower() == target_role.lower():
            return role_data.get('required_skills', [])
    
    return []

def analyze_skill_gap(user_skills: List[str], target_role: str) -> Dict:
    """
    Analyze skill gap between user's current skills and required skills for target role
    
    Args:
        user_skills: List of user's current skills
        target_role: Target role name
    
    Returns:
        Dictionary containing:
        - required_skills: All skills needed for the role
        - missing_skills: Skills user doesn't have
        - existing_skills: Skills user already has
        - skill_gap_percentage: Percentage of skills missing
    """
    # Normalize user skills (strip whitespace, convert to lowercase)
    normalized_user_skills = [skill.strip().lower() for skill in user_skills if skill.strip()]
    
    # Get required skills for the target role
    required_skills = get_required_skills(target_role)
    normalized_required_skills = [skill.lower() for skill in required_skills]
    
    # Find existing skills (case-insensitive match)
    existing_skills = []
    for user_skill in normalized_user_skills:
        for req_skill in normalized_required_skills:
            if user_skill == req_skill or user_skill in req_skill or req_skill in user_skill:
                # Get the original case version from required skills
                original_skill = required_skills[normalized_required_skills.index(req_skill)]
                existing_skills.append(original_skill)
                break
    
    # Remove duplicates
    existing_skills = list(set(existing_skills))
    
    # Find missing skills
    missing_skills = [skill for skill in required_skills if skill not in existing_skills]
    
    # Calculate skill gap percentage
    if len(required_skills) > 0:
        skill_gap_percentage = (len(missing_skills) / len(required_skills)) * 100
    else:
        skill_gap_percentage = 0
    
    return {
        'required_skills': required_skills,
        'missing_skills': missing_skills,
        'existing_skills': existing_skills,
        'skill_gap_percentage': round(skill_gap_percentage, 2),
        'total_required_skills': len(required_skills),
        'total_existing_skills': len(existing_skills),
        'total_missing_skills': len(missing_skills)
    }

def get_all_available_roles() -> List[str]:
    """Get list of all available roles"""
    roles = load_roles()
    return list(roles.keys())

def skill_priority_analysis(missing_skills: List[str]) -> Dict:
    """
    Prioritize missing skills based on importance and difficulty
    
    Args:
        missing_skills: List of missing skills
    
    Returns:
        Dictionary with prioritized skills
    """
    # Define skill priorities (lower number = higher priority)
    skill_priorities = {
        'Python': 1,
        'JavaScript': 1,
        'HTML': 1,
        'CSS': 1,
        'SQL': 2,
        'Git': 2,
        'Statistics': 2,
        'Machine Learning': 3,
        'Deep Learning': 4,
        'TensorFlow': 4,
        'PyTorch': 4,
        'React': 3,
        'Node.js': 3,
        'Docker': 3,
        'AWS': 4,
        'Kubernetes': 5
    }
    
    prioritized_skills = []
    for skill in missing_skills:
        priority = skill_priorities.get(skill, 3)  # Default priority is 3
        prioritized_skills.append({
            'skill': skill,
            'priority': priority,
            'category': get_skill_category(skill)
        })
    
    # Sort by priority
    prioritized_skills.sort(key=lambda x: x['priority'])
    
    return {
        'prioritized_skills': prioritized_skills,
        'high_priority': [s for s in prioritized_skills if s['priority'] <= 2],
        'medium_priority': [s for s in prioritized_skills if s['priority'] == 3],
        'low_priority': [s for s in prioritized_skills if s['priority'] >= 4]
    }

def get_skill_category(skill: str) -> str:
    """Get category for a skill"""
    programming_languages = ['Python', 'JavaScript', 'HTML', 'CSS', 'SQL']
    frameworks = ['React', 'Node.js', 'TensorFlow', 'PyTorch']
    tools = ['Git', 'Docker', 'AWS', 'Kubernetes', 'Tableau', 'Excel']
    concepts = ['Machine Learning', 'Deep Learning', 'Statistics', 'Data Visualization']
    
    skill_lower = skill.lower()
    
    if any(lang.lower() in skill_lower for lang in programming_languages):
        return 'Programming Language'
    elif any(fw.lower() in skill_lower for fw in frameworks):
        return 'Framework'
    elif any(tool.lower() in skill_lower for tool in tools):
        return 'Tool'
    elif any(concept.lower() in skill_lower for concept in concepts):
        return 'Concept'
    else:
        return 'General'

def generate_skill_summary(analysis_result: Dict) -> str:
    """Generate a human-readable summary of skill analysis"""
    total_required = analysis_result['total_required_skills']
    total_existing = analysis_result['total_existing_skills']
    total_missing = analysis_result['total_missing_skills']
    gap_percentage = analysis_result['skill_gap_percentage']
    
    summary = f"You have {total_existing} out of {total_required} required skills "
    summary += f"({100 - gap_percentage}% match). "
    
    if total_missing > 0:
        summary += f"You need to learn {total_missing} skills: "
        summary += ", ".join(analysis_result['missing_skills'][:5])
        if total_missing > 5:
            summary += f" and {total_missing - 5} more."
    
    return summary
