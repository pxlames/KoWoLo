// 全局状态管理
let statusList = [];
let summary = '';
let sidebarCollapsed = false;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    loadStatus();
    setupEventListeners();
    initializeSidebar();
});

// 设置事件监听器
function setupEventListeners() {
    const form = document.getElementById('addStatusForm');
    form.addEventListener('submit', handleAddStatus);
}

// 处理添加状态表单提交
async function handleAddStatus(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const title = formData.get('title').trim();
    const description = formData.get('description').trim();
    const type = formData.get('type');
    
    if (!title) {
        alert('请填写状态标题');
        return;
    }
    
    // 显示加载状态
    showLoading();
    
    try {
        const response = await fetch('/api/add-status', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                title: title,
                description: description,
                type: type
            })
        });
        
        if (!response.ok) {
            throw new Error('添加状态失败');
        }
        
        const result = await response.json();
        
        // 更新本地状态列表
        statusList.push(result.status);
        updateStatusList();
        
        // 清空表单
        event.target.reset();
        
        // 显示成功消息
        showMessage('状态添加成功！', 'success');
        
    } catch (error) {
        console.error('Error:', error);
        showMessage('添加失败，请重试', 'error');
    } finally {
        hideLoading();
    }
}

// 初始化侧边栏
function initializeSidebar() {
    // 从本地存储读取侧边栏状态
    const savedState = localStorage.getItem('sidebarCollapsed');
    if (savedState === 'true') {
        toggleSidebar();
    }
}

// 切换侧边栏折叠状态
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const toggleIcon = document.getElementById('sidebarToggle');
    
    sidebarCollapsed = !sidebarCollapsed;
    
    if (sidebarCollapsed) {
        sidebar.classList.add('collapsed');
        toggleIcon.classList.remove('fa-chevron-left');
        toggleIcon.classList.add('fa-chevron-right');
    } else {
        sidebar.classList.remove('collapsed');
        toggleIcon.classList.remove('fa-chevron-right');
        toggleIcon.classList.add('fa-chevron-left');
    }
    
    // 保存状态到本地存储
    localStorage.setItem('sidebarCollapsed', sidebarCollapsed.toString());
}

// 更新状态列表显示
function updateStatusList() {
    const statusListElement = document.getElementById('statusList');
    
    if (statusList.length === 0) {
        statusListElement.innerHTML = '<div class="placeholder-item"><p class="placeholder">暂无状态记录</p></div>';
        return;
    }
    
    statusListElement.innerHTML = statusList.map(status => `
        <div class="status-item ${status.completed ? 'completed' : ''} ${!status.aiProcessed ? 'unprocessed' : ''}" onclick="toggleStatus('${status.id}')">
            <div class="status-item-title">${status.title}</div>
            <span class="status-item-type status-type-${status.type}">${getTypeLabel(status.type)}</span>
            ${status.description ? `<div class="status-item-description">${status.description}</div>` : ''}
            <div class="status-item-meta">
                ${formatDate(status.createdAt)}
                ${!status.aiProcessed ? '<span style="color: #f59e0b;">🆕</span>' : ''}
            </div>
        </div>
    `).join('');
}

// 获取类型标签
function getTypeLabel(type) {
    const labels = {
        'ongoing': '正在进行',
        'planned': '计划进行',
        'completed': '已完成'
    };
    return labels[type] || type;
}

// 格式化日期
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN');
}

// 更新状态显示
function updateStatusDisplay(type, content, completed) {
    const statusElement = document.getElementById(type + 'Status');
    const statusItem = statusElement.closest('.status-item');
    
    if (content) {
        statusElement.innerHTML = `<p>${content}</p>`;
        statusItem.classList.remove('placeholder');
        
        if (completed) {
            statusItem.classList.add('status-success');
            statusElement.classList.add('completed');
        } else {
            statusItem.classList.remove('status-success');
            statusElement.classList.remove('completed');
        }
    } else {
        statusElement.innerHTML = '<p class="placeholder">暂无' + (type === 'current' ? '进行中' : '计划中') + '的工作</p>';
        statusItem.classList.remove('status-success');
        statusElement.classList.remove('completed');
    }
}

// 更新总结显示
function updateSummaryDisplay(summary) {
    const summaryElement = document.getElementById('summaryContent');
    
    // 如果summary是JSON格式，提取summary字段
    let summaryText = summary;
    if (typeof summary === 'object' && summary.summary) {
        summaryText = summary.summary;
    } else if (typeof summary === 'string' && summary.includes('"summary"')) {
        try {
            const parsed = JSON.parse(summary);
            summaryText = parsed.summary || summary;
        } catch (e) {
            summaryText = summary;
        }
    }
    
    // 渲染Markdown
    summaryElement.innerHTML = renderMarkdown(summaryText);
    summaryElement.classList.remove('placeholder');
}

// 切换状态完成状态
async function toggleStatus(statusId) {
    const status = statusList.find(s => s.id === statusId);
    if (!status) return;
    
    const newStatus = !status.completed;
    
    try {
        const response = await fetch('/api/toggle-status', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                id: statusId,
                completed: newStatus
            })
        });
        
        if (!response.ok) {
            throw new Error('切换状态失败');
        }
        
        const result = await response.json();
        statusList = result.statusList;
        updateStatusList();
        
        showMessage('状态更新成功！', 'success');
        
    } catch (error) {
        console.error('Error:', error);
        showMessage('切换状态失败，请重试', 'error');
    }
}

