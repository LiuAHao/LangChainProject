// DeepSeek风格聊天机器人前端JavaScript代码
class ChatApp {
    constructor() {
        console.log('ChatApp 构造函数调用'); // 调试日志

        this.currentSessionId = null;
        this.currentPersonaId = null;
        this.sessions = []; // 明确初始化为空数组
        this.personas = []; // 明确初始化为空数组
        this.messages = [];
        this.frontendConfig = {}; // 前端配置
        this.settings = {
            aiProvider: 'local',
            modelName: 'qwen2.5:7b',
            temperature: 0.7,
            contextCompression: true,
            contextWindowSize: 10
        };

        // 新对话相关状态
        this.selectedPersonaId = null;

        // 删除会话相关状态
        this.sessionToDelete = null;
        this.sessionTitleToDelete = null;

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
            console.log('加载前端配置...'); // 调试日志
            await this.loadFrontendConfig();

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

        // 人设优化按钮 - 新对话模态框
        document.getElementById('optimize-persona-btn')?.addEventListener('click', () => {
            this.optimizePersonaDescription('new-chat');
        });

        // 添加人设名称实时重复检查
        document.getElementById('custom-persona-name')?.addEventListener('input', (e) => {
            this.checkPersonaNameAvailability(e.target.value, 'new-chat');
        });

        document.getElementById('custom-persona-name-persona-modal')?.addEventListener('input', (e) => {
            this.checkPersonaNameAvailability(e.target.value, 'persona-modal');
        });

        // 人设选择模态框
        document.getElementById('close-persona-modal').addEventListener('click', () => this.closePersonaModal());
        document.getElementById('create-custom-persona-persona-modal')?.addEventListener('click', () => this.createCustomPersona('persona-modal'));

        // 人设优化按钮 - 人设选择模态框
        document.getElementById('optimize-persona-btn-persona-modal')?.addEventListener('click', () => {
            this.optimizePersonaDescription('persona-modal');
        });

        // 设置模态框
        document.getElementById('close-settings-modal').addEventListener('click', () => this.closeSettingsModal());

        // 删除确认模态框
        document.getElementById('cancel-delete').addEventListener('click', () => this.closeDeleteConfirmModal());
        document.getElementById('confirm-delete').addEventListener('click', () => this.deleteCurrentSession());

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
        document.getElementById('confirm-delete-modal').addEventListener('click', (e) => {
            if (e.target.id === 'confirm-delete-modal') this.closeDeleteConfirmModal();
        });
    }

    bindSettingsEvents() {
        // AI提供商选择（侧边栏）
        document.getElementById('model-selector').addEventListener('change', (e) => {
            this.settings.aiProvider = e.target.value;
        });

        // 设置模态框中的控件
        document.getElementById('context-compression-toggle').addEventListener('change', (e) => {
            this.settings.contextCompression = e.target.checked;
            this.updateFrontendConfig({
                chat: {
                    enableCompression: e.target.checked
                }
            });
        });

        document.getElementById('context-window-size').addEventListener('change', (e) => {
            this.settings.contextWindowSize = parseInt(e.target.value);
            this.updateFrontendConfig({
                chat: {
                    contextWindowSize: parseInt(e.target.value)
                }
            });
        });

        // 界面设置
        document.getElementById('enable-animations-toggle')?.addEventListener('change', (e) => {
            this.updateFrontendConfig({
                ui: {
                    enableAnimations: e.target.checked
                }
            });
            this.applyAnimationsSetting(e.target.checked);
        });

        document.getElementById('show-timestamps-toggle')?.addEventListener('change', (e) => {
            this.updateFrontendConfig({
                ui: {
                    showTimestamps: e.target.checked
                }
            });
            this.applyTimestampsSetting(e.target.checked);
        });

        document.getElementById('max-message-length')?.addEventListener('change', (e) => {
            const maxLength = parseInt(e.target.value);
            this.updateFrontendConfig({
                ui: {
                    maxMessageLength: maxLength
                }
            });
            this.updateCharCountLimit(maxLength);
        });
    }

