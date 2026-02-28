"""
LLM helpers for the 3 new features:
  1. Multi-sheet error pattern analysis
  2. AI reply in discussions
"""
import json
import google.generativeai as genai
import os

# Re-use the same Gemini setup from llm_enhanced
genai.configure(api_key=os.getenv("GEMINI_API_KEY", "AIzaSyC41bKOSH6T8y1DAW1GcufBEz-iLdyM-lA"))
model = genai.GenerativeModel('gemini-2.5-flash')


def analyze_error_patterns_across_sheets(profile_data: dict, sheets_data: list) -> list:
    """
    Given a list of test sheet texts, find recurring error patterns.
    Returns a list of ErrorPattern dicts.
    sheets_data: [{"file_name": "...", "raw_text": "...", "score": 70}, ...]
    """
    exam_type = profile_data.get("exam_type", "")
    target    = profile_data.get("target_marks_rank", "")

    combined = ""
    for i, sheet in enumerate(sheets_data, 1):
        combined += f"\n--- Sheet {i}: {sheet.get('file_name','Untitled')} (Score: {sheet.get('score','N/A')}) ---\n"
        combined += sheet.get("raw_text", "")[:2000]   # cap per sheet

    prompt = f"""You are an expert {exam_type} exam coach doing a deep error-pattern analysis.

Student Target: {target}
Exam: {exam_type}

Below are results from {len(sheets_data)} mock test sheets:
{combined}

Identify the TOP recurring error patterns across these sheets. For each pattern return:
- topic: which topic it belongs to
- error_type: one of [conceptual, calculation, silly, time_based]
- frequency: how many times this type of error appears (integer)
- description: what the student keeps doing wrong (1-2 sentences)
- suggestion: specific actionable fix (1-2 sentences)
- severity: one of [low, medium, high]

Return ONLY a valid JSON array. No markdown. Example:
[
  {{
    "topic": "Thermodynamics",
    "error_type": "conceptual",
    "frequency": 4,
    "description": "Student confuses isothermal and adiabatic processes.",
    "suggestion": "Revise PV diagrams and practice distinguishing the two processes with 10 examples.",
    "severity": "high"
  }}
]
Provide 5-8 patterns max."""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        start = text.find('[')
        end   = text.rfind(']') + 1
        if start != -1 and end > 0:
            return json.loads(text[start:end])
    except Exception as e:
        print(f"Error in analyze_error_patterns: {e}")

    # Fallback
    return [
        {
            "topic": "General",
            "error_type": "calculation",
            "frequency": 3,
            "description": "Recurring arithmetic errors under time pressure.",
            "suggestion": "Practice mental math drills daily for 10 minutes.",
            "severity": "medium"
        }
    ]


def generate_ai_discussion_reply(profile_data: dict, post_title: str, post_content: str, exam_tag: str) -> str:
    """
    Generate an AI reply for a student's discussion post.
    """
    exam_type = exam_tag or profile_data.get("exam_type", "competitive exam")

    prompt = f"""You are a helpful senior student and {exam_type} expert on a peer study forum.

A student posted the following question/problem:

Title: {post_title}
Content: {post_content}

Provide a clear, helpful, and encouraging reply. Include:
- Direct answer or approach to the problem
- Step-by-step explanation if it's a concept/calculation
- A practical tip or common mistake to avoid
- Keep it friendly and concise (under 300 words)

Do NOT start with "As an AI" or similar disclaimers."""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating AI reply: {e}")
        return "Great question! Unfortunately the AI tutor is busy right now. Another student will reply soon. In the meantime, try searching for this topic in the Resources section."


def extract_text_from_content(raw_content: str, file_type: str) -> str:
    """
    For text/csv uploads, just return as-is.
    For structured content, ask Gemini to extract meaningful test data.
    """
    if file_type in ("text", "csv"):
        return raw_content[:5000]

    prompt = f"""The following is content extracted from a student's mock test sheet (file type: {file_type}).
Extract and summarise the key information: questions attempted, topics covered, correct/incorrect answers, scores.
Keep it under 500 words and focus on what was wrong.

Content:
{raw_content[:3000]}"""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return raw_content[:3000]
