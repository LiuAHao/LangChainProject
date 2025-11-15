// 聊天机器人前端JavaScript代码
let sessionId = 'session_' + Date.now(); // 生成唯一的会话ID

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 显示会话ID
    document.getElementById('session-id').textContent = sessionId;
    
    // 绑定发送按钮事件
    document.getElementById('send-button').addEventListener('click', sendMessage);
    
    // 绑定输入框回车事件
    document.getElementById('user-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    // 绑定清空聊天记录按钮事件
    document.getElementById('clear-button').addEventListener('click', clearChatHistory);
});

// 发送消息函数
function sendMessage() {
    const userInput = document.getElementById('user-input');
    const message = userInput.value.trim();
    
    if (message === '') {
        return;
    }
    
    // 显示用户消息
    addMessageToChat('user', message);
    
    // 清空输入框
    userInput.value = '';
    
    // 禁用发送按钮并显示加载状态
    const sendButton = document.getElementById('send-button');
    sendButton.disabled = true;
    sendButton.textContent = '发送中...';
    
    // 显示加载提示
    const loadingElement = document.createElement('div');
    loadingElement.className = 'loading';
    loadingElement.id = 'loading';
    loadingElement.textContent = '正在思考...';
    document.querySelector('.chat-history').appendChild(loadingElement);
    scrollToBottom();
    
    // 发送请求到后端
    fetch('/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            session_id: sessionId,
            message: message
        })
    })
    .then(response => response.json())
    .then(data => {
        // 移除加载提示
        const loadingElement = document.getElementById('loading');
        if (loadingElement) {
            loadingElement.remove();
        }
        
        // 显示助手回复
        if (data.response) {
            addMessageToChat('assistant', data.response);
        } else {
            addMessageToChat('system', '抱歉，我没有收到回复。请稍后再试。');
        }
    })
    .catch(error => {
        // 移除加载提示
        const loadingElement = document.getElementById('loading');
        if (loadingElement) {
            loadingElement.remove();
        }
        
        console.error('Error:', error);
        addMessageToChat('system', '发生错误：' + error.message);
    })
    .finally(() => {
        // 重新启用发送按钮
        sendButton.disabled = false;
        sendButton.textContent = '发送';
    });
}

// 添加消息到聊天历史
function addMessageToChat(role, content) {
    const chatHistory = document.querySelector('.chat-history');
    const messageElement = document.createElement('div');
    messageElement.className = `message ${role}-message`;
    messageElement.textContent = content;
    chatHistory.appendChild(messageElement);
    scrollToBottom();
}

// 滚动到底部
function scrollToBottom() {
    const chatHistory = document.querySelector('.chat-history');
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

// 清空聊天记录
function clearChatHistory() {
    const chatHistory = document.querySelector('.chat-history');
    // 保留欢迎消息
    chatHistory.innerHTML = '<div class="message system-message">聊天记录已清空。</div>';
    setTimeout(() => {
        chatHistory.innerHTML = '<div class="message system-message">你好！我是你的 Qwen AI 助手，有什么我可以帮你的吗？</div>';
    }, 1000);
}