    async loadFrontendConfig() {
        try {
            const response = await fetch('/api/frontend-config');
            this.frontendConfig = await response.json();
            console.log('前端配置加载完成:', this.frontendConfig);
        } catch (error) {
            console.error('加载前端配置失败:', error);
            // 使用默认配置
            this.frontendConfig = {
                ui: {
                    maxMessageLength: 4000,
                    autoScroll: true,
                    showTimestamps: true
                },
                chat: {
                    contextWindowSize: 10,
                    temperature: 0.7,
                    enableCompression: true
                }
            };
        }
    }

    async updateFrontendConfig(configUpdates) {
        try {
            const response = await fetch('/api/frontend-config', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(configUpdates)
            });

            if (response.ok) {
                const data = await response.json();
                this.frontendConfig = data.config;
                return true;
            }
            return false;
        } catch (error) {
            console.error('更新前端配置失败:', error);
            return false;
        }
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
                    console.log(`  ${index + 1}. Session ID: ${session.session_id}, Title: ${session.title}, Persona ID: ${session.persona_id}, Persona Name: ${session.persona_name}, Updated: ${session.updated_at}`);
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
            chatItem.style.position = 'relative'; // 为删除按钮定位

            // 整个会话项都可以点击切换会话
            chatItem.addEventListener('click', () => this.switchToSession(session.session_id));

            const header = document.createElement('div');
            header.className = 'chat-item-header';

            // --- 左侧标题 ---
            const title = document.createElement('span');
            title.className = 'chat-item-title';
            // 确保标题是字符串类型
            title.textContent = (session.title && typeof session.title === 'string') ? session.title : '新对话';

            // --- 中间人设标签 ---
            // 查找人设名称逻辑：先看session里有没有，没有就去personas数组里找
            let personaName = session.persona_name;
            if ((!personaName || typeof personaName !== 'string') && session.persona_id) {
                const personaObj = this.personas.find(p => p.id === session.persona_id);
                if (personaObj && personaObj.name) personaName = personaObj.name;
            }
            
            const persona = document.createElement('span');
            persona.className = 'chat-item-persona-tag';
            // 确保人设名称是字符串类型，并且不是日期字符串
            persona.textContent = (personaName && typeof personaName === 'string' && !personaName.includes('datetime')) ? personaName : '通用助手';

            // --- 右侧时间 ---
            const time = document.createElement('div');
            time.className = 'chat-item-time';
            // 使用 updated_at 或 created_at，根据你的需求
            const timestamp = session.updated_at || session.created_at;
            time.textContent = timestamp ? this.formatTime(timestamp) : '';

            // 确保元素按正确顺序添加
            header.appendChild(title);
            header.appendChild(persona);
            header.appendChild(time);

            // 获取最近两条消息作为预览
            const preview = document.createElement('div');
            preview.className = 'chat-item-preview';
            this.loadLastMessagesPreview(session.session_id, preview);

            // 添加删除按钮到右上角
            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'chat-item-delete-btn';
            deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
            deleteBtn.title = '删除会话';
            deleteBtn.addEventListener('click', (e) => {
                e.stopPropagation(); // 阻止事件冒泡，防止触发会话切换
                this.confirmDeleteSession(session.session_id, session.title || '未命名会话');
            });

            chatItem.appendChild(header);
            chatItem.appendChild(preview);
            chatItem.appendChild(deleteBtn);
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
        if (!timestamp) return '';
        const date = new Date(timestamp);
        const now = new Date();

        // 补零辅助函数
        const pad = (n) => n.toString().padStart(2, '0');
        
        const month = pad(date.getMonth() + 1);
        const day = pad(date.getDate());
        const hours = pad(date.getHours());
        const minutes = pad(date.getMinutes());

        // 如果是今天的消息，只显示时间 HH:mm
        if (date.toDateString() === now.toDateString()) {
            return `${hours}:${minutes}`;
        }
        
