import streamlit as st
import json
import os
import re
from datetime import datetime, date
from fuzzywuzzy import fuzz
from typing import Dict, List, Any, Optional

def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    if 'user_name' not in st.session_state:
        st.session_state.user_name = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'login'
    if 'roadmap_generated' not in st.session_state:
        st.session_state.roadmap_generated = False
    if 'skill_analysis_done' not in st.session_state:
        st.session_state.skill_analysis_done = False

def logout_user():
    """Logout user and clear session state"""
    st.session_state.logged_in = False
    st.session_state.user_email = None
    st.session_state.user_name = None
    st.session_state.current_page = 'login'
    st.session_state.roadmap_generated = False
    st.session_state.skill_analysis_done = False

def save_session_data(key: str, data: Any):
    """Save data to session state"""
    st.session_state[key] = data

def get_session_data(key: str, default: Any = None) -> Any:
    """Get data from session state"""
    return st.session_state.get(key, default)

def validate_input(input_value: str, input_type: str) -> tuple[bool, str]:
    """
    Validate user input
    
    Args:
        input_value: The input value to validate
        input_type: Type of input (email, phone, name, etc.)
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check if input_value is None or empty
    if input_value is None:
        return False, "This field is required"
    
    # Convert to string and check if empty after stripping
    if isinstance(input_value, str):
        if not input_value.strip():
            return False, "This field is required"
        input_value = input_value.strip()
    else:
        # Handle non-string inputs
        input_value = str(input_value)
        if not input_value:
            return False, "This field is required"
    
    if input_type == 'email':
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, input_value):
            return False, "Please enter a valid email address"
    
    elif input_type == 'phone':
        if not input_value.isdigit():
            return False, "Phone number should contain only digits"
        if len(input_value) < 10:
            return False, "Phone number should be at least 10 digits"
    
    elif input_type == 'name':
        if len(input_value) < 2:
            return False, "Name should be at least 2 characters long"
        if len(input_value) > 50:
            return False, "Name should not exceed 50 characters"
    
    elif input_type == 'password':
        if len(input_value) < 6:
            return False, "Password should be at least 6 characters long"
    
    return True, ""

def format_skills_list(skills: List[str]) -> str:
    """Format skills list for display"""
    if not skills:
        return "None"
    
    if len(skills) <= 3:
        return ", ".join(skills)
    else:
        return ", ".join(skills[:3]) + f" and {len(skills) - 3} more"

def create_progress_bar(percentage: float, title: str) -> None:
    """Create a custom progress bar"""
    st.write(f"**{title}**")
    progress_color = get_progress_color(percentage)
    st.markdown(f"""
    <div style="width: 100%; background-color: #f0f0f0; border-radius: 10px; overflow: hidden;">
        <div style="width: {percentage}%; background-color: {progress_color}; height: 20px; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">
            {percentage:.1f}%
        </div>
    </div>
    """, unsafe_allow_html=True)

def get_progress_color(percentage: float) -> str:
    """Get color for progress bar based on percentage"""
    if percentage >= 80:
        return "#4CAF50"  # Green
    elif percentage >= 60:
        return "#FF9800"  # Orange
    elif percentage >= 40:
        return "#FFC107"  # Yellow
    else:
        return "#F44336"  # Red

def create_skill_card(skill: str, level: str, status: str) -> None:
    """Create a skill card component"""
    status_color = {
        'existing': '#4CAF50',
        'missing': '#F44336',
        'learning': '#FF9800'
    }.get(status, '#9E9E9E')
    
    st.markdown(f"""
    <div style="border: 1px solid #ddd; border-radius: 8px; padding: 10px; margin: 5px 0; background-color: #f8f9fa;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="color: #333;">
                <strong style="color: #333;">{skill}</strong>
                <br><small style="color: #666;">{level}</small>
            </div>
            <div style="background-color: {status_color}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px;">
                {status.title()}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_course_card(course: Dict) -> None:
    """Create a course card component"""
    level_colors = {
        'beginner': '#4CAF50',
        'intermediate': '#FF9800',
        'advanced': '#F44336'
    }
    
    level = course.get('level', 'intermediate').lower()
    color = level_colors.get(level, '#9E9E9E')
    
    st.markdown(f"""
    <div style="border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin: 10px 0; background-color: #f8f9fa;">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
            <h4 style="margin: 0; color: #333;">{course.get('title', 'Course Title')}</h4>
            <div style="background-color: {color}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px;">
                {course.get('level', 'Intermediate').title()}
            </div>
        </div>
        <p style="margin: 5px 0; color: #666; font-size: 14px;">
            <strong style="color: #333;">Provider:</strong> {course.get('provider', 'Unknown')}<br>
            <strong style="color: #333;">Duration:</strong> {course.get('duration', 'Not specified')}<br>
            <strong style="color: #333;">Skill:</strong> {course.get('skill', 'General')}
        </p>
        <a href="{course.get('link', '#')}" target="_blank" style="display: inline-block; background-color: #007bff; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px; margin-top: 10px;">
            View Course
        </a>
    </div>
    """, unsafe_allow_html=True)

