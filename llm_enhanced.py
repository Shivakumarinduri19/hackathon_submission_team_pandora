"""
LLM integration for Exam Coach - includes analysis, planning, and Q&A
"""
import os
import json
import google.generativeai as genai

# Configure Google Gemini
genai.configure(api_key="")
model = genai.GenerativeModel('gemini-2.5-flash')

def analyze_weak_topics(profile_data: dict, test_result_text: str) -> list:
    """
    Analyze mock test results and identify weak topics using Gemini.
    Returns a list of weak topics.
    """
    exam_type = profile_data.get("exam_type", "")
    target = profile_data.get("target_marks_rank", "")
    
    # Check if the input is the user's JSON structure
    try:
        data = json.loads(test_result_text)
        if "questions" in data:
            wrong_qs = [f"Subject: {q.get('subject', 'Unknown')} | Question: {q.get('question')}" 
                        for q in data["questions"] if not q.get("is_correct", True)]
            if wrong_qs:
                test_result_text = "The student answered these questions INCORRECTLY:\n- " + "\n- ".join(wrong_qs)
    except:
        pass

    prompt = f"""You are an expert exam coach. Analyze the following mock test results for a student preparing for {exam_type} aiming for {target}.

Mock Test Results/Errors:
{test_result_text}

Based on the errors and performance described, identify and list the KEY WEAK TOPICS (topics where the student needs improvement).

Return ONLY a JSON array of topic strings. Example:
["Thermodynamics", "Organic Chemistry", "Coordinate Geometry"]

Provide 3-7 most critical weak topics only. DO NOT wrap the output in markdown code blocks."""

    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Parse JSON array from response
        # Try to find JSON array in the response string
        start = response_text.find('[')
        end = response_text.rfind(']') + 1
        if start != -1 and end != 0:
            topics_json = response_text[start:end]
            weak_topics = json.loads(topics_json)
            return weak_topics if isinstance(weak_topics, list) else []
            
        # Fallback: try to extract topics from text
        lines = response_text.split('\n')
        topics = [line.strip().strip('`').strip('"').strip("'").strip('-').strip() 
                  for line in lines if line.strip() and not line.startswith('[') and not line.startswith(']')]
        return [t for t in topics if t and len(t) > 2][:7]
    except Exception as e:
        print(f"Error analyzing weak topics: {e}")
        # Default mock fallback if rate limits are hit
        return ["Physics: Kinematics", "Chemistry: Organic Reactions", "Math: Calculus"]

