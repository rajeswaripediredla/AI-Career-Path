import os
import json
from typing import List, Dict, Optional
from openai import OpenAI

class RoadmapGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    def generate_roadmap(self, target_role: str, missing_skills: List[str], 
                        time_commitment: str, existing_skills: List[str] = None) -> Dict:
        """
        Generate a personalized learning roadmap using OpenAI API or fallback
        
        Args:
            target_role: The role user wants to achieve
            missing_skills: List of skills user needs to learn
            time_commitment: User's time commitment (e.g., "10 hours per week", "3 months")
            existing_skills: List of skills user already has
        
        Returns:
            Dictionary containing structured roadmap
        """
        if existing_skills is None:
            existing_skills = []
        
        # Try OpenAI API first
        try:
            if self.client and os.getenv('OPENAI_API_KEY'):
                prompt = self._create_prompt(target_role, missing_skills, time_commitment, existing_skills)
                
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert career counselor and learning path designer. Create detailed, actionable learning roadmaps."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )
                
                roadmap_text = response.choices[0].message.content
                structured_roadmap = self._parse_roadmap(roadmap_text)
                
                return {
                    'success': True,
                    'roadmap': structured_roadmap,
                    'raw_text': roadmap_text,
                    'metadata': {
                        'target_role': target_role,
                        'missing_skills_count': len(missing_skills),
                        'time_commitment': time_commitment,
                        'existing_skills_count': len(existing_skills),
                        'source': 'openai'
                    }
                }
        except Exception as e:
            # If OpenAI fails, fall back to mock roadmap
            print(f"OpenAI API failed: {e}")
            return self._generate_mock_roadmap(target_role, missing_skills, time_commitment, existing_skills)
        
        # Fallback to mock if no client or API key
        return self._generate_mock_roadmap(target_role, missing_skills, time_commitment, existing_skills)
    
    def _create_prompt(self, target_role: str, missing_skills: List[str], 
                      time_commitment: str, existing_skills: List[str]) -> str:
        """Create a detailed prompt for OpenAI"""
        
        prompt = f"""
Create a detailed learning roadmap for someone who wants to become a {target_role}.

CURRENT SITUATION:
- Target Role: {target_role}
- Skills they already have: {', '.join(existing_skills) if existing_skills else 'None'}
- Skills they need to learn: {', '.join(missing_skills)}
- Time commitment: {time_commitment}

Please create a structured learning roadmap with the following format:

## Learning Roadmap for {target_role}

### Overview
[Brief summary of the learning journey]

### Phase 1: Foundation Skills (Weeks 1-4)
**Topics:**
- [Topic 1]
- [Topic 2]
- [Topic 3]

**Recommended Resources:**
- [Resource 1 with link if possible]
- [Resource 2 with link if possible]

**Practice Projects:**
- [Project 1]
- [Project 2]

**Difficulty Level:** Beginner

### Phase 2: Intermediate Skills (Weeks 5-8)
**Topics:**
- [Topic 1]
- [Topic 2]
- [Topic 3]

**Recommended Resources:**
- [Resource 1 with link if possible]
- [Resource 2 with link if possible]

**Practice Projects:**
- [Project 1]
- [Project 2]

**Difficulty Level:** Intermediate

### Phase 3: Advanced Skills (Weeks 9-12)
**Topics:**
- [Topic 1]
- [Topic 2]
- [Topic 3]

**Recommended Resources:**
- [Resource 1 with link if possible]
- [Resource 2 with link if possible]

**Practice Projects:**
- [Project 1]
- [Project 2]

**Difficulty Level:** Advanced

### Phase 4: Specialization & Portfolio (Weeks 13-16)
**Topics:**
- [Topic 1]
- [Topic 2]

**Recommended Resources:**
- [Resource 1 with link if possible]

**Capstone Project:**
- [Detailed capstone project description]

**Difficulty Level:** Advanced

### Success Metrics
- [What they should be able to do after each phase]
- [How to measure progress]

### Tips for Success
- [3-5 specific tips for this learning journey]

Make the roadmap practical, specific, and tailored to the {time_commitment} time commitment. 
Focus on the missing skills but build on their existing knowledge.
"""
        
        return prompt
    
    def _parse_roadmap(self, roadmap_text: str) -> Dict:
        """Parse the roadmap text into a structured format"""
        
        # Simple parsing - in production, you might use more sophisticated parsing
        phases = []
        lines = roadmap_text.split('\n')
        current_phase = None
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('### Phase'):
                if current_phase:
                    phases.append(current_phase)
                phase_title = line.replace('###', '').strip()
                current_phase = {
                    'title': phase_title,
                    'topics': [],
                    'resources': [],
                    'projects': [],
                    'difficulty': 'Not specified'
                }
                current_section = 'topics'
            
            elif current_phase and line.startswith('**Topics:**'):
                current_section = 'topics'
            elif current_phase and line.startswith('**Recommended Resources:**'):
                current_section = 'resources'
            elif current_phase and line.startswith('**Practice Projects:**'):
                current_section = 'projects'
            elif current_phase and line.startswith('**Difficulty Level:**'):
                current_section = 'difficulty'
                difficulty = line.replace('**Difficulty Level:**', '').strip()
                current_phase['difficulty'] = difficulty
            
            elif current_phase and line.startswith('- ') and current_section:
                content = line.replace('- ', '').strip()
                if current_section == 'topics':
                    current_phase['topics'].append(content)
                elif current_section == 'resources':
                    current_phase['resources'].append(content)
                elif current_section == 'projects':
                    current_phase['projects'].append(content)
        
        if current_phase:
            phases.append(current_phase)
        
        # Extract other sections
        overview = ""
        success_metrics = []
        tips = []
        
        current_section = None
        for line in lines:
            line = line.strip()
            
            if line.startswith('### Overview'):
                current_section = 'overview'
            elif line.startswith('### Success Metrics'):
                current_section = 'metrics'
            elif line.startswith('### Tips for Success'):
                current_section = 'tips'
            elif line.startswith('###') and not any(keyword in line for keyword in ['Overview', 'Success Metrics', 'Tips for Success', 'Phase']):
                current_section = None
            
            elif current_section == 'overview' and line and not line.startswith('#'):
                overview += line + " "
            elif current_section == 'metrics' and line.startswith('- '):
                success_metrics.append(line.replace('- ', '').strip())
            elif current_section == 'tips' and line.startswith('- '):
                tips.append(line.replace('- ', '').strip())
        
        return {
            'overview': overview.strip(),
            'phases': phases,
            'success_metrics': success_metrics,
            'tips': tips,
            'total_phases': len(phases)
        }
    
    def save_roadmap(self, roadmap: Dict, user_email: str, filename: Optional[str] = None) -> str:
        """Save roadmap to JSON file"""
        if filename is None:
            timestamp = str(int(time.time()))
            filename = f"roadmap_{user_email}_{timestamp}.json"
        
        # Create roadmaps directory if it doesn't exist
        os.makedirs("data/roadmaps", exist_ok=True)
        
        filepath = f"data/roadmaps/{filename}"
        
        roadmap_data = {
            'user_email': user_email,
            'generated_at': str(time.time()),
            'roadmap': roadmap
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(roadmap_data, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def load_roadmap(self, filepath: str) -> Dict:
        """Load roadmap from JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _generate_mock_roadmap(self, target_role: str, missing_skills: List[str], 
                              time_commitment: str, existing_skills: List[str]) -> Dict:
        """Generate a mock roadmap when OpenAI API is unavailable"""
        
        # Create phases based on missing skills with proper difficulty progression
        phases = []
        
        # Define skill importance levels (basic to advanced)
        basic_skills = ['Python', 'SQL', 'Statistics', 'Linear Algebra', 'Probability']
        intermediate_skills = ['Machine Learning', 'Data Visualization', 'Data Cleaning']
        advanced_skills = ['Deep Learning', 'Feature Engineering', 'TensorFlow', 'PyTorch']
        
        # Categorize missing skills by difficulty
        categorized_skills = {
            'beginner': [],
            'intermediate': [],
            'advanced': [],
            'expert': []
        }
        
        for skill in missing_skills:
            skill_lower = skill.lower()
            if any(basic in skill_lower for basic in basic_skills):
                categorized_skills['beginner'].append(skill)
            elif any(intermediate in skill_lower for intermediate in intermediate_skills):
                categorized_skills['intermediate'].append(skill)
            else:
                categorized_skills['advanced'].append(skill)
        
        # Create phases with proper skill distribution in correct order
        phase_number = 1
        difficulty_order = ['beginner', 'intermediate', 'advanced', 'expert']
        
        for difficulty in difficulty_order:
            if categorized_skills[difficulty]:
                phase_skills = categorized_skills[difficulty]
                phase = {
                    'title': f'Phase {phase_number}: {difficulty.title()} Skills',
                    'topics': phase_skills,
                    'resources': [
                        f'Online courses for {skill}' 
                        for skill in phase_skills[:2]  # Limit resources
                    ],
                    'projects': [
                        f'Build a {skill} project' 
                        for skill in phase_skills[:2]  # Limit projects
                    ],
                    'difficulty': difficulty
                }
                phases.append(phase)
                phase_number += 1
        
        # Ensure we have exactly 4 phases in correct order
        while len(phases) < 4:
            current_difficulty = difficulty_order[min(len(phases), len(difficulty_order) - 1)]
            
            phases.append({
                'title': f'Phase {phase_number}: {current_difficulty.title()} Skills',
                'topics': ['Advanced problem solving', 'Portfolio development'],
                'resources': ['GitHub projects', 'Coding challenges'],
                'projects': ['Capstone project', 'Portfolio website'],
                'difficulty': current_difficulty
            })
            phase_number += 1
        
        # Sort phases by difficulty level
        difficulty_order = {'beginner': 0, 'intermediate': 1, 'advanced': 2, 'expert': 3}
        phases.sort(key=lambda x: difficulty_order.get(x['difficulty'].lower(), 0))
        
        roadmap = {
            'overview': f"This is a structured learning path to help you become a {target_role}. The roadmap is designed to build your skills progressively over {time_commitment}. You'll start with foundational concepts and gradually move to advanced topics.",
            'phases': phases[:4],  # Limit to 4 phases
            'success_metrics': [
                f"Complete all {len(missing_skills)} skill modules",
                "Build 3+ portfolio projects",
                "Achieve practical understanding of core concepts",
                f"Be ready for {target_role} interviews"
            ],
            'tips': [
                "Practice coding every day",
                "Join online communities for support",
                "Build projects to reinforce learning",
                "Seek feedback on your work",
                "Stay consistent with your schedule"
            ],
            'total_phases': len(phases[:4])
        }
        
        return {
            'success': True,
            'roadmap': roadmap,
            'raw_text': f"Mock roadmap for {target_role}",
            'metadata': {
                'target_role': target_role,
                'missing_skills_count': len(missing_skills),
                'time_commitment': time_commitment,
                'existing_skills_count': len(existing_skills),
                'source': 'mock'
            }
        }

import time
