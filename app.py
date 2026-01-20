from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pickle
import sqlite3
from datetime import datetime
import string
import sys
import io

# Fix encoding issues for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

app = Flask(__name__)
CORS(app)

# Initialize database
def init_db():
    conn = sqlite3.connect('spam_detection.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS predictions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  message TEXT NOT NULL,
                  prediction TEXT NOT NULL,
                  confidence REAL,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

# Text preprocessing function
def preprocess_text(text):
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = ' '.join(text.split())
    return text

# Load model
try:
    with open('spam_model.pkl', 'rb') as f:
        model = pickle.load(f)
    with open('vectorizer.pkl', 'rb') as f:
        vectorizer = pickle.load(f)
    print("[SUCCESS] Model loaded successfully!")
except:
    print("[ERROR] Model not found! Please run 'python model_training.py' first")
    model = None
    vectorizer = None

init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        if model is None:
            return jsonify({'error': 'Model not trained. Run model_training.py first'}), 500
            
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Preprocess and predict
        processed_message = preprocess_text(message)
        vectorized_message = vectorizer.transform([processed_message])
        prediction = model.predict(vectorized_message)[0]
        confidence = model.predict_proba(vectorized_message)[0]
        
        confidence_score = float(max(confidence) * 100)
        
        # Save to database
        conn = sqlite3.connect('spam_detection.db')
        c = conn.cursor()
        c.execute('INSERT INTO predictions (message, prediction, confidence) VALUES (?, ?, ?)',
                  (message[:100], prediction, confidence_score))
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': message,
            'prediction': prediction,
            'confidence': confidence_score,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    try:
        conn = sqlite3.connect('spam_detection.db')
        c = conn.cursor()
        c.execute('SELECT * FROM predictions ORDER BY timestamp DESC LIMIT 50')
        results = c.fetchall()
        conn.close()
        
        history = []
        for row in results:
            history.append({
                'id': row[0],
                'message': row[1],
                'prediction': row[2],
                'confidence': row[3],
                'timestamp': row[4]
            })
        
        return jsonify({'history': history})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        conn = sqlite3.connect('spam_detection.db')
        c = conn.cursor()
        
        c.execute('SELECT COUNT(*) FROM predictions')
        total = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM predictions WHERE prediction = "spam"')
        spam_count = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM predictions WHERE prediction = "ham"')
        ham_count = c.fetchone()[0]
        
        c.execute('SELECT AVG(confidence) FROM predictions')
        avg_confidence = c.fetchone()[0] or 0
        
        conn.close()
        
        return jsonify({
            'total': total,
            'spam': spam_count,
            'ham': ham_count,
            'accuracy': 97.0,
            'avg_confidence': round(avg_confidence, 2)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear', methods=['DELETE'])
def clear_history():
    try:
        conn = sqlite3.connect('spam_detection.db')
        c = conn.cursor()
        c.execute('DELETE FROM predictions')
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'History cleared successfully'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("SPAM EMAIL DETECTION SYSTEM")
    print("="*60)
    print("\n[INFO] Server starting on http://127.0.0.1:8080")
    print("\nOpen your browser and go to: http://127.0.0.1:8080")
    print("\nPress CTRL+C to stop the server")
    print("="*60 + "\n")
    app.run(debug=True, port=8080)