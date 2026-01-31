async function fetchJSON(url, options) { // 呼叫 API 並回傳 JSON
  const res = await fetch(url, options); // 發送請求
  if (!res.ok) throw new Error(await res.text()); // 錯誤處理
  return res.json(); // 回傳 JSON
}

async function loadNotes(params = {}) { // 載入筆記清單
  const list = document.getElementById('notes'); // 取得清單
  list.innerHTML = ''; // 清空
  const query = new URLSearchParams(params); // 建立查詢字串
  const notes = await fetchJSON('/notes/?' + query.toString()); // 取得筆記
  for (const n of notes) { // 逐筆處理
    const li = document.createElement('li'); // 建立 li
    li.innerHTML = `<strong>${n.title}</strong>: ${n.content}`; // 設定內容
    list.appendChild(li); // 加入清單
  }
}

async function loadActions(params = {}) { // 載入行動項目
  const list = document.getElementById('actions'); // 取得清單
  list.innerHTML = ''; // 清空
  const query = new URLSearchParams(params); // 建立查詢字串
  const items = await fetchJSON('/action-items/?' + query.toString()); // 取得行動項目
  for (const a of items) { // 逐筆處理
    const li = document.createElement('li'); // 建立 li
    li.textContent = `${a.description} [${a.completed ? 'done' : 'open'}]`; // 設定文字
    if (!a.completed) { // 若未完成
      const btn = document.createElement('button'); // 建立按鈕
      btn.textContent = 'Complete'; // 設定文字
      btn.onclick = async () => { // 綁定點擊事件
        await fetchJSON(`/action-items/${a.id}/complete`, { method: 'PUT' }); // 完成項目
        loadActions(params); // 重新載入
      };
      li.appendChild(btn); // 加入按鈕
    } else {
      const btn = document.createElement('button'); // 建立按鈕
      btn.textContent = 'Reopen'; // 設定文字
      btn.onclick = async () => { // 綁定點擊事件
        await fetchJSON(`/action-items/${a.id}`, { // 重新打開
          method: 'PATCH', // 使用 PATCH
          headers: { 'Content-Type': 'application/json' }, // JSON 格式
          body: JSON.stringify({ completed: false }), // 傳送更新
        });
        loadActions(params); // 重新載入
      };
      li.appendChild(btn); // 加入按鈕
    }
    list.appendChild(li); // 加入清單
  }
}

window.addEventListener('DOMContentLoaded', () => { // DOM 載入完成
  document.getElementById('note-form').addEventListener('submit', async (e) => { // 提交筆記
    e.preventDefault(); // 阻止預設
    const title = document.getElementById('note-title').value; // 取得標題
    const content = document.getElementById('note-content').value; // 取得內容
    await fetchJSON('/notes/', { // 呼叫新增 API
      method: 'POST', // 使用 POST
      headers: { 'Content-Type': 'application/json' }, // JSON 格式
      body: JSON.stringify({ title, content }), // 傳送資料
    });
    e.target.reset(); // 清空表單
    loadNotes(); // 重新載入
  });

  document.getElementById('note-search-btn').addEventListener('click', async () => { // 搜尋按鈕
    const q = document.getElementById('note-search').value; // 取得關鍵字
    loadNotes({ q }); // 重新載入
  });

  document.getElementById('action-form').addEventListener('submit', async (e) => { // 新增行動項目
    e.preventDefault(); // 阻止預設
    const description = document.getElementById('action-desc').value; // 取得描述
    await fetchJSON('/action-items/', { // 呼叫新增 API
      method: 'POST', // 使用 POST
      headers: { 'Content-Type': 'application/json' }, // JSON 格式
      body: JSON.stringify({ description }), // 傳送資料
    });
    e.target.reset(); // 清空表單
    loadActions(); // 重新載入
  });

  document.getElementById('filter-completed').addEventListener('change', (e) => { // 完成狀態切換
    const checked = e.target.checked; // 取得狀態
    loadActions({ completed: checked }); // 重新載入
  });

  loadNotes(); // 初始載入
  loadActions(); // 初始載入
});


