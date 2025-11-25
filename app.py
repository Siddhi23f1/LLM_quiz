from flask import Flask, request, jsonify
import os
from quiz_solver import QuizSolver

app = Flask(__name__)

# Load from environment variables
EMAIL = os.getenv('STUDENT_EMAIL', 'your-email@example.com')
SECRET = os.getenv('STUDENT_SECRET', 'your-secret-string')

solver = QuizSolver(EMAIL, SECRET)

@app.route('/quiz', methods=['POST'])
def handle_quiz():
    try:
        data = request.get_json()
        
        # Validate JSON
        if not data:
            return jsonify({'error': 'Invalid JSON'}), 400
        
        # Verify secret
        if data.get('secret') != SECRET:
            return jsonify({'error': 'Invalid secret'}), 403
        
        # Verify email
        if data.get('email') != EMAIL:
            return jsonify({'error': 'Email mismatch'}), 403
        
        # Get quiz URL
        quiz_url = data.get('url')
        if not quiz_url:
            return jsonify({'error': 'No URL provided'}), 400
        
        # Start solving quiz chain
        solver.solve_quiz_chain(quiz_url)
        
        return jsonify({
            'status': 'started',
            'message': 'Quiz solving initiated'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
