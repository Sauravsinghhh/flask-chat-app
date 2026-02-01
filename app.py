from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import datetime
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Secret key for sessions

# In-memory storage
# Users: {username: {avatar: str, status: str}}
users = {
    "Alice": {"avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Alice", "status": "online"},
    "Bob": {"avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Bob", "status": "away"},
    "Charlie": {"avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Charlie", "status": "busy"},
    "David": {"avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=David", "status": "online"},
}

# Messages: List of {sender, recipient, content, timestamp}
messages = []

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('chat'))
    return render_template('login.html', available_users=users.keys())

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    if username:
        # If user doesn't exist, create a synthetic one
        if username not in users:
            users[username] = {
                "avatar": f"https://api.dicebear.com/7.x/avataaars/svg?seed={username}",
                "status": "online"
            }
        session['user'] = username
        return redirect(url_for('chat'))
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/chat')
def chat():
    if 'user' not in session:
        return redirect(url_for('index'))
    return render_template('chat.html', current_user=session['user'])

# API Endpoints for AJAX

@app.route('/api/users')
def get_users():
    if 'user' not in session:
        return jsonify([]), 401
    
    current_user = session['user']
    user_list = []
    for username, data in users.items():
        if username != current_user:
            user_list.append({
                "username": username,
                "avatar": data['avatar'],
                "status": data['status']
            })
    return jsonify(user_list)

@app.route('/api/messages/<partner>')
def get_messages(partner):
    if 'user' not in session:
        return jsonify([]), 401
    
    current_user = session['user']
    chat_history = []
    for msg in messages:
        if (msg['sender'] == current_user and msg['recipient'] == partner) or \
           (msg['sender'] == partner and msg['recipient'] == current_user):
            chat_history.append(msg)
    
    return jsonify(chat_history)

@app.route('/api/send', methods=['POST'])
def send_message():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    recipient = data.get('recipient')
    content = data.get('content')
    
    if not recipient or not content:
        return jsonify({"error": "Missing data"}), 400
    
    message = {
        "sender": session['user'],
        "recipient": recipient,
        "content": content,
        "timestamp": datetime.datetime.now().strftime("%H:%M")
    }
    messages.append(message)
    return jsonify({"status": "success", "message": message})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
