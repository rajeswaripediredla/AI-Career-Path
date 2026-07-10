import json
import os
from typing import List, Dict, Tuple
from fuzzywuzzy import fuzz

COURSES_FILE = "data/courses.json"

def load_courses() -> List[Dict]:
    """Load courses from JSON file"""
    if not os.path.exists(COURSES_FILE):
        return []
    
    try:
        with open(COURSES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('courses', [])
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def match_courses_to_skills(missing_skills: List[str], 
                           preferred_level: str = None,
                           max_courses_per_skill: int = 3) -> Dict:
    """
    Match courses to missing skills with intelligent filtering
    
    Args:
        missing_skills: List of skills user needs to learn
        preferred_level: Preferred difficulty level (beginner/intermediate/advanced)
        max_courses_per_skill: Maximum number of courses to recommend per skill
    
    Returns:
        Dictionary with matched courses organized by skill
    """
    courses = load_courses()
    matched_courses = {}
    
    for skill in missing_skills:
        skill_courses = []
        
        for course in courses:
            # Check if course matches the skill (fuzzy matching for better results)
            course_skill = course.get('skill', '').lower()
            skill_lower = skill.lower()
            
            # Exact match
            if course_skill == skill_lower:
                match_score = 100
            # Check for common skill variations
            elif skill_lower in course_skill or course_skill in skill_lower:
                match_score = 95
            # Fuzzy match
            else:
                match_score = fuzz.ratio(course_skill, skill_lower)
            
            # Include course if it's a good match
            if match_score >= 50:  # 50% similarity threshold to catch more matches
                course_with_score = course.copy()
                course_with_score['match_score'] = match_score
                skill_courses.append(course_with_score)
        
        # Filter by preferred level if specified
        if preferred_level and preferred_level != 'all':
            skill_courses = [
                course for course in skill_courses 
                if course.get('level', '').lower() == preferred_level.lower()
            ]
        
        # Sort by match score and level (beginner first)
        skill_courses.sort(key=lambda x: (
            -x['match_score'],
            {'beginner': 0, 'intermediate': 1, 'advanced': 2}.get(x.get('level', 'intermediate'), 1)
        ))
        
        # Limit number of courses per skill
        if skill_courses:
            matched_courses[skill] = skill_courses[:max_courses_per_skill]
    
    return matched_courses

def get_course_recommendations(missing_skills: List[str], 
                              user_preferences: Dict = None) -> Dict:
    """
    Get comprehensive course recommendations based on missing skills and user preferences
    
    Args:
        missing_skills: List of skills user needs to learn
        user_preferences: Dictionary with user preferences like level, provider, duration
    
    Returns:
        Dictionary with structured course recommendations
    """
    if user_preferences is None:
        user_preferences = {}
    
    preferred_level = user_preferences.get('level', 'beginner')
    preferred_provider = user_preferences.get('provider')
    max_duration = user_preferences.get('max_duration')
    
    # Get basic matched courses
    matched_courses = match_courses_to_skills(missing_skills, preferred_level)
    
    # Apply additional filters
    filtered_courses = {}
    
    for skill, courses in matched_courses.items():
        filtered_skill_courses = []
        
        for course in courses:
            # Filter by provider if specified
            if preferred_provider and preferred_provider.lower() != 'all':
                if course.get('provider', '').lower() == preferred_provider.lower():
                    filtered_skill_courses.append(course)
            else:
                # If no provider specified or "All" is selected, include all courses
                filtered_skill_courses.append(course)
            
            # Filter by duration if specified
            if max_duration:
                duration_str = course.get('duration', '').lower()
                if 'month' in duration_str:
                    try:
                        months = int(duration_str.split()[0])
                        if months > max_duration:
                            # Remove the last added course if duration exceeds limit
                            if filtered_skill_courses and filtered_skill_courses[-1] == course:
                                filtered_skill_courses.pop()
                            continue
                    except (ValueError, IndexError):
                        pass
        
        if filtered_skill_courses:
            filtered_courses[skill] = filtered_skill_courses
    
    # Generate summary statistics
    total_courses = sum(len(courses) for courses in filtered_courses.values())
    
    # Organize by difficulty level
    courses_by_level = {'beginner': [], 'intermediate': [], 'advanced': []}
    
    for skill, courses in filtered_courses.items():
        for course in courses:
            level = course.get('level', 'intermediate').lower()
            if level in courses_by_level:
                courses_by_level[level].append({
                    'skill': skill,
                    'course': course
                })
    
    # Get unique providers
    all_providers = set()
    for courses in filtered_courses.values():
        for course in courses:
            if course.get('provider'):
                all_providers.add(course['provider'])
    
    return {
        'matched_courses': filtered_courses,
        'total_skills': len(filtered_courses),
        'total_courses': total_courses,
        'courses_by_level': courses_by_level,
        'available_providers': list(all_providers),
        'recommendations_summary': generate_recommendation_summary(filtered_courses, missing_skills)
    }

def generate_recommendation_summary(matched_courses: Dict, missing_skills: List[str]) -> str:
    """Generate a human-readable summary of course recommendations"""
    total_courses = sum(len(courses) for courses in matched_courses.values())
    covered_skills = len(matched_courses)
    
    # Positive summary only - no negative messages
    summary = f"Found {total_courses} courses covering {covered_skills} skills for your learning journey. "
    
    # Add provider information
    providers = set()
    for courses in matched_courses.values():
        for course in courses:
            if course.get('provider'):
                providers.add(course['provider'])
    
    if providers:
        provider_list = list(providers)[:3]
        if len(providers) <= 3:
            summary += f"Available from: {', '.join(provider_list)}."
        else:
            summary += f"Available from: {', '.join(provider_list)} and {len(providers) - 3} more platforms."
    
    return summary

def get_course_by_id(course_id: str) -> Dict:
    """Get course details by ID (placeholder for future enhancement)"""
    courses = load_courses()
    for course in courses:
        if course.get('id') == course_id or course.get('title') == course_id:
            return course
    return {}

def filter_courses_by_criteria(courses: List[Dict], criteria: Dict) -> List[Dict]:
    """
    Filter courses based on various criteria
    
    Args:
        courses: List of courses to filter
        criteria: Dictionary with filtering criteria
    
    Returns:
        Filtered list of courses
    """
    filtered = courses.copy()
    
    # Filter by level
    if 'level' in criteria and criteria['level'] != 'all':
        filtered = [c for c in filtered if c.get('level', '').lower() == criteria['level'].lower()]
    
    # Filter by provider
    if 'provider' in criteria:
        filtered = [c for c in filtered if c.get('provider', '').lower() == criteria['provider'].lower()]
    
    # Filter by duration
    if 'max_duration' in criteria:
        max_duration = criteria['max_duration']
        filtered = [c for c in filtered if parse_duration(c.get('duration', '')) <= max_duration]
    
    # Filter by minimum rating (if available)
    if 'min_rating' in criteria:
        min_rating = criteria['min_rating']
        filtered = [c for c in filtered if c.get('rating', 0) >= min_rating]
    
    return filtered

def parse_duration(duration_str: str) -> int:
    """Parse duration string to number of months"""
    duration_str = duration_str.lower().strip()
    
    if 'month' in duration_str:
        try:
            return int(duration_str.split()[0])
        except (ValueError, IndexError):
            return 12  # Default to 12 months if parsing fails
    
    return 12  # Default duration

def get_learning_path_recommendations(missing_skills: List[str], 
                                    time_commitment: str) -> Dict:
    """
    Get learning path recommendations ordered by priority and time commitment
    
    Args:
        missing_skills: List of missing skills
        time_commitment: User's time commitment
    
    Returns:
        Ordered learning path with courses
    """
    recommendations = get_course_recommendations(missing_skills)
    
    # Parse time commitment
    hours_per_week = parse_time_commitment(time_commitment)
    
    # Order courses by skill priority and difficulty
    learning_path = []
    
    # Start with beginner courses
    for level in ['beginner', 'intermediate', 'advanced']:
        level_courses = recommendations['courses_by_level'].get(level, [])
        
        # Sort by skill importance (basic skills first)
        skill_priority = {
            'Python': 1, 'JavaScript': 1, 'HTML': 1, 'CSS': 1, 'SQL': 2,
            'Git': 2, 'Statistics': 2, 'Machine Learning': 3, 'React': 3,
            'Node.js': 3, 'Deep Learning': 4, 'TensorFlow': 4, 'AWS': 4
        }
        
        level_courses.sort(key=lambda x: skill_priority.get(x['skill'], 5))
        
        for item in level_courses:
            learning_path.append({
                'skill': item['skill'],
                'course': item['course'],
                'estimated_weeks': estimate_course_duration(item['course'], hours_per_week),
                'priority': skill_priority.get(item['skill'], 5)
            })
    
    return {
        'learning_path': learning_path,
        'total_estimated_weeks': sum(item['estimated_weeks'] for item in learning_path),
        'hours_per_week': hours_per_week,
        'recommendations': recommendations
    }

def parse_time_commitment(time_commitment: str) -> int:
    """Parse time commitment string to hours per week"""
    time_commitment = time_commitment.lower()
    
    if 'hour' in time_commitment:
        try:
            return int(time_commitment.split()[0])
        except (ValueError, IndexError):
            return 10  # Default to 10 hours per week
    
    return 10  # Default

def estimate_course_duration(course: Dict, hours_per_week: int) -> int:
    """Estimate course duration in weeks based on course details and time commitment"""
    duration_str = course.get('duration', '').lower()
    
    if 'month' in duration_str:
        try:
            months = int(duration_str.split()[0])
            return months * 4  # Approximate 4 weeks per month
        except (ValueError, IndexError):
            pass
    
    # Default estimation based on course level
    level = course.get('level', 'intermediate').lower()
    if level == 'beginner':
        return 8  # 8 weeks for beginner courses
    elif level == 'intermediate':
        return 12  # 12 weeks for intermediate courses
    else:
        return 16  # 16 weeks for advanced courses
