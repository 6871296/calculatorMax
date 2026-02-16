// API 等待脚本 - 适用于 HTTP 模式
let apiReady = false;

function apiLoaded() {
    apiReady = true;
    console.log('API loaded');
}

// 等待 DOM 加载完成
document.addEventListener('DOMContentLoaded', function() {
    // 在 HTTP 模式下，模拟 pywebview API
    if (typeof window.pywebview === 'undefined') {
        // 创建模拟 API，通过 HTTP 调用后端
        window.pywebview = {
            api: {
                calc: function(expression) {
                    return fetch('/api/calc', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ expression: expression })
                    }).then(res => res.json());
                },
                m: 0
            }
        };
    }
    apiLoaded();
});
