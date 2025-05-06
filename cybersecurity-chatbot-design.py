"""
CyberGuard - An Interactive Cybersecurity Education Chatbot
Built with Flask, Python, and OpenAI
"""

# app.py - Main Flask Application
from flask import Flask, render_template, request, jsonify, session
from openai import OpenAI
import os
import json
import secrets
from modules.password_checker import check_password_strength
from modules.phishing_simulator import generate_phishing_example
from modules.lesson_manager import get_lesson_content, get_next_lesson
from modules.quiz_manager import generate_quiz, evaluate_answer

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Load cybersecurity content
with open('data/lessons.json', 'r') as f:
    LESSONS = json.load(f)

# Configure system prompt for the chatbot
SYSTEM_PROMPT = """
You are CyberGuard, an educational assistant specialized in teaching cybersecurity concepts in a 
friendly, conversational manner. Your primary goal is to help users understand cybersecurity 
fundamentals and develop good security habits.

Topics you can teach include:
- Password creation and management best practices
- How to identify phishing attempts
- Safe browsing habits
- Understanding malware and how to prevent it
- Basic data protection techniques
- Two-factor authentication
- Public Wi-Fi safety

Present information in bite-sized, easy-to-understand chunks. Use examples that relate to everyday 
activities. When appropriate, ask questions to check understanding and engage the user.
"""

