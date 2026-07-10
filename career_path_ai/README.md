# AI Personalized Learning Path Generator

A comprehensive web application that generates personalized learning roadmaps using AI to help users achieve their career goals.

## Features

- 🔐 **Authentication System**: Login and signup with local JSON storage
- 📊 **Skill Gap Analysis**: Compare current skills with role requirements
- 🗺️ **AI-Powered Roadmaps**: Generate personalized learning paths using OpenAI API
- 📚 **Course Recommendations**: Match missing skills with relevant courses
- 🎯 **Multiple Career Roles**: Support for 8+ popular tech roles
- 📱 **Responsive UI**: Clean, modern interface using Streamlit

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **AI Integration**: OpenAI API (GPT-3.5-turbo)
- **Data Storage**: JSON files
- **Authentication**: Simple local JSON-based system

## Project Structure

```
career_path_ai/
│
├── app.py                 # Main Streamlit application
├── auth.py                # Authentication system
├── skill_analysis.py      # Skill gap analysis
├── roadmap_generator.py   # AI roadmap generation
├── course_matcher.py      # Course recommendation system
│
├── data/
│   ├── users.json         # User data storage
│   ├── roles.json         # Career role requirements
│   └── courses.json       # Course database
│
├── utils/
│   └── helpers.py         # Utility functions
│
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- OpenAI API key

### 2. Installation

1. Clone or download the project:
```bash
cd career_path_ai
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
export OPENAI_API_KEY="your_openai_api_key_here"
```
On Windows:
```powershell
$env:OPENAI_API_KEY="your_openai_api_key_here"
```

### 3. Run the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## Usage Guide

### 1. Create Account
- Start with signup to create your account
- Enter your name, email, phone, and password

### 2. Login
- Use your email and password to login

### 3. Generate Learning Path
- Enter your current skills (one per line)
- Select your target role from the dropdown
- Choose your time commitment (hours/week or months)
- Click "Generate Learning Path"

### 4. View Analysis
- See skill gap analysis with progress bars
- View skills you have vs. skills you need
- Check match percentage

### 5. Get AI Roadmap
- Click "Generate AI Roadmap" to get personalized learning phases
- View topics, resources, and projects for each phase
- Download roadmap as JSON

### 6. Course Recommendations
- Browse courses for your missing skills
- Filter by difficulty level and provider
- Click on course links to view details

## Supported Career Roles

- Data Scientist
- Web Developer
- Machine Learning Engineer
- Data Analyst
- Full Stack Developer
- DevOps Engineer
- Mobile App Developer
- AI/ML Research Scientist

## Data Files

### roles.json
Contains required skills for each career role. You can add new roles or modify existing ones.

### courses.json
Database of online courses with skill mappings, levels, providers, and links.

### users.json
Stores user account information locally.

## Customization

### Adding New Roles
Edit `data/roles.json`:
```json
{
  "New Role": {
    "required_skills": ["Skill1", "Skill2", "Skill3"]
  }
}
```

### Adding New Courses
Edit `data/courses.json`:
```json
{
  "courses": [
    {
      "skill": "Skill Name",
      "title": "Course Title",
      "link": "https://example.com/course",
      "level": "beginner",
      "provider": "Provider Name",
      "duration": "3 months"
    }
  ]
}
```

## Environment Variables

- `OPENAI_API_KEY`: Required for AI roadmap generation

## Troubleshooting

### Common Issues

1. **OpenAI API Key Error**
   - Ensure the API key is set as environment variable
   - Check if the API key has sufficient credits

2. **Module Import Errors**
   - Ensure all dependencies are installed
   - Check Python version compatibility

3. **File Not Found Errors**
   - Ensure you're running the app from the correct directory
   - Check if data files exist in the `data/` folder

4. **Port Already in Use**
   - Kill existing Streamlit processes
   - Or use: `streamlit run app.py --server.port 8502`

## Features in Detail

### Authentication System
- User registration with validation
- Login with email/password
- Session management
- Logout functionality

### Skill Analysis
- Fuzzy matching for skill comparison
- Gap percentage calculation
- Skill categorization
- Priority analysis

### AI Roadmap Generation
- GPT-3.5-turbo powered
- Structured phase-wise output
- Personalized recommendations
- Resource suggestions

### Course Matching
- Intelligent skill-to-course mapping
- Multiple filtering options
- Provider and level filtering
- Duration-based recommendations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions, please create an issue in the repository.

---

**Note**: This application uses OpenAI API. Ensure you have sufficient API credits for roadmap generation features.
