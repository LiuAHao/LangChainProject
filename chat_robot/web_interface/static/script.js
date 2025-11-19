// DeepSeek风格聊天机器人前端JavaScript代码
class ChatApp {
    constructor() {
        console.log('ChatApp 构造函数调用'); // 调试日志

        this.currentSessionId = null;
        this.currentPersonaId = null;
        this.sessions = []; // 明确初始化为空数组
        this.personas = []; // 明确初始化为空数组
        this.messages = [];
        this.settings = {
            aiProvider: 'local',
            modelName: 'qwen2.5:7b',
            temperature: 0.7,
            contextCompression: true,
            contextWindowSize: 10
        };

        // 新对话相关状态
        this.selectedPersonaId = null;

        console.log('初始状态:', {
            sessions: this.sessions,
            personas: this.personas
        }); // 调试日志

        this.init();
    }

    async init() {
        console.log('开始初始化应用...'); // 调试日志
        this.bindEvents();

        try {
            console.log('加载人设...'); // 调试日志
            await this.loadPersonas();
            console.log('人设加载完成，数量:', this.personas.length);

            console.log('加载会话...'); // 调试日志
            await this.loadSessions();
            console.log('会话加载完成，数量:', this.sessions.length);

            console.log('初始化对话...'); // 调试日志
            await this.initChat();

            console.log('更新UI...'); // 调试日志
            this.updateUI();

            console.log('应用初始化完成'); // 调试日志
        } catch (error) {
            console.error('初始化过程中出错:', error);
            this.showError('应用初始化失败: ' + error.message);
        }
    }

    bindEvents() {
        // 发送消息相关事件
        document.getElementById('send-button').addEventListener('click', () => this.sendMessage());
        document.getElementById('user-input').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // 自动调整输入框高度
        document.getElementById('user-input').addEventListener('input', (e) => {
            this.autoResizeTextarea(e.target);
            this.updateCharCount();
        });

        // 新对话按钮
        document.getElementById('new-chat-btn').addEventListener('click', () => this.openNewChatModal());

        // 侧边栏事件
        document.getElementById('settings-btn').addEventListener('click', () => this.openSettingsModal());

        // 顶部操作按钮
        document.getElementById('persona-btn').addEventListener('click', () => this.openPersonaModal());
        document.getElementById('clear-chat-btn').addEventListener('click', () => this.clearCurrentChat());
        document.getElementById('export-chat-btn').addEventListener('click', () => this.exportCurrentChat());

        // 模态框事件
        this.bindModalEvents();

        // 设置相关事件
        this.bindSettingsEvents();
    }

    bindModalEvents() {
        // 新对话模态框
        document.getElementById('close-new-chat-modal').addEventListener('click', () => this.closeNewChatModal());
        document.getElementById('cancel-new-chat').addEventListener('click', () => this.closeNewChatModal());
        document.getElementById('confirm-new-chat').addEventListener('click', () => this.createNewChat());

        // 人设选择模态框
        document.getElementById('close-persona-modal').addEventListener('click', () => this.closePersonaModal());
        document.getElementById('create-custom-persona').addEventListener('click', () => this.createCustomPersona());

        // 设置模态框
        document.getElementById('close-settings-modal').addEventListener('click', () => this.closeSettingsModal());

        // 点击背景关闭模态框
        document.getElementById('new-chat-modal').addEventListener('click', (e) => {
            if (e.target.id === 'new-chat-modal') this.closeNewChatModal();
        });
        document.getElementById('persona-modal').addEventListener('click', (e) => {
            if (e.target.id === 'persona-modal') this.closePersonaModal();
        });
        document.getElementById('settings-modal').addEventListener('click', (e) => {
            if (e.target.id === 'settings-modal') this.closeSettingsModal();
        });
    }

    bindSettingsEvents() {
        // AI提供商选择
        document.getElementById('model-selector').addEventListener('change', (e) => {
            this.settings.aiProvider = e.target.value;
        });

        // 设置模态框中的控件
        document.getElementById('ai-provider-select').addEventListener('change', (e) => {
            this.settings.aiProvider = e.target.value;
            this.saveSettings();
        });

        document.getElementById('model-name-input').addEventListener('change', (e) => {
            this.settings.modelName = e.target.value;
            this.saveSettings();
        });

        document.getElementById('temperature-slider').addEventListener('input', (e) => {
            this.settings.temperature = parseFloat(e.target.value);
            document.getElementById('temperature-value').textContent = e.target.value;
            this.saveSettings();
        });

        document.getElementById('context-compression-toggle').addEventListener('change', (e) => {
            this.settings.contextCompression = e.target.checked;
            this.saveSettings();
        });

        document.getElementById('context-window-size').addEventListener('change', (e) => {
            this.settings.contextWindowSize = parseInt(e.target.value);
            this.saveSettings();
        });
    }