def generate_revision_plan(profile_data: dict, weak_topics: list, weekday_hours: float, weekend_hours: float) -> str:
    """
    Generate a personalized 7-day revision plan using Gemini.
    Returns structured JSON plan text.
    """
    exam_type = profile_data.get("exam_type", "")
    target = profile_data.get("target_marks_rank", "")
    topics_str = ", ".join(weak_topics)
    
    prompt = f"""You are an expert exam coach. Create a detailed 7-day revision timetable for a student.

Student Profile:
- Exam: {exam_type}
- Target: {target}
- Weak Topics: {topics_str}
- Weekday Study Hours: {weekday_hours} hours/day
- Weekend Study Hours: {weekend_hours} hours/day

Create a JSON response with this exact structure:
{{
    "plan": [
        {{
            "day": "Day 1",
            "subject": "Subject Name",
            "topic": "Topic Name",
            "time": "HH:MM - HH:MM",
            "focus": [
                "Focus point 1",
                "Focus point 2"
            ]
        }}
    ],
    "strategy": "Brief overall strategy",
    "tips": ["Tip 1", "Tip 2"]
}}

Make sure to:
1. Distribute topics evenly across 7 days
2. Place difficult topics in morning slots
3. Include 15-minute breaks after each 45-minute session
4. Vary subjects to prevent boredom
5. Allocate extra time to weakest topics"""

    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Strip markdown if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        elif response_text.startswith("```"):
            response_text = response_text[3:]
            
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            
        return response_text.strip()
    except Exception as e:
        print(f"Error generating revision plan: {e}")
        # Default plan fallback if rate limits are hit
        return json.dumps({
            "plan": [
                {
                    "day": "Day 1",
                    "subject": "Physics",
                    "topic": "Waves and Oscillations",
                    "time": "09:00 - 09:45",
                    "focus": [
                        "Fundamental concepts: Types of waves, wave equation",
                        "Speed of transverse and longitudinal waves"
                    ]
                },
                {
                    "day": "Day 1",
                    "subject": "Chemistry",
                    "topic": "Periodic Classification",
                    "time": "10:00 - 10:45",
                    "focus": [
                        "Modern Periodic Law and basic structure",
                        "Periodic trends: Atomic radius, ionic radius"
                    ]
                },
                {
                    "day": "Day 2",
                    "subject": "Mathematics",
                    "topic": "Calculus Foundations",
                    "time": "09:00 - 09:45",
                    "focus": [
                        "Limits and derivatives",
                        "Practice common differentiation rules"
                    ]
                },
                {
                    "day": "Day 3",
                    "subject": "Physics",
                    "topic": "Thermodynamics",
                    "time": "14:00 - 15:30",
                    "focus": [
                        "Laws of Thermodynamics",
                        "Heat engines and refrigerators"
                    ]
                },
                {
                    "day": "Day 4",
                    "subject": "Chemistry",
                    "topic": "Organic Chemistry",
                    "time": "16:00 - 18:00",
                    "focus": [
                        "Nomenclature and basic concepts",
                        "Isomerism in organic compounds"
                    ]
                },
                {
                    "day": "Day 5",
                    "subject": "Mathematics",
                    "topic": "Coordinate Geometry",
                    "time": "09:00 - 11:30",
                    "focus": [
                        "Straight lines and conic sections",
                        "Distance formula and section formula"
                    ]
                },
                {
                    "day": "Day 6",
                    "subject": "Mock Test",
                    "topic": "Full Syllabus Review",
                    "time": "10:00 - 13:00",
                    "focus": [
                        "Take a timed full-length mock test",
                        "Analyze mistakes and mark weak areas"
                    ]
                },
                {
                    "day": "Day 7",
                    "subject": "Revision",
                    "topic": "Weak Areas Focus",
                    "time": "14:00 - 17:00",
                    "focus": [
                        "Review all mistakes from Day 6 test",
                        "Re-read theory for identified weak spots"
                    ]
                }
            ],
            "strategy": "The AI is currently unavailable or busy. Here is a sample strategy to get you started.",
            "tips": ["Take short breaks", "Stay hydrated"]
        })

def answer_question(profile_data: dict, question: str, topic: str = None) -> str:
    """
    Answer a student's question using Gemini with exam-specific context.
    Returns a detailed, helpful answer.
    """
    exam_type = profile_data.get("exam_type", "")
    target = profile_data.get("target_marks_rank", "")
    
    topic_context = f"\nThe question relates to: {topic}" if topic else ""
    
    prompt = f"""You are an expert tutor preparing students for {exam_type} exams, aiming for {target} performance level.
    
Your role is to:
1. Answer questions clearly and concisely
2. Provide relevant formulas and concepts
3. Give practical tips and tricks for the exam
4. Highlight common mistakes to avoid
5. Use examples when helpful
6. Adapt complexity to the exam level

Student Question: {question}{topic_context}

Please provide a detailed, helpful answer."""

    response = model.generate_content(prompt)
    return response.text.strip()

def get_resource_recommendations(profile_data: dict, topic: str) -> str:
    """
    Get AI-recommended free resources for learning a topic.
    """
    exam_type = profile_data.get("exam_type", "")
    
    prompt = f"""You are helping a student preparing for {exam_type} exams learn about: {topic}

Recommend the best FREE learning resources for this topic. Include:
1. YouTube channels or videos (with channel/video names)
2. Online articles or blogs
3. Problem-solving websites
4. Free practice tests
5. Study tips specific to this topic

Format your response exactly as:
## Videos
- Resource name + brief description

## Articles/Blogs
- Resource name + link/source

## Practice Problems
- Resource name + description

## Study Tips
- Tip 1
- Tip 2

Make all recommendations specific and actionable."""

    response = model.generate_content(prompt)
    return response.text.strip()

