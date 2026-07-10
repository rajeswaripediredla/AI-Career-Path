import streamlit as st
import os
import sys

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from auth import register_user, authenticate_user, get_user_by_email
from skill_analysis import analyze_skill_gap, get_all_available_roles, generate_skill_summary
from roadmap_generator import RoadmapGenerator
from course_matcher import get_course_recommendations
from utils.helpers import (
    initialize_session_state, logout_user, save_session_data, get_session_data,
    validate_input, create_progress_bar, create_skill_card, create_course_card,
    create_roadmap_phase, load_css_styles, show_message, create_sidebar_navigation,
    check_openai_api_key, format_skills_list, format_time_commitment,
    create_download_button, create_learning_streak
)

def main():
    # Initialize session state
    initialize_session_state()
    
    # Load custom CSS
    load_css_styles()
    
    # Page configuration
    st.set_page_config(
        page_title="Career Path AI - Personalized Learning Path Generator",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Sidebar navigation
    current_page = create_sidebar_navigation()
    st.session_state.current_page = current_page
    
    # Route to appropriate page
    if not st.session_state.get('logged_in'):
        show_login_page()
    else:
        if current_page == 'dashboard':
            show_dashboard()
        elif current_page == 'profile':
            show_profile_page()
        elif current_page == 'input':
            show_input_page()
        elif current_page == 'analysis':
            show_analysis_page()
        elif current_page == 'roadmap':
            show_roadmap_page()
        elif current_page == 'courses':
            show_courses_page()
        else:
            show_dashboard()

def show_login_page():
    """Show login/signup page"""
    st.markdown("""
    <div class="main-header">
        <h1>🎯 Career Path AI</h1>
        <p>Your personalized roadmap to success</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.image("https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=400&h=300&fit=crop", 
                width=400)
    
    with col2:
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            st.subheader("Welcome Back!")
            
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Login", type="primary"):
                is_valid, error = validate_input(email, "email")
                if not is_valid:
                    show_message(error, "error")
                    return
                
                is_valid, error = validate_input(password, "password")
                if not is_valid:
                    show_message(error, "error")
                    return
                
                success, user = authenticate_user(email, password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.user_email = user['email']
                    st.session_state.user_name = user['name']
                    show_message("Login successful! Redirecting to dashboard...", "success")
                    st.rerun()
                else:
                    show_message("Invalid email or password", "error")
        
        with tab2:
            st.subheader("Create Account")
            
            name = st.text_input("Full Name", key="signup_name")
            email = st.text_input("Email", key="signup_email")
            phone = st.text_input("Phone Number", key="signup_phone")
            password = st.text_input("Password", type="password", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
            
            if st.button("Sign Up", type="primary"):
                # Validate all fields
                validations = [
                    (name, "name"),
                    (email, "email"),
                    (phone, "phone"),
                    (password, "password")
                ]
                
                for field_value, field_type in validations:
                    is_valid, error = validate_input(field_value, field_type)
                    if not is_valid:
                        show_message(f"{field_type.title()}: {error}", "error")
                        return
                
                if password != confirm_password:
                    show_message("Passwords do not match", "error")
                    return
                
                success, message = register_user(name, email, phone, password)
                if success:
                    show_message(message, "success")
                    # Clear form
                    st.session_state.signup_name = ""
                    st.session_state.signup_email = ""
                    st.session_state.signup_phone = ""
                    st.session_state.signup_password = ""
                    st.session_state.confirm_password = ""
                else:
                    show_message(message, "error")

def show_dashboard():
    """Show dashboard page"""
    st.markdown("""
    <div class="main-header">
        <h1>🎯 Career Path AI</h1>
        <p>Your personalized roadmap to success</p>
    </div>
    """, unsafe_allow_html=True)
    
    # User info
    user_name = st.session_state.get('user_name', 'User')
    st.markdown(f"### Welcome back, {user_name}! 👋")
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Learning Paths", "0")
    
    with col2:
        st.metric("Skills Analyzed", "0")
    
    with col3:
        st.metric("Courses Recommended", "0")
    
    with col4:
        st.metric("Progress", "0%")
    
    # Action buttons
    st.markdown("---")
    st.subheader("Get Started")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Generate Learning Path", type="primary", use_container_width=True):
            st.session_state.current_page = 'input'
            st.rerun()
    
    with col2:
        if st.button("📊 View Skill Analysis", use_container_width=True):
            if st.session_state.get('skill_analysis_done'):
                st.session_state.current_page = 'analysis'
                st.rerun()
            else:
                show_message("Please generate a learning path first", "info")
    
    # Recent activity (placeholder)
    st.markdown("---")
    st.subheader("Recent Activity")
    show_message("No recent activity. Start by generating your first learning path!", "info")

def show_input_page():
    """Show user input page for learning path generation"""
    st.markdown("""
    <div class="main-header">
        <h1>📝 Create Your Learning Path</h1>
        <p>Tell us about your goals and we'll create a personalized roadmap</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("learning_path_form"):
        st.subheader("Your Information")
        
        # User name (pre-filled)
        user_name = st.text_input("Your Name", value=st.session_state.get('user_name', ''), disabled=True)
        
        # Current skills
        st.subheader("Current Skills")
        st.write("Enter the skills you already have (one per line):")
        current_skills_text = st.text_area(
            "Current Skills",
            placeholder="Python\nJavaScript\nSQL\n...",
            height=150
        )
        
        # Target role
        available_roles = get_all_available_roles()
        if not available_roles:
            show_message("No roles available. Please check the roles data file.", "error")
            return
        
        target_role = st.selectbox(
            "Target Role",
            options=available_roles,
            help="Choose the role you want to achieve"
        )
        
        # Time commitment
        st.subheader("Time Commitment")
        time_option = st.radio(
            "How would you like to specify your time commitment?",
            ["Hours per week", "Months to complete"]
        )
        
        if time_option == "Hours per week":
            time_commitment = st.selectbox(
                "Hours per week",
                options=["5 hours", "10 hours", "15 hours", "20 hours", "25+ hours"],
                index=1
            )
        else:
            time_commitment = st.selectbox(
                "Months to complete",
                options=["3 months", "6 months", "9 months", "12 months", "18+ months"],
                index=1
            )
        
        # Submit button
        submitted = st.form_submit_button("🚀 Generate Learning Path", type="primary")
        
        if submitted:
            # Process the form data
            current_skills = [skill.strip() for skill in current_skills_text.split('\n') if skill.strip()]
            
            if not current_skills:
                show_message("Please enter at least one current skill", "error")
                return
            
            # Save to session state
            save_session_data('current_skills', current_skills)
            save_session_data('target_role', target_role)
            save_session_data('time_commitment', time_commitment)
            
            # Perform skill analysis
            with st.spinner("Analyzing your skills..."):
                analysis_result = analyze_skill_gap(current_skills, target_role)
                save_session_data('skill_analysis', analysis_result)
                save_session_data('skill_analysis_done', True)
            
            show_message("Skill analysis complete! Redirecting to analysis page...", "success")
            st.session_state.current_page = 'analysis'
            st.rerun()

def show_analysis_page():
    """Show skill gap analysis page"""
    if not st.session_state.get('skill_analysis_done'):
        show_message("Please complete the learning path input first", "info")
        return
    
    st.markdown("""
    <div class="main-header">
        <h1>📊 Skill Gap Analysis</h1>
        <p>See how your current skills match your target role requirements</p>
    </div>
    """, unsafe_allow_html=True)
    
    analysis = get_session_data('skill_analysis')
    target_role = get_session_data('target_role')
    current_skills = get_session_data('current_skills')
    
    if not analysis:
        show_message("No analysis data available", "error")
        return
    
    # Summary section
    st.subheader(f"Analysis Summary for {target_role}")
    
    # Progress bar
    match_percentage = 100 - analysis['skill_gap_percentage']
    create_progress_bar(match_percentage, "Skill Match")
    
    # Stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Required Skills", analysis['total_required_skills'])
    
    with col2:
        st.metric("Skills You Have", analysis['total_existing_skills'])
    
    with col3:
        st.metric("Skills to Learn", analysis['total_missing_skills'])
    
    # Detailed analysis
    st.markdown("---")
    
    # Skills You Have Section
    st.subheader("✅ Skills You Have")
    if analysis['existing_skills']:
        for skill in analysis['existing_skills']:
            create_skill_card(skill, "Existing", "existing")
    else:
        show_message("No matching skills found", "info")
    
    # Skills to Learn Section
    st.markdown("---")
    st.subheader("🎯 Skills to Learn")
    if analysis['missing_skills']:
        for skill in analysis['missing_skills']:
            create_skill_card(skill, "Missing", "missing")
    else:
        show_message("You have all required skills!", "success")
    
    # Summary text
    st.markdown("---")
    summary = generate_skill_summary(analysis)
    st.info(summary)
    
    # Action buttons
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗺️ Generate AI Roadmap", type="primary", use_container_width=True):
            if check_openai_api_key():
                st.session_state.current_page = 'roadmap'
                st.rerun()
    
    with col2:
        if st.button("📚 View Course Recommendations", use_container_width=True):
            st.session_state.current_page = 'courses'
            st.rerun()

def show_roadmap_page():
    """Show AI-generated roadmap page"""
    if not st.session_state.get('skill_analysis_done'):
        show_message("Please complete skill analysis first", "info")
        return
    
    analysis = get_session_data('skill_analysis')
    target_role = get_session_data('target_role')
    time_commitment = get_session_data('time_commitment')
    current_skills = get_session_data('current_skills')
    
    st.markdown("""
    <div class="main-header">
        <h1>🗺️ Your Personalized Learning Roadmap</h1>
        <p>AI-generated learning path tailored to your goals and timeline</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if roadmap is already generated
    if not st.session_state.get('roadmap_generated'):
        if not check_openai_api_key():
            return
        
        # Generate roadmap
        with st.spinner("Generating your personalized roadmap with AI..."):
            generator = RoadmapGenerator()
            result = generator.generate_roadmap(
                target_role=target_role,
                missing_skills=analysis['missing_skills'],
                time_commitment=time_commitment,
                existing_skills=current_skills
            )
            
            if result['success']:
                save_session_data('roadmap_result', result)
                save_session_data('roadmap_generated', True)
                show_message("Roadmap generated successfully!", "success")
            else:
                show_message(f"Error generating roadmap: {result.get('error', 'Unknown error')}", "error")
                return
    
    # Display roadmap
    roadmap_data = get_session_data('roadmap_result')
    if not roadmap_data or not roadmap_data['success']:
        show_message("No roadmap data available", "error")
        return
    
    roadmap = roadmap_data['roadmap']
    
    # Display learning streak
    create_learning_streak()
    
    # Overview
    if roadmap.get('overview'):
        st.subheader("📋 Overview")
        st.write(roadmap['overview'])
    
    # Phases sorted by difficulty
    if roadmap.get('phases'):
        st.subheader("🎯 Learning Phases (Basic to Advanced)")
        
        # Sort phases by difficulty level
        difficulty_order = {'beginner': 0, 'intermediate': 1, 'advanced': 2, 'expert': 3}
        sorted_phases = sorted(roadmap['phases'], key=lambda x: difficulty_order.get(x['difficulty'].lower(), 0))
        
        # Debug: Show the order
        st.write("Debug - Phase order:")
        for i, phase in enumerate(sorted_phases):
            st.write(f"  Phase {i+1}: {phase.get('difficulty', 'unknown')} - {phase.get('topics', [])}")
        
        for i, phase in enumerate(sorted_phases, 1):
            create_roadmap_phase(phase, i)
    
    # Success metrics
    if roadmap.get('success_metrics'):
        st.subheader("📈 Success Metrics")
        for metric in roadmap['success_metrics']:
            st.write(f"- {metric}")
    
    # Tips
    if roadmap.get('tips'):
        st.subheader("💡 Tips for Success")
        for tip in roadmap['tips']:
            st.write(f"- {tip}")
    
    # Download option only (removed course recommendations)
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("� Back to Analysis", use_container_width=True):
            st.session_state.current_page = 'analysis'
            st.rerun()
    
    with col2:
        if st.button("📥 Download Roadmap", use_container_width=True):
            create_download_button(
                roadmap_data,
                f"learning_roadmap_{target_role.replace(' ', '_')}.json",
                "Download Roadmap as JSON"
            )

def show_courses_page():
    """Show course recommendations page"""
    if not st.session_state.get('skill_analysis_done'):
        show_message("Please complete skill analysis first", "info")
        return
    
    analysis = get_session_data('skill_analysis')
    st.markdown("""
    <div class="main-header">
        <h1>📚 Course Recommendations</h1>
        <p>Curated courses to help you acquire the missing skills</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Generate course recommendations
    with st.spinner("Finding the best courses for you..."):
        recommendations = get_course_recommendations(analysis['missing_skills'])
    
    # Filter options
    st.subheader("🔍 Filter Options")
    col1, col2 = st.columns(2)
    
    with col1:
        selected_level = st.selectbox(
            "Difficulty Level",
            options=["All", "Beginner", "Intermediate", "Advanced"],
            index=0
        )
    
    with col2:
        selected_provider = st.selectbox(
            "Provider",
            options=["All"] + recommendations['available_providers'],
            index=0
        )
    
    # Display courses by skill
    st.markdown("---")
    st.subheader("🎯 Courses by Skill")
    
    matched_courses = recommendations['matched_courses']
    
    if not matched_courses:
        show_message("No courses found for your missing skills", "info")
        return
    
    for skill, courses in matched_courses.items():
        st.markdown(f"### {skill}")
        
        # Filter courses based on selection
        filtered_courses = courses
        if selected_level != "All":
            filtered_courses = [c for c in filtered_courses if c.get('level', '').lower() == selected_level.lower()]
        
        if selected_provider != "All":
            filtered_courses = [c for c in filtered_courses if c.get('provider', '') == selected_provider]
        
        if filtered_courses:
            for course in filtered_courses:
                create_course_card(course)
        else:
            st.info(f"No courses match the selected filters for {skill}")
    
    # Statistics
    st.markdown("---")
    st.subheader("📈 Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Skills Covered", recommendations['total_skills'])
    
    with col2:
        st.metric("Total Courses", recommendations['total_courses'])
    
    with col3:
        st.metric("Providers", len(recommendations['available_providers']))
    
    # Action buttons
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗺️ View AI Roadmap", use_container_width=True):
            st.session_state.current_page = 'roadmap'
            st.rerun()
    
    with col2:
        if st.button("📊 Back to Analysis", use_container_width=True):
            st.session_state.current_page = 'analysis'
            st.rerun()

def show_profile_page():
    """Show user profile page"""
    st.markdown("""
    <div class="main-header">
        <h1>👤 Edit Profile</h1>
        <p>Update your personal information</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get current user data
    current_name = st.session_state.get('user_name', '')
    current_email = st.session_state.get('user_email', '')
    
    # Profile form
    with st.form("profile_form"):
        st.subheader("Personal Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            new_name = st.text_input("Full Name", value=current_name, key="profile_name")
        
        with col2:
            new_email = st.text_input("Email Address", value=current_email, key="profile_email")
        
        st.subheader("Career Information")
        target_role = st.selectbox(
            "Target Career Role",
            ["Data Scientist", "Machine Learning Engineer", "Data Analyst", "Software Developer", "Product Manager", "Other"],
            index=0,
            key="profile_role"
        )
        
        experience_level = st.selectbox(
            "Experience Level",
            ["Beginner", "Intermediate", "Advanced", "Expert"],
            index=0,
            key="profile_experience"
        )
        
        time_commitment = st.selectbox(
            "Time Commitment",
            ["1-2 hours per week", "3-5 hours per week", "6-10 hours per week", "10+ hours per week"],
            index=1,
            key="profile_time"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            submitted = st.form_submit_button("💾 Save Changes", use_container_width=True)
        
        with col2:
            if st.form_submit_button("🔄 Reset", use_container_width=True):
                st.rerun()
        
        if submitted:
            # Update session state
            st.session_state.user_name = new_name
            st.session_state.user_email = new_email
            
            # Here you would typically update the database
            # For now, we'll just show a success message
            show_message("Profile updated successfully!", "success")
            st.rerun()
    
    st.markdown("---")
    
    # Account settings section
    st.subheader("🔐 Account Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Change Password", use_container_width=True):
            show_message("Password change feature coming soon!", "info")
    
    with col2:
        if st.button("📊 View Progress", use_container_width=True):
            st.session_state.current_page = 'dashboard'
            st.rerun()

if __name__ == "__main__":
    main()