    async loadPersonas() {
        try {
            const response = await fetch('/api/personas');
            this.personas = await response.json();
        } catch (error) {
            console.error('加载人设失败:', error);
        }
    }

    async loadSessions() {
        try {
            console.log('正在请求会话数据...');
            const response = await fetch('/api/sessions');

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const sessionsData = await response.json();
            console.log('原始会话数据:', sessionsData);

            // 确保数据是数组格式
            this.sessions = Array.isArray(sessionsData) ? sessionsData : [];
            console.log('处理后的会话数组:', this.sessions);
            console.log('会话数量:', this.sessions.length);

            // 打印每个会话的详细信息
            if (this.sessions.length > 0) {
                console.log('会话详情:');
                this.sessions.forEach((session, index) => {
                    console.log(`  ${index + 1}. Session ID: ${session.session_id}, Title: ${session.title}, Updated: ${session.updated_at}`);
                });
            }

        } catch (error) {
            console.error('加载会话失败:', error);
            this.sessions = []; // 确保出错时设置为空数组
            this.showError('加载会话列表失败: ' + error.message);
        }
    }

    openNewChatModal() {
        const modal = document.getElementById('new-chat-modal');
        this.selectedPersonaId = this.getDefaultPersonaId();

        // 清空表单
        document.getElementById('new-chat-title').value = '';

        // 渲染人设选择
        this.renderNewChatPersonaGrid();

        modal.classList.add('show');
    }

    closeNewChatModal() {
        const modal = document.getElementById('new-chat-modal');
        modal.classList.remove('show');
        this.selectedPersonaId = null;
    }

