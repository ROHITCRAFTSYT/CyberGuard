# CyberGuard - Cybersecurity Education Chatbot

CyberGuard is an interactive educational chatbot designed to teach cybersecurity concepts through conversational learning. It helps users learn about essential security practices like password hygiene, phishing identification, and more.

## Features

- **Interactive Lessons**: Learn about cybersecurity concepts through guided lessons
- **Knowledge Quizzes**: Test your understanding with topic-specific quizzes
- **Password Strength Checker**: Get feedback on password security and improvement tips
- **Phishing Simulation**: Practice identifying phishing attempts with realistic examples
- **Personalized Learning**: Chatbot adapts to your knowledge level and completed lessons

## Tech Stack

- **Backend**: Python with Flask
- **NLP/AI**: OpenAI API
- **Frontend**: HTML/CSS/JavaScript with Bootstrap
- **Additional Libraries**:
  - `zxcvbn` for advanced password strength analysis
  - `papaparse` for data parsing
  - Various Flask extensions for session management

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/ROHITCRAFTSYT/CyberGuard.git
   cd cyberguard
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```
   export FLASK_APP=app.py
   export FLASK_ENV=development
   export OPENAI_API_KEY=your_openai_api_key
   ```

5. Initialize the database:
   ```
   flask init-db
   ```

6. Run the application:
   ```
   flask run
   ```

The application will be available at `http://127.0.0.1:5000/`.

## Project Structure

```
cyberguard/
├── app.py                      # Main Flask application
├── modules/                    # Application modules
│   ├── __init__.py
│   ├── lesson_manager.py       # Lesson content management
│   ├── password_checker.py     # Password strength analysis
│   ├── phishing_simulator.py   # Phishing example generation
│   └── quiz_manager.py         # Quiz generation and evaluation
├── data/                       # Data files
│   ├── lessons.json            # Lesson content
│   ├── phishing_templates.json # Phishing email templates
│   └── quiz_questions.json     # Quiz questions and answers
├── static/                     # Static files (CSS, JS)
│   ├── css/
│   └── js/
├── templates/                  # HTML templates
│   └── index.html              # Main chat interface
└── requirements.txt            # Python dependencies
```

## Custom Commands

The chatbot understands these special commands:

- `/lesson [topic]` - Start a specific lesson
- `/quiz [topic]` - Take a quiz on a specific topic  
- `/check_password [your_password]` - Check password strength
- `/phishing_example` - See a simulated phishing example

## Development

### Adding New Lessons

To add a new lesson, add a new entry to `data/lessons.json` following the existing format:

```json
"new_lesson_id": {
  "title": "Lesson Title",
  "content": "Main lesson content...",
  "key_points": [
    "Key point 1",
    "Key point 2"
  ],
  "exercises": [
    "Exercise instruction 1",
    "Exercise instruction 2"
  ]
}
```

### Adding Quiz Questions

Add new questions to `data/quiz_questions.json` under the appropriate topic:

```json
"topic_name": [
  {
    "id": "unique_question_id",
    "question": "Question text?",
    "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
    "correct_answer": "Option 2",
    "feedback_correct": "Why this answer is correct...",
    "feedback_incorrect": "Why other answers are incorrect..."
  }
]
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Special thanks to cybersecurity experts for content validation
- Security awareness training resources that inspired lesson content
