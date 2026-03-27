// 请求通知权限
function requestNotificationPermission() {
	if ('Notification' in window && Notification.permission === 'default') {
		Notification.requestPermission().then(permission => {
			console.log('通知权限:', permission);
		});
	}
}

// 发送计算完成通知
function sendCalcNotification(expression, result, isError) {
	if (!('Notification' in window)) {
		console.log('浏览器不支持 Notification API');
		return;
	}
	if (Notification.permission !== 'granted') {
		console.log('没有通知权限');
		return;
	}
	
	const title = isError ? '❌ 计算出错' : '✓ 计算完成';
	// 处理长文本
	const maxExprLen = 30;
	const maxResultLen = 50;
	const shortExpr = expression.length > maxExprLen 
		? expression.substring(0, maxExprLen) + '...' 
		: expression;
	const shortResult = result.length > maxResultLen 
		? result.substring(0, maxResultLen) + '...' 
		: result;
	
	const body = isError 
		? `算式: ${shortExpr}\n错误: ${shortResult}`
		: `算式: ${shortExpr}\n结果: ${shortResult}`;
	
	try {
		const notification = new Notification(title, {
			body: body,
			tag: 'calc-result-' + Date.now(),
			requireInteraction: false,
			silent: false
		});
		
		// 点击通知时聚焦窗口
		notification.onclick = () => {
			window.focus();
			notification.close();
		};
		
		console.log('已发送通知:', title);
	} catch (e) {
		console.error('发送通知失败:', e);
	}
}

function updateInputBg(){
	var input = document.getElementById("ev-input");
	if(input.value === ""){
		input.style.backgroundColor = "#00ffff44";
	}else{
		input.style.backgroundColor = "#00ffff88";
	}
}
function onload(){
	var input = document.getElementById("ev-input");
	input.onkeydown=function(e){if(e.key=="Enter")calc();}
	input.oninput=updateInputBg;
	input.onfocus=function(){
		input.select()
		if(resExists)input.value=fullResultText
		updateInputBg();
	};
	input.onblur=function(){
		input.style.backgroundColor = "";
	};
	input.focus();
}
function displayResult(text) {
	const resultEl = document.getElementById("ev-result");
	const truncatedEl = document.getElementById("ev-result-truncated");
	const hintEl = document.getElementById("ev-result-hint");
	
	// 保存完整结果用于复制
	fullResultText = text;
	
	// 先设置完整文本
	resultEl.innerText = text;
	resultEl.classList.remove("truncated");
	truncatedEl.style.display = "none";
	hintEl.style.display = "none";
	
	// 使用 requestAnimationFrame 确保 DOM 已更新
	requestAnimationFrame(() => {
		// 计算行数
		const lineHeight = parseFloat(getComputedStyle(resultEl).lineHeight);
		const height = resultEl.scrollHeight;
		const lines = Math.round(height / lineHeight);
		
		if (lines > 5) {
			// 超过5行，添加截断样式
			resultEl.classList.add("truncated");
			truncatedEl.style.display = "inline";
			hintEl.style.display = "block";
		}
	});
}

function ac(){
	resExists=false;
	document.getElementById("ev-input").value="";
	document.getElementById("ev-res").style.display="none";
	document.getElementById("res-btns").style.display="none";
	document.getElementById("ev-equal-sign").style.color="black";
	document.getElementById("ev-equal-sign").innerText="=";
	// 重置结果显示
	document.getElementById("ev-result").innerText = "";
	document.getElementById("ev-result").classList.remove("truncated");
	document.getElementById("ev-result-truncated").style.display = "none";
	document.getElementById("ev-result-hint").style.display = "none";
}
function copy_res(){
	if(!resExists || !navigator.clipboard){
		document.getElementById("res-copy").innerText="复制失败！";
		document.getElementById("res-copy").style.color="red";
		status(false);
	}else{
		navigator.clipboard.writeText(fullResultText);
		document.getElementById("res-copy").innerText="已复制";
		document.getElementById("res-copy").style.color="green";
		status(true);
	}
	setTimeout(function(){
		document.getElementById("res-copy").innerText="复制";
		document.getElementById("res-copy").style.color="black";
	},1000);
}

function copy_full(){
	if(!resExists || !navigator.clipboard){
		document.getElementById("res-copy").innerText="复制失败！";
		document.getElementById("res-copy").style.color="red";
		status(false);
	}else{
		navigator.clipboard.writeText(document.getElementById("ev-input").value + " = " + fullResultText);
		document.getElementById("res-copy").innerText="已复制完整算式";
		document.getElementById("res-copy").style.color="green";
		status(true);
	}
	setTimeout(function(){
		document.getElementById("res-copy").innerText="复制";
		document.getElementById("res-copy").style.color="black";
	},1000);
}

async function mem_res(){
	if(!resExists){
		document.getElementById("res-copy").innerText="记忆失败！";
		document.getElementById("res-copy").style.color="red";
		status(false);
	}else{
		let val = fullResultText;
		// 直接存储字符串，不转换为 float（避免精度丢失）
		memoryValue = val;
		
		// 同步到服务器（HTTP 模式）
		try {
			await fetch('/api/mem', {
				method: 'POST',
				headers: {'Content-Type': 'application/json'},
				body: JSON.stringify({value: val})  // 发送字符串
			});
		} catch(e) {
			document.getElementById("res-copy").innerText="记忆失败";
			document.getElementById("res-copy").style.color="red";
			status(false)
			console.error('Failed to sync memory:', e);
		}
		
		document.getElementById("res-copy").innerText="已记忆";
		document.getElementById("res-copy").style.color="green";
		status(true);
	}
	setTimeout(function(){
		document.getElementById("res-copy").innerText="记忆";
		document.getElementById("res-copy").style.color="black";
	},1000);
}
function openDialog(id){
	document.getElementById(id).showModal()
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', onload);

// 暴露函数到全局作用域，供 HTML onclick 使用
window.calc = calc;
window.ac = ac;
window.copy_res = copy_res;
window.copy_full = copy_full;
window.mem_res = mem_res;
window.openDialog = openDialog;
window.displayResult = displayResult;