    async createNewChat() {
        const title = document.getElementById('new-chat-title').value.trim();
        const personaId = this.selectedPersonaId;

        if (!title) {
            this.showError('请输入对话名称');
            return;
        }

        if (!personaId) {
            this.showError('请选择AI人设');
            return;
        }

        try {
            const response = await fetch('/api/session', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: title,
                    persona_id: personaId
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            this.currentSessionId = data.session_id;
            this.currentPersonaId = personaId;
            this.messages = [];

            // 关闭模态框
            this.closeNewChatModal();

            // 重新加载会话列表
            await this.loadSessions();
            this.updateUI();

            this.showSuccess('对话创建成功');
        } catch (error) {
            console.error('创建新对话失败:', error);
            this.showError('创建新对话失败: ' + error.message);
        }
    }

    getDefaultPersonaId() {
        const defaultPersona = this.personas.find(p => p.is_default);
        return defaultPersona ? defaultPersona.id : (this.personas[0] ? this.personas[0].id : null);
    }

    async sendMessage() {
        const input = document.getElementById('user-input');
        const message = input.value.trim();

        if (!message || !this.currentSessionId) return;

        // 添加用户消息到界面
        this.addMessageToUI('user', message);
        input.value = '';
        this.autoResizeTextarea(input);
        this.updateCharCount();

        // 禁用发送按钮
        this.setSendButtonState(false);
        this.showLoadingIndicator(true);

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: this.currentSessionId,
                    message: message,
                    persona_id: this.currentPersonaId,
                    settings: this.settings
                })
            });

            const data = await response.json();

            if (data.response) {
                this.addMessageToUI('assistant', data.response);
            } else {
                this.showError('没有收到回复');
            }

            // 更新会话列表
            await this.loadSessions();
            this.updateChatList();

        } catch (error) {
            console.error('发送消息失败:', error);
            this.showError('发送消息失败: ' + error.message);
        } finally {
            this.setSendButtonState(true);
            this.showLoadingIndicator(false);
        }
    }

    addMessageToUI(role, content) {
        const messagesContainer = document.getElementById('messages-container');

        // 移除欢迎消息
        const welcomeMessage = messagesContainer.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }

        const messageElement = document.createElement('div');
        messageElement.className = `message ${role}`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = role === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';

        const contentElement = document.createElement('div');
        contentElement.className = 'message-content';

        const textElement = document.createElement('div');
        textElement.className = 'message-text';
        textElement.textContent = content;

        const timeElement = document.createElement('div');
        timeElement.className = 'message-time';
        timeElement.textContent = new Date().toLocaleTimeString();

        contentElement.appendChild(textElement);
        contentElement.appendChild(timeElement);

        messageElement.appendChild(avatar);
        messageElement.appendChild(contentElement);

        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        // 保存到本地消息数组
        this.messages.push({ role, content, timestamp: Date.now() });
    }

    setSendButtonState(enabled) {
        const sendButton = document.getElementById('send-button');
        sendButton.disabled = !enabled;
    }

    showLoadingIndicator(show) {
        const indicator = document.getElementById('loading-indicator');
        indicator.style.display = show ? 'flex' : 'none';
    }

    showError(message) {
        // 显示系统错误消息
        this.addMessageToUI('system', message);

        // 同时在页面顶部显示一个toast通知
        const toast = document.createElement('div');
        toast.className = 'error-toast';
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #ef4444;
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            z-index: 10000;
            max-width: 300px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        `;

        document.body.appendChild(toast);

        // 3秒后自动移除
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 3000);
    }

    autoResizeTextarea(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }

    updateCharCount() {
        const input = document.getElementById('user-input');
        const charCount = document.getElementById('char-count');
        const length = input.value.length;
        charCount.textContent = `${length} / 4000`;

        if (length > 4000) {
            charCount.style.color = '#ef4444';
        } else if (length > 3500) {
            charCount.style.color = '#f59e0b';
        } else {
            charCount.style.color = '#71717a';
        }
    }

    async initChat() {
        console.log('initChat 调用'); // 调试日志
        console.log('  - sessions 类型:', typeof this.sessions);
        console.log('  - sessions 值:', this.sessions);
        console.log('  - sessions 长度:', this.sessions?.length || 0);
        console.log('  - 是否为数组:', Array.isArray(this.sessions));

        // 确保sessions是数组
        if (!Array.isArray(this.sessions)) {
            console.warn('sessions 不是数组，重置为空数组');
            this.sessions = [];
        }

        // 如果有现有会话，加载第一个会话，否则打开新对话创建界面
        if (this.sessions.length > 0) {
            const firstSession = this.sessions[0];
            console.log('找到现有会话，切换到第一个会话:'); // 调试日志
            console.log('  - Session ID:', firstSession.session_id);
            console.log('  - Title:', firstSession.title);
            console.log('  - Updated At:', firstSession.updated_at);

            try {
                await this.switchToSession(firstSession.session_id);
                console.log('成功切换到现有会话');
            } catch (error) {
                console.error('切换到现有会话失败:', error);
                console.log('尝试打开新对话创建界面...');
                this.openNewChatModal();
            }
        } else {
            console.log('没有现有会话，打开新对话创建界面'); // 调试日志
            this.openNewChatModal();
        }
    }

    updateUI() {
        this.updateChatList();
        this.updatePersonaBadge();
        this.updateChatTitle();
    }

    updateChatList() {
        const chatList = document.getElementById('chat-list');
        chatList.innerHTML = '';

        this.sessions.forEach(session => {
            const chatItem = document.createElement('div');
            chatItem.className = `chat-item ${session.session_id === this.currentSessionId ? 'active' : ''}`;
            chatItem.addEventListener('click', () => this.switchToSession(session.session_id));

            const header = document.createElement('div');
            header.className = 'chat-item-header';

            const titleContainer = document.createElement('div');
            titleContainer.className = 'chat-item-title-container';

            const title = document.createElement('div');
            title.className = 'chat-item-title';
            title.textContent = session.title || '新对话';

            const persona = document.createElement('span');
            persona.className = 'chat-item-persona-tag';
            persona.textContent = session.persona_name || '通用助手';

            titleContainer.appendChild(title);
            titleContainer.appendChild(persona);

            const time = document.createElement('div');
            time.className = 'chat-item-time';
            time.textContent = this.formatTime(session.updated_at);

            header.appendChild(titleContainer);
            header.appendChild(time);

            // 获取最近两条消息作为预览
            const preview = document.createElement('div');
            preview.className = 'chat-item-preview';
            this.loadLastMessagesPreview(session.session_id, preview);

            chatItem.appendChild(header);
            chatItem.appendChild(preview);
            chatList.appendChild(chatItem);
        });
    }

    updatePersonaBadge() {
        const currentPersona = this.personas.find(p => p.id == this.currentPersonaId);
        if (currentPersona) {
            document.getElementById('current-persona-name').textContent = currentPersona.name;
        }
    }

    updateChatTitle() {
        const currentSession = this.sessions.find(s => s.session_id === this.currentSessionId);
        const titleElement = document.querySelector('.title-text');
        if (currentSession && currentSession.title) {
            titleElement.textContent = currentSession.title;
        } else {
            titleElement.textContent = '新对话';
        }
    }

    async loadLastMessagesPreview(sessionId, previewElement) {
        try {
            const response = await fetch(`/api/history/${sessionId}`);
            if (response.ok) {
                const data = await response.json();
                const messages = Array.isArray(data.messages) ? data.messages : [];

                if (messages.length === 0) {
                    previewElement.textContent = '暂无消息';
                    return;
                }

                // 获取最近两条消息
                const lastMessages = messages.slice(-2);
                const previewText = lastMessages
                    .map(msg => {
                        const role = msg.role === 'user' ? '用户' : 'AI';
                        const content = msg.content.length > 30
                            ? msg.content.substring(0, 30) + '...'
                            : msg.content;
                        return `${role}: ${content}`;
                    })
                    .join('\n');

                previewElement.textContent = previewText;
            } else {
                previewElement.textContent = '暂无消息';
            }
        } catch (error) {
            console.error('加载消息预览失败:', error);
            previewElement.textContent = '暂无消息';
        }
    }

    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return '刚刚';
        if (diffMins < 60) return `${diffMins}分钟前`;
        if (diffHours < 24) return `${diffHours}小时前`;
        if (diffDays < 7) return `${diffDays}天前`;

        return date.toLocaleDateString();
    }

    async switchToSession(sessionId) {
        console.log('切换到会话:', sessionId);
        this.currentSessionId = sessionId;

        // 加载会话消息
        try {
            console.log('正在加载会话历史...');
            const response = await fetch(`/api/history/${sessionId}`);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            console.log('会话历史数据:', data);

            this.messages = Array.isArray(data.messages) ? data.messages : [];
            console.log('加载到', this.messages.length, '条消息');

            this.renderMessages();

            // 更新当前人设
            const session = this.sessions.find(s => s.session_id === sessionId);
            if (session) {
                console.log('当前会话信息:', session);
                if (session.persona_id) {
                    this.currentPersonaId = session.persona_id;
                    console.log('更新当前人设ID:', this.currentPersonaId);
                }
            }

            this.updateUI();
            console.log('会话切换完成');
        } catch (error) {
            console.error('切换会话失败:', error);
            this.showError('切换会话失败: ' + error.message);
            // 清空当前会话ID，防止状态不一致
            this.currentSessionId = null;
        }
    }

    renderMessages() {
        const messagesContainer = document.getElementById('messages-container');
        messagesContainer.innerHTML = '';

        if (this.messages.length === 0) {
            // 显示欢迎消息
            const welcomeMessage = document.createElement('div');
            welcomeMessage.className = 'welcome-message';
            welcomeMessage.innerHTML = `
                <div class="welcome-icon">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="welcome-text">
                    <h2>你好！我是 Qwen AI 助手</h2>
                    <p>我可以帮助你回答问题、编写代码、创意写作等。选择一个人设开始我们的对话吧！</p>
                </div>
            `;
            messagesContainer.appendChild(welcomeMessage);
        } else {
            this.messages.forEach(msg => {
                this.addMessageToUI(msg.role, msg.content);
            });
        }
    }

    openPersonaModal() {
        const modal = document.getElementById('persona-modal');
        this.renderPersonaGrid();
        modal.classList.add('show');
    }

    closePersonaModal() {
        const modal = document.getElementById('persona-modal');
        modal.classList.remove('show');
    }

    renderPersonaGrid() {
        const grid = document.getElementById('persona-grid');
        grid.innerHTML = '';

        this.personas.forEach(persona => {
            const card = document.createElement('div');
            card.className = `persona-card ${persona.id == this.currentPersonaId ? 'selected' : ''}`;
            card.addEventListener('click', () => this.selectPersona(persona.id));

            card.innerHTML = `
                <div class="persona-name">${persona.name}</div>
                <div class="persona-description">${persona.description}</div>
                <div class="persona-prompt">${persona.system_prompt}</div>
            `;

            grid.appendChild(card);
        });
    }

    renderNewChatPersonaGrid() {
        const grid = document.getElementById('new-chat-persona-grid');
        grid.innerHTML = '';

        this.personas.forEach(persona => {
            const card = document.createElement('div');
            card.className = `persona-card ${persona.id == this.selectedPersonaId ? 'selected' : ''}`;
            card.addEventListener('click', () => this.selectPersonaForNewChat(persona.id));

            card.innerHTML = `
                <div class="persona-name">${persona.name}</div>
                <div class="persona-description">${persona.description}</div>
                <div class="persona-prompt">${persona.system_prompt}</div>
            `;

            grid.appendChild(card);
        });
    }

    selectPersonaForNewChat(personaId) {
        this.selectedPersonaId = personaId;
        this.renderNewChatPersonaGrid();
    }

    async selectPersona(personaId) {
        this.currentPersonaId = personaId;

        // 更新当前会话的人设
        if (this.currentSessionId) {
            try {
                const response = await fetch(`/api/session/${this.currentSessionId}/persona`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ persona_id: personaId })
                });

                if (response.ok) {
                    const data = await response.json();
                    // 更新会话列表中的人设信息
                    await this.loadSessions();
                    this.updateChatList();
                    console.log('人设更新成功:', data);
                } else {
                    const errorData = await response.json();
                    console.error('更新会话人设失败:', errorData.detail);
                    this.showError('更新人设失败: ' + errorData.detail);
                }
            } catch (error) {
                console.error('更新会话人设失败:', error);
                this.showError('更新人设失败: ' + error.message);
            }
        }

        this.updatePersonaBadge();
        this.closePersonaModal();
        this.renderPersonaGrid(); // 更新选中状态
    }

    async createCustomPersona() {
        const name = document.getElementById('custom-persona-name').value.trim();
        const prompt = document.getElementById('custom-persona-prompt').value.trim();

        if (!name || !prompt) {
            this.showError('请填写人设名称和系统提示词');
            return;
        }

        try {
            const response = await fetch('/api/personas', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: name,
                    description: `自定义人设: ${name}`,
                    system_prompt: prompt
                })
            });

            if (response.ok) {
                await this.loadPersonas();
                document.getElementById('custom-persona-name').value = '';
                document.getElementById('custom-persona-prompt').value = '';
                this.renderPersonaGrid();
                this.showSuccess('人设创建成功');
            } else {
                this.showError('创建人设失败');
            }
        } catch (error) {
            console.error('创建人设失败:', error);
            this.showError('创建人设失败: ' + error.message);
        }
    }

    openSettingsModal() {
        const modal = document.getElementById('settings-modal');
        this.loadSettingsToModal();
        modal.classList.add('show');
    }

    closeSettingsModal() {
        const modal = document.getElementById('settings-modal');
        modal.classList.remove('show');
    }

    loadSettingsToModal() {
        document.getElementById('ai-provider-select').value = this.settings.aiProvider;
        document.getElementById('model-name-input').value = this.settings.modelName;
        document.getElementById('temperature-slider').value = this.settings.temperature;
        document.getElementById('temperature-value').textContent = this.settings.temperature;
        document.getElementById('context-compression-toggle').checked = this.settings.contextCompression;
        document.getElementById('context-window-size').value = this.settings.contextWindowSize;
    }

    async saveSettings() {
        try {
            await fetch('/api/settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(this.settings)
            });
        } catch (error) {
            console.error('保存设置失败:', error);
        }
    }

    async clearCurrentChat() {
        if (!this.currentSessionId) return;

        if (confirm('确定要清空当前对话吗？此操作不可撤销。')) {
            try {
                await fetch(`/api/session/${this.currentSessionId}/clear`, {
                    method: 'DELETE'
                });

                this.messages = [];
                this.renderMessages();
                this.showSuccess('对话已清空');
            } catch (error) {
                console.error('清空对话失败:', error);
                this.showError('清空对话失败');
            }
        }
    }

    exportCurrentChat() {
        if (this.messages.length === 0) {
            this.showError('没有可导出的对话');
            return;
        }

        const currentPersona = this.personas.find(p => p.id == this.currentPersonaId);
        const content = `对话导出
时间: ${new Date().toLocaleString()}
人设: ${currentPersona ? currentPersona.name : '未知'}

` +
            this.messages.map(msg => `${msg.role === 'user' ? '用户' : 'AI'}: ${msg.content}`).join('\n\n');

        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `chat_export_${new Date().getTime()}.txt`;
        a.click();
        URL.revokeObjectURL(url);
    }

    showSuccess(message) {
        // 在页面顶部显示一个成功toast通知
        const toast = document.createElement('div');
        toast.className = 'success-toast';
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #22c55e;
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            z-index: 10000;
            max-width: 300px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        `;

        document.body.appendChild(toast);

        // 2秒后自动移除
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 2000);
    }
}

// 初始化应用
let app;
document.addEventListener('DOMContentLoaded', function() {
    app = new ChatApp();
});