        // 否则显示日期 MM-DD
        // 如果你需要完整的 YYYY-MM-DD HH:mm，可以直接返回:
        // return `${date.getFullYear()}-${month}-${day} ${hours}:${minutes}`;
        
        return `${month}-${day}`;
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

                    // 确保人设名称存在
                    if (!session.persona_name && session.persona_id) {
                        const personaObj = this.personas.find(p => p.id === session.persona_id);
                        if (personaObj) {
                            session.persona_name = personaObj.name;
                        }
                    }
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
                    console.log('人设更新成功:', data);

                    // 更新当前会话在sessions数组中的人设信息
                    const currentSession = this.sessions.find(s => s.session_id === this.currentSessionId);
                    if (currentSession) {
                        currentSession.persona_id = personaId;
                        // 如果返回了persona信息，更新persona_name
                        if (data.persona) {
                            currentSession.persona_name = data.persona.name;
                        } else {
                            // 如果没有返回persona信息，从personas数组中查找
                            const personaObj = this.personas.find(p => p.id === personaId);
                            if (personaObj) {
                                currentSession.persona_name = personaObj.name;
                            }
                        }
                    }

                    // 直接更新聊天列表，不需要重新加载所有会话
                    this.updateChatList();
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

    async optimizePersonaDescription(modalType) {
        const nameInput = modalType === 'new-chat'
            ? document.getElementById('custom-persona-name')
            : document.getElementById('custom-persona-name-persona-modal');

        const optimizeBtn = modalType === 'new-chat'
            ? document.getElementById('optimize-persona-btn')
            : document.getElementById('optimize-persona-btn-persona-modal');

        const personaName = nameInput.value.trim();

        if (!personaName) {
            this.showError('请先输入人设名称');
            return;
        }

        // 显示加载状态
        optimizeBtn.disabled = true;
        optimizeBtn.classList.add('optimizing');
        optimizeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

        try {
            const response = await fetch('/api/personas/optimize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: personaName })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            if (data.success && data.optimized_content) {
                // 尝试解析JSON格式的优化结果
                let optimizedData;
                try {
                    optimizedData = JSON.parse(data.optimized_content);

                    // 处理system_prompt是对象的情况
                    if (optimizedData.system_prompt && typeof optimizedData.system_prompt === 'object') {
                        const promptParts = [];
                        for (const [key, value] of Object.entries(optimizedData.system_prompt)) {
                            promptParts.push(`${key}：${value}`);
                        }
                        optimizedData.system_prompt = promptParts.join('\n');
                    }
                } catch (e) {
                    console.warn('JSON解析失败，使用原始内容:', e);
                    // 如果解析失败，将整个内容作为system_prompt
                    optimizedData = {
                        description: `优化的人设: ${personaName}`,
                        system_prompt: data.optimized_content
                    };
                }

                // 确保有system_prompt
                if (!optimizedData.system_prompt) {
                    optimizedData.system_prompt = `你是${personaName}，一个专业的AI助手。`;
                }

                // 填充到对应的textarea
                const promptTextarea = modalType === 'new-chat'
                    ? document.getElementById('custom-persona-prompt')
                    : document.getElementById('custom-persona-prompt-persona-modal');

                if (promptTextarea && optimizedData.system_prompt) {
                    promptTextarea.value = optimizedData.system_prompt;
                    console.log('优化的人设描述:', optimizedData.system_prompt);
                }

                this.showSuccess('人设描述优化成功');
            } else {
                this.showError('优化失败，请重试');
            }
        } catch (error) {
            console.error('优化人设失败:', error);
            this.showError('优化人设失败: ' + error.message);
        } finally {
            // 恢复按钮状态
            optimizeBtn.disabled = false;
            optimizeBtn.classList.remove('optimizing');
            optimizeBtn.innerHTML = '<i class="fas fa-magic"></i>';
        }
    }

