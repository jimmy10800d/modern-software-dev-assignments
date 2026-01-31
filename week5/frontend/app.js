async function fetchJSON(url, options) { // 呼叫 API 並回傳 JSON
  const res = await fetch(url, options); // 發送請求
  if (!res.ok) throw new Error(await res.text()); // 錯誤處理
  return res.json(); // 回傳 JSON
}

async function loadNotes() { // 載入筆記清單
  const list = document.getElementById('notes'); // 取得清單元素
  list.innerHTML = ''; // 清空清單
  const notes = await fetchJSON('/notes/'); // 取得筆記
  for (const n of notes) { // 逐筆處理
    const li = document.createElement('li'); // 建立 li
    li.textContent = `${n.title}: ${n.content}`; // 設定文字
    list.appendChild(li); // 加入清單
  }
}

async function loadActions() { // 載入行動項目
  const list = document.getElementById('actions'); // 取得清單
  list.innerHTML = ''; // 清空清單
  const items = await fetchJSON('/action-items/'); // 取得行動項目
  for (const a of items) { // 逐筆處理
    const li = document.createElement('li'); // 建立 li
    li.textContent = `${a.description} [${a.completed ? 'done' : 'open'}]`; // 設定文字
    if (!a.completed) { // 若未完成
      const btn = document.createElement('button'); // 建立按鈕
      btn.textContent = 'Complete'; // 設定按鈕文字
      btn.onclick = async () => { // 綁定點擊事件
        await fetchJSON(`/action-items/${a.id}/complete`, { method: 'PUT' }); // 呼叫完成 API
        loadActions(); // 重新載入
      };
      li.appendChild(btn); // 加入按鈕
    }
    list.appendChild(li); // 加入清單
  }
}

window.addEventListener('DOMContentLoaded', () => { // DOM 載入完成
  document.getElementById('note-form').addEventListener('submit', async (e) => { // 提交筆記表單
    e.preventDefault(); // 阻止預設行為
    const title = document.getElementById('note-title').value; // 取得標題
    const content = document.getElementById('note-content').value; // 取得內容
    await fetchJSON('/notes/', { // 呼叫新增筆記 API
      method: 'POST', // 使用 POST
      headers: { 'Content-Type': 'application/json' }, // JSON 格式
      body: JSON.stringify({ title, content }), // 傳送資料
    });
    e.target.reset(); // 清空表單
    loadNotes(); // 重新載入清單
  });

  document.getElementById('action-form').addEventListener('submit', async (e) => { // 提交行動項目表單
    e.preventDefault(); // 阻止預設
    const description = document.getElementById('action-desc').value; // 取得描述
    await fetchJSON('/action-items/', { // 呼叫新增行動項目 API
      method: 'POST', // 使用 POST
      headers: { 'Content-Type': 'application/json' }, // JSON 格式
      body: JSON.stringify({ description }), // 傳送資料
    });
    e.target.reset(); // 清空表單
    loadActions(); // 重新載入清單
  });

  loadNotes(); // 初始載入筆記
  loadActions(); // 初始載入行動項目
});
