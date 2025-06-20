/**
 * 通知管理模块
 * 负责显示各种类型的通知消息
 */
class NotificationManager {
    constructor() {
        this.toastElement = null;
        this.init();
    }

    /**
     * 初始化通知系统
     */
    init() {
        this.toastElement = document.getElementById('notificationToast');
        if (!this.toastElement) {
            console.warn('通知Toast元素未找到');
        }
    }

    /**
     * 显示通知
     */
    show(message, type = 'info') {
        if (!this.toastElement) {
            console.warn('通知系统未初始化');
            return;
        }

        const toastMessage = document.getElementById('toastMessage');
        
        // 设置图标和样式
        const icons = {
            'success': 'bi-check-circle-fill text-success',
            'error': 'bi-x-circle-fill text-danger',
            'warning': 'bi-exclamation-triangle-fill text-warning',
            'info': 'bi-info-circle-fill text-primary'
        };
        
        const icon = icons[type] || icons.info;
        const header = this.toastElement.querySelector('.toast-header i');
        if (header) {
            header.className = `${icon} me-2`;
        }
        
        if (toastMessage) {
            toastMessage.textContent = message;
        }
        
        const bsToast = new bootstrap.Toast(this.toastElement);
        bsToast.show();
    }

    /**
     * 显示成功通知
     */
    success(message) {
        this.show(message, 'success');
    }

    /**
     * 显示错误通知
     */
    error(message) {
        this.show(message, 'error');
    }

    /**
     * 显示警告通知
     */
    warning(message) {
        this.show(message, 'warning');
    }

    /**
     * 显示信息通知
     */
    info(message) {
        this.show(message, 'info');
    }
}

export default NotificationManager; 