def create_roadmap_phase(phase: Dict, phase_number: int) -> None:
    """Create a roadmap phase component"""
    # Update the title to reflect the correct phase number
    phase_title = f"Phase {phase_number}: {phase.get('difficulty', 'Not specified').title()} Skills"
    
    st.markdown(f"""
    <div style="border: 2px solid #007bff; border-radius: 8px; padding: 10px; margin: 8px 0; background-color: #f8f9fa;">
        <h3 style="color: #007bff; margin: 5px 0;">{phase_title}</h3>
        <div style="background-color: #007bff; color: white; padding: 2px 8px; border-radius: 12px; font-size: 10px; display: inline-block; margin-bottom: 5px;">
            {phase.get('difficulty', 'Not specified').title()}
        </div>
    """, unsafe_allow_html=True)
    
    # Topics
    if phase.get('topics'):
        st.write("**📚 Topics:**")
        for topic in phase['topics']:
            st.write(f"- {topic}")
            st.markdown("<div style='margin-bottom: 2px;'></div>", unsafe_allow_html=True)
    
    # Resources with clickable links
    if phase.get('resources'):
        st.write("**📖 Resources:**")
        for resource in phase['resources']:
            # Check if resource looks like a URL or contains a link
            if 'http' in resource or 'www.' in resource:
                st.markdown(f"- [{resource}]({resource})")
            else:
                st.write(f"- {resource}")
            st.markdown("<div style='margin-bottom: 2px;'></div>", unsafe_allow_html=True)
    
    # Projects
    if phase.get('projects'):
        st.write("**🛠️ Practice Projects:**")
        for project in phase['projects']:
            st.write(f"- {project}")
            st.markdown("<div style='margin-bottom: 2px;'></div>", unsafe_allow_html=True)
    
    # Phase completion button
    if st.button(f"✅ Mark Phase {phase_number} Complete", key=f"complete_phase_{phase_number}"):
        # Update learning streak
        if 'learning_streak' not in st.session_state:
            st.session_state.learning_streak = {
                'current_streak': 0,
                'last_active_date': None,
                'total_days': 0,
                'completed_phases': []
            }
        
        if phase_number not in st.session_state.learning_streak['completed_phases']:
            st.session_state.learning_streak['completed_phases'].append(phase_number)
            st.success(f"Phase {phase_number} marked as complete! Keep up the great work!")
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

