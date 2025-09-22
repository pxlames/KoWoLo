// 全局状态管理
let currentStatus = {
    currentWork: '',
    futureWork: '',
    currentCompleted: false,
    futureCompleted: false
};

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    loadStatus();
    setupEventListeners();
});

// 设置事件监听器
function setupEventListeners() {
    const form = document.getElementById('statusForm');
    form.addEventListener('submit', handleFormSubmit);
}

// 处理表单提交
async function handleFormSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const currentWork = formData.get('currentWork').trim();
    const futureWork = formData.get('futureWork').trim();
    
    if (!currentWork && !futureWork) {
        alert('请至少填写一个状态');
        return;
    }
    
    // 显示加载状态
    showLoading();
    
    try {
        const response = await fetch('/api/update-status', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                currentWork: currentWork,
                futureWork: futureWork
            })
        });
        
        if (!response.ok) {
            throw new Error('更新状态失败');
        }
        
        const result = await response.json();
        
        // 更新本地状态
        updateLocalStatus(result);
        
        // 清空表单
        event.target.reset();
        
        // 显示成功消息
        showMessage('状态更新成功！', 'success');
        
    } catch (error) {
        console.error('Error:', error);
        showMessage('更新失败，请重试', 'error');
    } finally {
        hideLoading();
    }
}

// 更新本地状态显示
function updateLocalStatus(data) {
    // 更新当前工作状态
    if (data.currentWork) {
        currentStatus.currentWork = data.currentWork;
        currentStatus.currentCompleted = data.currentCompleted || false;
        updateStatusDisplay('current', data.currentWork, currentStatus.currentCompleted);
    }
    
    // 更新未来工作状态
    if (data.futureWork) {
        currentStatus.futureWork = data.futureWork;
        currentStatus.futureCompleted = data.futureCompleted || false;
        updateStatusDisplay('future', data.futureWork, currentStatus.futureCompleted);
    }
    
    // 更新总结
    if (data.summary) {
        updateSummaryDisplay(data.summary);
    }
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
    summaryElement.textContent = summary;
    summaryElement.classList.remove('placeholder');
}

// 切换状态完成状态
async function toggleStatus(type) {
    const statusKey = type + 'Completed';
    const newStatus = !currentStatus[statusKey];
    
    try {
        const response = await fetch('/api/toggle-status', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                type: type,
                completed: newStatus
            })
        });
        
        if (!response.ok) {
            throw new Error('切换状态失败');
        }
        
        const result = await response.json();
        currentStatus[statusKey] = newStatus;
        updateStatusDisplay(type, currentStatus[type + 'Work'], newStatus);
        
        if (result.summary) {
            updateSummaryDisplay(result.summary);
        }
        
    } catch (error) {
        console.error('Error:', error);
        showMessage('切换状态失败，请重试', 'error');
    }
}

// 刷新总结
async function refreshSummary() {
    showLoading();
    
    try {
        const response = await fetch('/api/refresh-summary', {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error('刷新总结失败');
        }
        
        const result = await response.json();
        updateSummaryDisplay(result.summary);
        showMessage('总结已刷新', 'success');
        
    } catch (error) {
        console.error('Error:', error);
        showMessage('刷新失败，请重试', 'error');
    } finally {
        hideLoading();
    }
}

// 加载状态
async function loadStatus() {
    try {
        const response = await fetch('/api/status');
        if (response.ok) {
            const data = await response.json();
            updateLocalStatus(data);
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
