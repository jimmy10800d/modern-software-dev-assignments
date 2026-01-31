def test_create_list_and_patch_notes(client):  # 測試建立、列表與更新筆記
    payload = {"title": "Test", "content": "Hello world"}  # 建立 payload
    r = client.post("/notes/", json=payload)  # 呼叫建立 API
    assert r.status_code == 201, r.text  # 檢查建立成功
    data = r.json()  # 解析回應
    assert data["title"] == "Test"  # 標題應正確
    assert "created_at" in data and "updated_at" in data  # 應包含時間欄位

    r = client.get("/notes/")  # 查詢所有筆記
    assert r.status_code == 200  # 檢查成功
    items = r.json()  # 解析清單
    assert len(items) >= 1  # 至少一筆

    r = client.get("/notes/", params={"q": "Hello", "limit": 10, "sort": "-created_at"})  # 查詢條件
    assert r.status_code == 200  # 檢查成功
    items = r.json()  # 解析清單
    assert len(items) >= 1  # 至少一筆

    note_id = data["id"]  # 取得筆記 id
    r = client.patch(f"/notes/{note_id}", json={"title": "Updated"})  # 更新標題
    assert r.status_code == 200  # 檢查成功
    patched = r.json()  # 解析回應
    assert patched["title"] == "Updated"  # 標題應更新