  async createCustomPersona(modalType = 'new-chat') {
        const nameInput = modalType === 'new-chat'
            ? document.getElementById('custom-persona-name')
            : document.getElementById('custom-persona-name-persona-modal');
        const promptTextarea = modalType === 'new-chat'
            ? document.getElementById('custom-persona-prompt')
            : document.getElementById('custom-persona-prompt-persona-modal');

        const name = nameInput.value.trim();
        const prompt = promptTextarea.value.trim();

        if (!name || !prompt) {
            this.showError('请填写人设名称和系统提示词');
            return;
        }

        // 前端检查是否已存在同名人设
        const existingPersona = this.personas.find(p => p.name === name);
        if (existingPersona) {
            this.showError(`人设名称 "${name}" 已存在，请使用不同的名称`);
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
                nameInput.value = '';
                promptTextarea.value = '';

                // 刷新对应的人设网格
                if (modalType === 'new-chat') {
                    this.renderNewChatPersonaGrid();
                } else {
                    this.renderPersonaGrid();
                }

                this.showSuccess('人设创建成功');
            } else {
                // 处理特定的HTTP状态码
                const errorData = await response.json().catch(() => ({}));

                if (response.status === 409) {
                    // 409 Conflict - 人设名称已存在
                    this.showError(errorData.detail || '人设名称已存在，请使用不同的名称');
                } else {
                    this.showError(errorData.detail || '创建人设失败');
                }
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
        // 使用前端配置更新界面
        if (this.frontendConfig.chat) {
            document.getElementById('context-compression-toggle').checked = this.frontendConfig.chat.enableCompression !== false;
            document.getElementById('context-window-size').value = this.frontendConfig.chat.contextWindowSize || 10;
        }

        if (this.frontendConfig.ui) {
            document.getElementById('enable-animations-toggle') && (document.getElementById('enable-animations-toggle').checked = this.frontendConfig.ui.enableAnimations !== false);
            document.getElementById('show-timestamps-toggle') && (document.getElementById('show-timestamps-toggle').checked = this.frontendConfig.ui.showTimestamps !== false);
            document.getElementById('max-message-length') && (document.getElementById('max-message-length').value = this.frontendConfig.ui.maxMessageLength || 4000);
        }
    }

    applyAnimationsSetting(enabled) {
        if (!enabled) {
            document.body.style.setProperty('--transition-duration', '0s');
        } else {
            document.body.style.removeProperty('--transition-duration');
        }
    }

    applyTimestampsSetting(enabled) {
        const timeElements = document.querySelectorAll('.message-time');
        timeElements.forEach(element => {
            element.style.display = enabled ? 'block' : 'none';
        });
    }

    updateCharCountLimit(maxLength) {
        this.charLimit = maxLength;
        // 更新现有字符计数显示
        const charCount = document.getElementById('char-count');
        const input = document.getElementById('user-input');
        const currentLength = input.value.length;
        charCount.textContent = `${currentLength} / ${maxLength}`;
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

    // 删除会话相关方法
    confirmDeleteSession(sessionId, sessionTitle) {
        this.sessionToDelete = sessionId;
        this.sessionTitleToDelete = sessionTitle;

        // 更新确认对话框的内容
        const warningP = document.querySelector('.delete-warning p');
        if (warningP) {
            warningP.textContent = `确定要删除会话"${sessionTitle}"吗？`;
        }

        // 显示确认对话框
        const modal = document.getElementById('confirm-delete-modal');
        modal.classList.add('show');
    }

    closeDeleteConfirmModal() {
        const modal = document.getElementById('confirm-delete-modal');
        modal.classList.remove('show');
        this.sessionToDelete = null;
        this.sessionTitleToDelete = null;
    }

    async deleteCurrentSession() {
        if (!this.sessionToDelete) return;

        const deleteBtn = document.getElementById('confirm-delete');
        const originalContent = deleteBtn.innerHTML;

        // 显示加载状态
        deleteBtn.disabled = true;
        deleteBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 删除中...';

        try {
            const response = await fetch(`/api/session/${this.sessionToDelete}`, {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' }
            });

            if (response.ok) {
                this.showSuccess('会话删除成功');

                // 从本地会话列表中移除被删除的会话
                const sessionIndex = this.sessions.findIndex(s => s.session_id === this.sessionToDelete);
                const deletedSession = this.sessions[sessionIndex];
                this.sessions.splice(sessionIndex, 1);

                // 如果删除的是当前会话，需要切换到其他会话
                if (this.sessionToDelete === this.currentSessionId) {
                    this.handleCurrentSessionDeletion(deletedSession);
                }

                // 更新会话列表UI
                this.updateChatList();

            } else {
                const errorData = await response.json();
                this.showError(`删除失败: ${errorData.detail || '未知错误'}`);
            }
        } catch (error) {
            console.error('删除会话失败:', error);
            this.showError('删除会话失败，请重试');
        } finally {
            // 恢复按钮状态
            deleteBtn.disabled = false;
            deleteBtn.innerHTML = originalContent;
            this.closeDeleteConfirmModal();
        }
    }

    handleCurrentSessionDeletion(deletedSession = null) {
        // 找到其他可用的会话
        const otherSessions = this.sessions.filter(s => s.session_id !== this.sessionToDelete);

        if (otherSessions.length > 0) {
            // 切换到第一个其他会话
            console.log(`切换到其他会话: ${otherSessions[0].session_id}`);
            this.switchToSession(otherSessions[0].session_id);
        } else {
            // 没有其他会话，创建新会话
            console.log('没有其他会话，准备创建新会话');
            this.currentSessionId = null;
            this.currentPersonaId = null;
            this.messages = [];
            this.renderMessages();
            this.updateChatTitle();
            this.updatePersonaBadge();

            // 延迟一下打开新对话界面，让界面有时间更新
            setTimeout(() => {
                this.openNewChatModal();
            }, 100);
        }
    }

    checkPersonaNameAvailability(name, modalType) {
        const trimmedName = name.trim();

        if (!trimmedName) {
            // 清除任何提示
            this.clearPersonaNameWarning(modalType);
            return;
        }

        const existingPersona = this.personas.find(p => p.name === trimmedName);
        const nameInput = modalType === 'new-chat'
            ? document.getElementById('custom-persona-name')
            : document.getElementById('custom-persona-name-persona-modal');

        if (existingPersona) {
            // 显示重复名称警告
            this.showPersonaNameWarning(modalType, `人设名称 "${trimmedName}" 已存在`);
            nameInput.style.borderColor = '#ef4444';
        } else {
            // 清除警告，显示可用状态
            this.clearPersonaNameWarning(modalType);
            nameInput.style.borderColor = '#10b981';
        }
    }

    showPersonaNameWarning(modalType, message) {
        const warningId = modalType === 'new-chat'
            ? 'persona-name-warning-new-chat'
            : 'persona-name-warning-persona-modal';

        let warningElement = document.getElementById(warningId);

        if (!warningElement) {
            warningElement = document.createElement('div');
            warningElement.id = warningId;
            warningElement.style.cssText = `
                color: #ef4444;
                font-size: 12px;
                margin-top: 4px;
                display: block;
            `;

            const nameInput = modalType === 'new-chat'
                ? document.getElementById('custom-persona-name')
                : document.getElementById('custom-persona-name-persona-modal');

            nameInput.parentNode.appendChild(warningElement);
        }

        warningElement.textContent = message;
        warningElement.style.display = 'block';
    }

    clearPersonaNameWarning(modalType) {
        const warningId = modalType === 'new-chat'
            ? 'persona-name-warning-new-chat'
            : 'persona-name-warning-persona-modal';

        const warningElement = document.getElementById(warningId);
        if (warningElement) {
            warningElement.style.display = 'none';
        }

        const nameInput = modalType === 'new-chat'
            ? document.getElementById('custom-persona-name')
            : document.getElementById('custom-persona-name-persona-modal');

        if (nameInput) {
            nameInput.style.borderColor = '';
        }
    }
}

// 初始化应用
let app;
document.addEventListener('DOMContentLoaded', function() {
    app = new ChatApp();
});