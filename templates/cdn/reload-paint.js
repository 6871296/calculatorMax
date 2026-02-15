// 监听窗口大小改变事件
window.addEventListener('resize', function() {
    // 方案 A：强制重绘 (适用于大多数情况)
    document.body.style.display = 'none';
    // 触发回流
    void document.body.offsetHeight; 
    document.body.style.display = 'block'; // 或者恢复原来的 display 值
    
    // 方案 B：如果方案A不行，尝试调整缩放（备用）
     document.body.style.zoom = 1.0001;
     setTimeout(() => document.body.style.zoom = 1, 100);
});
window.addEventListener('resize', function() {
            // 强制回到顶部
            document.querySelector('html').scrollTop = 0;
            // 取消焦点
            if (document.activeElement) document.activeElement.blur();
        });