def generate_practice_questions(profile_data: dict, topic: str, difficulty: str = "medium") -> str:
    """
    Generate practice questions for a specific topic.
    """
    exam_type = profile_data.get("exam_type", "")
    
    prompt = f"""You are creating practice questions for {exam_type} exam preparation.

Topic: {topic}
Difficulty Level: {difficulty}

Generate 3 practice problems for this topic at {difficulty} difficulty level.
Include:
1. The question clearly stated
2. Hint (if needed)
3. Solution with explanation
4. Key concept being tested

Format each question clearly with ### Question 1, ### Question 2, etc."""

    response = model.generate_content(prompt)
    return response.text.strip()

def analyze_common_mistakes(profile_data: dict, topic: str) -> str:
    """
    Identify and explain common mistakes students make in a topic.
    """
    exam_type = profile_data.get("exam_type", "")
    
    prompt = f"""You are an expert {exam_type} exam coach analyzing common student mistakes.

Topic: {topic}

List the 5 most common mistakes students make when solving problems related to {topic}.

For each mistake, provide:
1. The mistake description
2. Why students make this error
3. How to avoid it
4. Correct approach with example

Use clear, concise language."""

    response = model.generate_content(prompt)
    return response.text.strip()

def find_open_resources(profile_data: dict, topic: str) -> list:
    """
    Find open resources using Gemini and return them as a list of dictionaries matching FreeResource schema.
    """
    exam_type = profile_data.get("exam_type", "General")
    
    prompt = f"""You are helping a student preparing for {exam_type} exams find open learning resources for: {topic}

Provide exactly 3 high-quality, free online resources (like YouTube videos, articles, or practice sites).
Format the output STRICTLY as a JSON list of dictionaries with the following keys:
- "topic": "{topic}"
- "exam_type": "{exam_type}"
- "resource_type": "video" OR "article" OR "practice_test"
- "title": "Resource Title"
- "description": "Short description of what they will learn"
- "url": "A real, valid URL to the resource (e.g. https://www.youtube.com/results?search_query=...)"
- "difficulty_level": "beginner", "intermediate", or "advanced"
- "source": "Name of the creator/platform (e.g., Khan Academy, YouTube)"

Return ONLY the valid JSON array without markdown formatting blocking it."""

    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        import json
        start = response_text.find('[')
        end = response_text.rfind(']') + 1
        if start != -1 and end != 0:
            parsed = json.loads(response_text[start:end])
            if isinstance(parsed, list) and len(parsed) > 0:
                return parsed
    except Exception as e:
        print(f"Error generating resources: {e}")
        pass
        
    # User requested demo resources if nothing is found or parsing fails
    return [
        {
            "topic": topic,
            "exam_type": exam_type,
            "resource_type": "video",
            "title": f"Master {topic} in 10 Minutes",
            "description": f"A comprehensive quick review of {topic}.",
            "url": f"https://www.youtube.com/results?search_query={topic}+{exam_type}+tutorial",
            "difficulty_level": "beginner",
            "source": "Demo Video Series"
        },
        {
            "topic": topic,
            "exam_type": exam_type,
            "resource_type": "article",
            "title": f"Ultimate Guide to {topic}",
            "description": f"Detailed notes and formulas for {topic}.",
            "url": f"https://www.google.com/search?q={topic}+{exam_type}+notes+pdf",
            "difficulty_level": "intermediate",
            "source": "Demo Learning Notes"
        },
        {
            "topic": topic,
            "exam_type": exam_type,
            "resource_type": "practice_test",
            "title": f"{topic} Hard Practice Questions",
            "description": f"Test your knowledge with these advanced {topic} problems.",
            "url": f"https://www.google.com/search?q={topic}+{exam_type}+practice+questions",
            "difficulty_level": "advanced",
            "source": "Demo Practice Platform"
        }
    ]
