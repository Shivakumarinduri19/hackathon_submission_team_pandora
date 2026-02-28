import requests, json

payload = {
    'student_id': 1, 
    'test_result_text': json.dumps({
        'additional_questions': 15, 
        'questions': [{
            'question_id': 47, 
            'subject': 'Physics', 
            'difficulty': 'Medium', 
            'question': 'Frequency is the reciprocal of:', 
            'options': {'A': 'Wavelength', 'B': 'Velocity', 'C': 'Time period', 'D': 'Amplitude'}, 
            'correct_option': 'C', 'student_selected': 'A', 'is_correct': False
        }]
    })
}

try:
    r = requests.post('http://127.0.0.1:8000/api/analyze-test', json=payload)
    print(r.status_code)
    
    with open('error_log.txt', 'w') as f:
        f.write(r.text)
except Exception as e:
    print('Failed:', e)
