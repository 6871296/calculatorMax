// API 等待脚本 - 适用于 HTTP 模式
let apiReady = false;

function apiLoaded() {
    apiReady = true;
    console.log('API loaded');
}

// 初始化 API
function initAPI() {
    // 如果 pywebview 不存在，创建模拟 API
    if (typeof window.pywebview === 'undefined') {
        console.log('Creating mock pywebview API');
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
    } else {
        console.log('Native pywebview detected');
        // 如果 pywebview 存在但没有 api.calc，添加 HTTP 备用
        if (!window.pywebview.api || !window.pywebview.api.calc) {
            console.log('Adding HTTP fallback for calc');
            if (!window.pywebview.api) {
                window.pywebview.api = {};
            }
            window.pywebview.api.calc = function(expression) {
                return fetch('/api/calc', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ expression: expression })
                }).then(res => res.json());
            };
        }
    }
    apiLoaded();
}

// 等待 DOM 加载完成
document.addEventListener('DOMContentLoaded', function() {
    initAPI();
});

const tips=['Tips还在制作中，敬请期待！']

Math.random()