@app.route('/')
def index():
    # Initialize user session if new
    if 'user_progress' not in session:
        session['user_progress'] = {
            'completed_lessons': [],
            'current_lesson': 'introduction',
            'knowledge_level': 'beginner'
        }
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    user_progress = session.get('user_progress', {})
    
    # Process special commands
    if user_message.startswith('/lesson'):
        lesson_id = user_message.split(' ')[1] if len(user_message.split(' ')) > 1 else user_progress['current_lesson']
        lesson_content = get_lesson_content(lesson_id, LESSONS)
        return jsonify({'response': lesson_content})
    
    elif user_message.startswith('/quiz'):
        topic = user_message.split(' ')[1] if len(user_message.split(' ')) > 1 else user_progress['current_lesson']
        quiz = generate_quiz(topic)
        return jsonify({'response': quiz, 'type': 'quiz'})
    
    elif user_message.startswith('/check_password'):
        password = user_message.split(' ')[1] if len(user_message.split(' ')) > 1 else ""
        result = check_password_strength(password)
        return jsonify({'response': result})
    
    elif user_message.startswith('/phishing_example'):
        example = generate_phishing_example()
        return jsonify({'response': example, 'type': 'phishing_example'})
    
    # Process normal chat interaction with OpenAI
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
    ]
    
    # Add context about user's progress for more personalized responses
    if user_progress.get('knowledge_level'):
        context = f"The user's current knowledge level is {user_progress['knowledge_level']}. "
        context += f"They have completed these lessons: {', '.join(user_progress.get('completed_lessons', []))}. "
        context += f"Their current lesson is {user_progress.get('current_lesson', 'introduction')}."
        messages.append({"role": "system", "content": context})
    
    # Get response from OpenAI
    try:
        completion = client.chat.completions.create(
            model="gpt-4",  # Can be adjusted based on requirements
            messages=messages,
            max_tokens=500
        )
        response = completion.choices[0].message.content
        
        # Update user progress based on conversation context
        # (In a real system, this would be more sophisticated)
        if "completed" in user_message.lower() and user_progress['current_lesson'] not in user_progress['completed_lessons']:
            user_progress['completed_lessons'].append(user_progress['current_lesson'])
            user_progress['current_lesson'] = get_next_lesson(user_progress['current_lesson'], LESSONS)
            session['user_progress'] = user_progress
            
        return jsonify({'response': response})
    
    except Exception as e:
        return jsonify({'response': f"I'm having trouble connecting right now. Please try again later. Error: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)


# modules/password_checker.py
import re
import zxcvbn  # Would need to be installed: pip install zxcvbn

def check_password_strength(password):
    """
    Evaluates password strength and returns feedback
    """
    if not password:
        return "Please provide a password to check."
    
    # Use zxcvbn for comprehensive password strength evaluation
    result = zxcvbn.zxcvbn(password)
    
    # Basic checks
    has_upper = bool(re.search(r'[A-Z]', password))
    has_lower = bool(re.search(r'[a-z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[^A-Za-z0-9]', password))
    
    feedback = [
        f"Password strength score: {result['score']}/4",
        f"Estimated crack time: {result['crack_times_display']['offline_slow_hashing_1e4_per_second']}"
    ]
    
    # Add specific recommendations
    if not has_upper:
        feedback.append("- Add uppercase letters")
    if not has_lower:
        feedback.append("- Add lowercase letters")
    if not has_digit:
        feedback.append("- Add numbers")
    if not has_special:
        feedback.append("- Add special characters")
    if len(password) < 12:
        feedback.append(f"- Increase length (currently {len(password)}, recommend at least 12)")
    
    # Add zxcvbn's feedback
    if result['feedback']['warning']:
        feedback.append(f"Warning: {result['feedback']['warning']}")
    
    for suggestion in result['feedback']['suggestions']:
        feedback.append(f"- {suggestion}")
    
    return "\n".join(feedback)


# modules/phishing_simulator.py
import random
import json

def generate_phishing_example():
    """
    Creates a simulated phishing email with highlighted red flags
    """
    # Load phishing templates
    with open('data/phishing_templates.json', 'r') as f:
        templates = json.load(f)
    
    # Select a random template
    template = random.choice(templates)
    
    # Create email content with annotations
    email = {
        "from": template["from"],
        "subject": template["subject"],
        "body": template["body"],
        "red_flags": template["red_flags"]
    }
    
    return email


# modules/lesson_manager.py
def get_lesson_content(lesson_id, lessons_data):
    """
    Retrieves content for a specific lesson
    """
    if lesson_id in lessons_data:
        return lessons_data[lesson_id]
    else:
        return "Lesson not found. Available lessons: " + ", ".join(lessons_data.keys())

def get_next_lesson(current_lesson, lessons_data):
    """
    Determines the next lesson based on the curriculum order
    """
    # Define the lesson sequence
    lesson_sequence = list(lessons_data.keys())
    
    try:
        current_index = lesson_sequence.index(current_lesson)
        next_index = (current_index + 1) % len(lesson_sequence)
        return lesson_sequence[next_index]
    except ValueError:
        # If current lesson not found, return the first lesson
        return lesson_sequence[0]


# modules/quiz_manager.py
import random
import json

def generate_quiz(topic):
    """
    Generates a quiz on the specified cybersecurity topic
    """
    # Load quiz questions
    with open('data/quiz_questions.json', 'r') as f:
        all_questions = json.load(f)
    
    # Filter questions for the requested topic
    topic_questions = all_questions.get(topic, [])
    
    if not topic_questions:
        return f"No quiz available for topic: {topic}"
    
    # Select 3-5 random questions
    num_questions = min(random.randint(3, 5), len(topic_questions))
    selected_questions = random.sample(topic_questions, num_questions)
    
    quiz = {
        "topic": topic,
        "questions": selected_questions
    }
    
    return quiz

def evaluate_answer(question_id, user_answer):
    """
    Evaluates a user's answer to a quiz question
    """
    # Load quiz questions
    with open('data/quiz_questions.json', 'r') as f:
        all_questions = json.load(f)
    
    # Find the question and check the answer
    for topic, questions in all_questions.items():
        for question in questions:
            if question.get("id") == question_id:
                correct_answer = question.get("correct_answer")
                if str(user_answer).lower() == str(correct_answer).lower():
                    return {
                        "correct": True,
                        "feedback": question.get("feedback_correct", "Correct!")
                    }
                else:
                    return {
                        "correct": False,
                        "feedback": question.get("feedback_incorrect", f"Incorrect. The correct answer is: {correct_answer}")
                    }
    
    return {"error": "Question not found"}


# Example of the data files structure

# data/lessons.json
"""
{
  "introduction": {
    "title": "Introduction to Cybersecurity",
    "content": "Cybersecurity is about protecting systems, networks, and programs from digital attacks...",
    "key_points": [
      "Cybersecurity protects digital assets from threats",
      "Common threats include malware, phishing, and data breaches",
      "Everyone has a role in maintaining security"
    ],
    "next_steps": "Try the password strength checker with /check_password [your_password]"
  },
  "password_hygiene": {
    "title": "Password Best Practices",
    "content": "Strong passwords are your first line of defense against unauthorized access...",
    "key_points": [
      "Use long, complex passwords with a mix of characters",
      "Never reuse passwords across different accounts",
      "Consider using a password manager"
    ],
    "exercises": [
      "Try the password strength checker with /check_password [your_password]",
      "Take a quiz on password security with /quiz password_hygiene"
    ]
  },
  "phishing_awareness": {
    "title": "Recognizing Phishing Attempts",
    "content": "Phishing is a type of social engineering attack often used to steal user data...",
    "key_points": [
      "Be suspicious of unsolicited emails requesting urgent action",
      "Check email sender addresses carefully",
      "Hover over links before clicking to see the actual URL",
      "Never provide sensitive information in response to an email request"
    ],
    "exercises": [
      "Practice identifying phishing emails with /phishing_example",
      "Take a quiz on phishing with /quiz phishing_awareness"
    ]
  }
}
"""

# data/phishing_templates.json
"""
[
  {
    "from": "security@apple-account-verify.com",
    "subject": "URGENT: Your Apple ID has been locked",
    "body": "Dear Customer,\n\nYour Apple ID has been locked due to too many failed login attempts. To unlock your account, please click the following link and verify your information: https://apple-account-verify.com/unlock\n\nIf you do not complete this process within 24 hours, your account will be permanently disabled.\n\nSincerely,\nApple Support Team",
    "red_flags": [
      "Suspicious domain in sender email - legitimate Apple emails come from @apple.com",
      "Creates urgency to pressure you into acting quickly",
      "Link points to a non-Apple domain",
      "Generic greeting rather than using your name",
      "Threatening consequences if you don't act immediately"
    ]
  },
  {
    "from": "payment-notification@netf1ix.com",
    "subject": "Netflix Payment Failed - Action Required",
    "body": "We were unable to process your payment for your Netflix subscription. To avoid service interruption, please update your payment information immediately by clicking here: https://netf1ix.com/account/payment\n\nIf you need assistance, contact our customer service department.\n\nNetflix Customer Service",
    "red_flags": [
      "Misspelled domain name (netf1ix.com uses the number 1 instead of letter l)",
      "Vague sender name",
      "Link URL doesn't match the legitimate Netflix domain",
      "No specific account information provided",
      "No signature with representative's name"
    ]
  }
]
"""

# data/quiz_questions.json
"""
{
  "password_hygiene": [
    {
      "id": "pw_q1",
      "question": "Which of the following is the MOST secure password?",
      "options": [
        "Password123",
        "MyBirthday1990",
        "k7B#9pL$zQ!2",
        "qwerty12345"
      ],
      "correct_answer": "k7B#9pL$zQ!2",
      "feedback_correct": "Correct! This password includes a mix of uppercase and lowercase letters, numbers, and special characters without forming common words.",
      "feedback_incorrect": "This password isn't the strongest option. The strongest passwords combine uppercase letters, lowercase letters, numbers, and special characters without forming common words or patterns."
    },
    {
      "id": "pw_q2",
      "question": "True or False: It's safe to use the same password across multiple accounts as long as it's complex.",
      "options": ["True", "False"],
      "correct_answer": "False",
      "feedback_correct": "Correct! Even if your password is complex, using it for multiple accounts means that if one account is compromised, all your accounts are at risk.",
      "feedback_incorrect": "Incorrect. Even complex passwords should not be reused. If one service experiences a data breach, attackers could access all your accounts that use the same password."
    }
  ],
  "phishing_awareness": [
    {
      "id": "ph_q1",
      "question": "Which of these is a common sign of a phishing email?",
      "options": [
        "The email addresses you by your full name",
        "The email comes from a domain slightly different from the company it claims to be",
        "The email has the company's logo",
        "The email was sent during business hours"
      ],
      "correct_answer": "The email comes from a domain slightly different from the company it claims to be",
      "feedback_correct": "Correct! Phishers often use domains that look similar to legitimate ones but have slight variations (like amazom.com instead of amazon.com).",
      "feedback_incorrect": "The biggest red flag is a sender domain that's slightly different from the legitimate company (like amaz0n.com instead of amazon.com)."
    }
  ]
}
"""
