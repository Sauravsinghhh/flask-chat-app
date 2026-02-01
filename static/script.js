document.addEventListener('DOMContentLoaded', () => {
    const userListEl = document.getElementById('userList');
    const chatPartnerNameEl = document.getElementById('chatPartnerName');
    const messagesContainer = document.getElementById('messagesContainer');
    const emptyState = document.getElementById('emptyState');
    const chatInputArea = document.getElementById('chatInputArea');
    const messageInput = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');

    let selectedUser = null;
    let pollInterval = null;

    // Fetch initial user list
    fetchUsers();
    
    // Poll for users occasionally
    setInterval(fetchUsers, 5000);

    // Poll for messages frequently
    setInterval(() => {
        if (selectedUser) {
            fetchMessages(selectedUser, false); // false = don't scroll unless new message
        }
    }, 1500);

    function fetchUsers() {
        fetch('/api/users')
            .then(res => res.json())
            .then(users => {
                renderUserList(users);
            })
            .catch(err => console.error('Error fetching users:', err));
    }

    function renderUserList(users) {
        userListEl.innerHTML = '';
        users.forEach(user => {
            const div = document.createElement('div');
            div.className = `user-item ${selectedUser === user.username ? 'active' : ''}`;
            div.onclick = () => selectUser(user);
            div.innerHTML = `
                <img src="${user.avatar}" class="user-avatar" alt="${user.username}">
                <div class="user-info">
                    <h4>${user.username}</h4>
                    <span class="user-status"><span class="status-dot ${user.status === 'online' ? '' : 'away'}"></span>${user.status}</span>
                </div>
            `;
            userListEl.appendChild(div);
        });
    }

    function selectUser(user) {
        if (selectedUser === user.username) return;
        
        selectedUser = user.username;
        chatPartnerNameEl.textContent = user.username;
        
        // UI Updates
        emptyState.classList.add('hidden');
        messagesContainer.classList.remove('hidden');
        chatInputArea.classList.add('visible');
        
        // Highlight active user
        document.querySelectorAll('.user-item').forEach(el => el.classList.remove('active'));
        fetchUsers(); // Re-render to show active state immediately

        // Clear messages and load new history
        messagesContainer.innerHTML = '';
        fetchMessages(selectedUser, true);
        
        // Focus input
        messageInput.focus();
    }

    async function fetchMessages(partner, forceScroll) {
        try {
            const res = await fetch(`/api/messages/${partner}`);
            const messages = await res.json();
            renderMessages(messages, forceScroll);
        } catch (err) {
            console.error(err);
        }
    }

    function renderMessages(messages, forceScroll) {
        // Simple optimization: only re-render if count changes or it's a force refresh
        // For a real app, we'd use IDs to only append new ones, but this is a prototype
        
        const currentCount = messagesContainer.childElementCount;
        if (!forceScroll && messages.length === currentCount) return;

        messagesContainer.innerHTML = '';
        messages.forEach(msg => {
            const div = document.createElement('div');
            div.className = `message ${msg.sender === CURRENT_USER ? 'sent' : 'received'}`;
            div.innerHTML = `
                ${msg.content}
                <span class="message-time">${msg.timestamp}</span>
            `;
            messagesContainer.appendChild(div);
        });

        if (forceScroll || messages.length > currentCount) {
            scrollToBottom();
        }
    }

    function scrollToBottom() {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // Send Message Logic
    function sendMessage() {
        const content = messageInput.value.trim();
        if (!content || !selectedUser) return;

        // Optimistic UI update
        const tempMsg = {
            sender: CURRENT_USER,
            content: content,
            timestamp: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
        };
        
        // Send to backend
        fetch('/api/send', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                recipient: selectedUser,
                content: content
            })
        })
        .then(res => res.json())
        .then(data => {
            messageInput.value = '';
            fetchMessages(selectedUser, true);
        });
    }

    sendBtn.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
});