def create_learning_streak() -> None:
    """Create a learning streak tracker"""
    # Initialize streak if not exists
    if 'learning_streak' not in st.session_state:
        st.session_state.learning_streak = {
            'current_streak': 0,
            'last_active_date': None,
            'total_days': 0,
            'completed_phases': []
        }
    
    streak_data = st.session_state.learning_streak
    
    # Check if user is active today
    from datetime import datetime, date
    today = date.today()
    
    # Update streak logic
    if streak_data['last_active_date']:
        last_active = datetime.strptime(streak_data['last_active_date'], '%Y-%m-%d').date()
        if today == last_active:
            # Already active today
            pass
        elif (today - last_active).days == 1:
            # Consecutive day
            streak_data['current_streak'] += 1
            streak_data['total_days'] += 1
        else:
            # Streak broken
            streak_data['current_streak'] = 1
            streak_data['total_days'] += 1
    else:
        # First time
        streak_data['current_streak'] = 1
        streak_data['total_days'] = 1
    
    streak_data['last_active_date'] = today.strftime('%Y-%m-%d')
    
    # Display streak
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px; border-radius: 10px; margin: 10px 0;">
        <h4 style="margin: 0; color: white;">🔥 Learning Streak</h4>
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="font-size: 20px; font-weight: bold;">{current_streak} days</div>
                <div style="font-size: 12px; opacity: 0.9;">Current Streak</div>
            </div>
            <div>
                <div style="font-size: 18px; font-weight: bold;">{total_days} days</div>
                <div style="font-size: 12px; opacity: 0.9;">Total Active Days</div>
            </div>
        </div>
    </div>
    """.format(
        current_streak=streak_data['current_streak'],
        total_days=streak_data['total_days']
    ), unsafe_allow_html=True)
    
    return streak_data

def load_css_styles() -> None:
    """Load custom CSS styles"""
    st.markdown("""
    <style>
        .main-header {
            text-align: center;
            padding: 1rem 0;
        }
        
        .skill-gap-container {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
        }
        
        .success-message {
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 0.5rem;
            border-radius: 5px;
            margin: 0.5rem 0;
        }
        
        .error-message {
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
            padding: 0.5rem;
            border-radius: 5px;
            margin: 0.5rem 0;
        }
        
        .info-message {
            background-color: #d1ecf1;
            border: 1px solid #bee5eb;
            color: #0c5460;
            padding: 0.5rem;
            border-radius: 5px;
            margin: 0.5rem 0;
        }
        
        .two-column-layout {
            display: flex;
            gap: 1rem;
        }
        
        .left-column {
            flex: 1;
        }
        
        .right-column {
            flex: 1;
        }
        
        /* Reduce padding and margins for compact layout */
        .stApp > div {
            padding-top: 1rem !important;
        }
        
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
        }
        
        /* Reduce spacing between elements */
        .element-container {
            margin-bottom: 0.5rem !important;
        }
        
        /* Make roadmap phases more compact */
        div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column"] > div {
            margin-bottom: 0.5rem !important;
        }
        
        /* Make course cards more compact */
        div[data-testid="stVerticalBlock"] > div {
            padding: 0.5rem !important;
        }
        
        @media (max-width: 768px) {
            .two-column-layout {
                flex-direction: column;
            }
        }
    </style>
    """, unsafe_allow_html=True)

def show_message(message: str, message_type: str = 'info') -> None:
    """Display a styled message"""
    css_classes = {
        'success': 'success-message',
        'error': 'error-message',
        'info': 'info-message'
    }
    
    css_class = css_classes.get(message_type, 'info-message')
    
    st.markdown(f"""
    <div class="{css_class}">
        {message}
    </div>
    """, unsafe_allow_html=True)

def get_timestamp() -> str:
    """Get current timestamp as string"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def save_to_json_file(data: Dict, filename: str) -> bool:
    """Save data to JSON file"""
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Error saving file: {e}")
        return False

def load_from_json_file(filename: str) -> Optional[Dict]:
    """Load data from JSON file"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

def format_time_commitment(time_str: str) -> str:
    """Format time commitment string"""
    if not time_str:
        return "Not specified"
    
    time_str = time_str.lower().strip()
    
    if 'hour' in time_str:
        return f"{time_str.title()} per week"
    elif 'month' in time_str:
        return f"Complete in {time_str.title()}"
    else:
        return time_str.title()

def create_download_button(data: Dict, filename: str, button_text: str = "Download") -> None:
    """Create a download button for JSON data"""
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    st.download_button(
        label=button_text,
        data=json_str,
        file_name=filename,
        mime='application/json'
    )

def check_openai_api_key() -> bool:
    """Check if OpenAI API key is available"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        st.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        return False
    return True

def create_sidebar_navigation() -> str:
    """Create sidebar navigation"""
    st.sidebar.title("Navigation")
    
    if st.session_state.get('logged_in'):
        pages = {
            'dashboard': '🏠 Dashboard',
            'profile': '👤 Edit Profile',
            'input': '📝 Learning Path Input',
            'analysis': '📊 Skill Analysis',
            'roadmap': '🗺️ Learning Roadmap',
            'courses': '📚 Course Recommendations'
        }
        
        # Show user info
        st.sidebar.markdown(f"**Logged in as:** {st.session_state.get('user_name', 'User')}")
        st.sidebar.markdown(f"**Email:** {st.session_state.get('user_email', 'user@example.com')}")
        
        st.sidebar.markdown("---")
        
        # Use buttons instead of selectbox for better visibility
        current_page = st.session_state.get('current_page', 'dashboard')
        
        selected_page = current_page
        for page_key, page_name in pages.items():
            if st.sidebar.button(page_name, key=f"nav_{page_key}", use_container_width=True):
                selected_page = page_key
        
        st.sidebar.markdown("---")
        
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            logout_user()
            st.rerun()
        
        return selected_page
    else:
        st.sidebar.markdown("**Please login to continue**")
        return 'login'

def create_animated_spinner(message: str = "Loading...") -> None:
    """Create an animated loading spinner"""
    with st.spinner(message):
        st.empty()  # This will be replaced by the actual loading content