// 生成AI总结
async function generateAISummary() {
    if (statusList.length === 0) {
        showMessage('请先添加状态再生成总结', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/generate-summary-stream', {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error('生成总结失败');
        }
        
        // 处理流式响应
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let fullSummary = '';
        
        // 准备显示流式内容（不清空，追加显示）
        const summaryElement = document.getElementById('summaryContent');
        
        // 如果之前有内容，先添加分隔线
        if (summaryElement.innerHTML.trim() && !summaryElement.innerHTML.includes('placeholder')) {
            const separator = document.createElement('div');
            separator.className = 'content-separator';
            const now = new Date();
            const timeStr = now.toLocaleString('zh-CN', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            });
            separator.innerHTML = `<hr><div class="separator-text">新的AI总结 - ${timeStr}</div><hr>`;
            summaryElement.appendChild(separator);
        }
        
        summaryElement.classList.remove('placeholder');
        
        
        // 创建消息元素用于流式显示
        let messageElement = null;
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split('\n');
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const data = JSON.parse(line.slice(6));
                        
                        if (data.type === 'error') {
                            throw new Error(data.content);
                        }
                        
                        if (data.type === 'content') {
                            fullSummary += data.content;
                            
                            // 创建消息元素（如果还没有）
                            if (!messageElement) {
                                messageElement = createStreamingMessage();
                                summaryElement.appendChild(messageElement);
                            }
                            
                            // 实时更新显示
                            updateStreamingContent(messageElement, fullSummary);
                        }
                        
                        if (data.type === 'done') {
                            // 流式输出完成
                            summary = data.summary || fullSummary;
                            
                            // 最终渲染Markdown
                            if (messageElement) {
                                const contentElement = messageElement.querySelector('.message-content');
                                if (contentElement) {
                                    contentElement.innerHTML = renderMarkdown(fullSummary);
                                }
                                // 移除流式样式
                                messageElement.classList.remove('streaming');
                            }
                            
                            updateStatusList();
                            showMessage('AI总结生成成功！', 'success');
                            return;
                        }
                    } catch (e) {
                        console.error('解析流式数据失败:', e);
                    }
                }
            }
        }
        
    } catch (error) {
        console.error('Error:', error);
        showMessage('生成总结失败，请重试', 'error');
    }
}

// 创建流式消息元素
function createStreamingMessage() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant streaming';
    messageDiv.innerHTML = `
        <div class="message-header">
            <span class="icon">🤖</span>
            <span>AI助手</span>
            <span class="streaming-indicator-small">正在生成...</span>
        </div>
        <div class="message-content"></div>
        <div class="message-time">${new Date().toLocaleTimeString()}</div>
    `;
    return messageDiv;
}

// 更新流式内容
function updateStreamingContent(messageElement, content) {
    const contentElement = messageElement.querySelector('.message-content');
    if (contentElement) {
        // 显示原始文本，不渲染Markdown（避免闪烁）
        contentElement.textContent = content;
        
        // 自动滚动到底部
        const summaryElement = document.getElementById('summaryContent');
        summaryElement.scrollTop = summaryElement.scrollHeight;
    }
}


// 刷新总结
async function refreshSummary() {
    // 直接调用生成AI总结，这样会追加到现有内容中
    await generateAISummary();
}

// 加载状态
async function loadStatus() {
    try {
        const response = await fetch('/api/status');
        if (response.ok) {
            const data = await response.json();
            statusList = data.statusList || [];
            summary = data.summary || '';
            
            updateStatusList();
            updateSummaryDisplay(summary);
        }
    } catch (error) {
        console.error('Error loading status:', error);
    }
}

// 显示加载状态
function showLoading() {
    document.getElementById('loadingOverlay').style.display = 'flex';
}

// 隐藏加载状态
function hideLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
}

// 显示消息
function showMessage(message, type) {
    // 创建消息元素
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${type}`;
    messageDiv.textContent = message;
    
    // 添加样式
    messageDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 20px;
        border-radius: 6px;
        color: white;
        font-weight: 600;
        z-index: 1001;
        animation: slideIn 0.3s ease-out;
        background-color: ${type === 'success' ? '#2da44e' : '#d73a49'};
    `;
    
    // 添加到页面
    document.body.appendChild(messageDiv);
    
    // 3秒后自动移除
    setTimeout(() => {
        messageDiv.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.parentNode.removeChild(messageDiv);
            }
        }, 300);
    }, 3000);
}

// Markdown渲染函数
function renderMarkdown(text) {
    if (!text) return '';
    
    return text
        // 标题
        .replace(/^### (.*$)/gim, '<h3>$1</h3>')
        .replace(/^## (.*$)/gim, '<h2>$1</h2>')
        .replace(/^# (.*$)/gim, '<h1>$1</h1>')
        
        // 粗体和斜体
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        
        // 代码块
        .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        
        // 列表
        .replace(/^\* (.*$)/gim, '<li>$1</li>')
        .replace(/^- (.*$)/gim, '<li>$1</li>')
        .replace(/^\d+\. (.*$)/gim, '<li>$1</li>')
        
        // 链接
        .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>')
        
        // 换行
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>')
        
        // 包装段落
        .replace(/^(.*)$/gm, '<p>$1</p>')
        
        // 清理空段落
        .replace(/<p><\/p>/g, '')
        .replace(/<p><br><\/p>/g, '')
        
        // 包装列表项
        .replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>')
        .replace(/<\/ul>\s*<ul>/g, '');
}

// 添加CSS动画
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
