##  Career Path AI

An AI-powered career guidance application that helps users identify skill gaps, explore suitable career roles, and generate personalized learning roadmaps based on their skills and career goals.

---

##  Features

-  User Authentication (Login & Signup)
-  User Profile Management
-  AI-Based Skill Analysis
-  Skill Gap Identification
-  Career Role Recommendations
-  Personalized Learning Roadmaps
-  Course Recommendations
-  JSON-Based Data Storage
-  Interactive Streamlit Web Interface

---

##  Tech Stack

- **Frontend:** Streamlit
- **Backend:** Python
- **Database:** JSON
- **AI Integration:** OpenAI API
- **Environment:** Python Virtual Environment

---

##  Project Structure

```
Career_Path_AI/
│
├── app.py
├── auth.py
├── skill_analysis.py
├── roadmap_generator.py
├── course_matcher.py
├── requirements.txt
├── .env
│
├── data/
│   ├── users.json
│   ├── roles.json
│   ├── courses.json
│   └── jobs.json
│
├── utils/
│
├── assets/
│
└── README.md
```

---

##  Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/career-path-ai.git
cd career-path-ai
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**Windows**

```bash
venv\Scripts\activate
```

**Linux / macOS**

```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Create Environment File

Create a file named `.env`

```env
OPENAI_API_KEY=your_openai_api_key
```

### 6. Run the Application

```bash
streamlit run app.py
```

Open your browser and visit:

```
http://localhost:8501
```

---

##  Screenshots

Add screenshots of your application here.

### Login Page

```
images/login.png
```

### Dashboard

```
images/dashboard.png
```

### Skill Analysis

```
images/skill-analysis.png
```

### Learning Roadmap

```
images/roadmap.png
```

---

##  How It Works

1. Register or log in to your account.
2. Enter your existing skills and career interests.
3. The system analyzes your skills.
4. It identifies missing skills required for your target career.
5. AI generates a personalized learning roadmap.
6. Recommended courses help bridge the identified skill gaps.

---

##  Future Enhancements

- MongoDB/MySQL Database Integration
- Resume Analyzer
- AI Career Chatbot
- Progress Tracking Dashboard
- Certificate Management
- Job Recommendation System
- Learning Progress Analytics

---

##  Learning Outcomes

This project demonstrates knowledge of:

- Python Programming
- Streamlit Development
- User Authentication
- JSON Data Management
- AI API Integration
- Software Design
- Problem Solving
- Project Organization

---

##  Author

-**Rajeswari Pediredla**  
GitHub: https://github.com/rajeswaripediredla
LinkedIn: *www.linkedin.com/in/rajeswari-pediredla-a8b43233b*

-**Likhitha Panchumarthi**

-**MounikaNare Lourdhu**   
GitHub: https://github.com/Mounikanare1708

---



##  Support

If you found this project useful, please consider giving it a ⭐ on GitHub!

---

##  License

This project is intended for educational and learning purposes.
