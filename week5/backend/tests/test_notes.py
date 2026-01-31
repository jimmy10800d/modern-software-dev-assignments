def test_create_and_list_notes(client):  # 測試建立與查詢筆記
    payload = {"title": "Test", "content": "Hello world"}  # 建立 payload
    r = client.post("/notes/", json=payload)  # 呼叫建立 API
    assert r.status_code == 201, r.text  # 檢查建立成功
    data = r.json()  # 解析回應
    assert data["title"] == "Test"  # 標題應正確

    r = client.get("/notes/")  # 查詢所有筆記
    assert r.status_code == 200  # 檢查成功
    items = r.json()  # 解析清單
    assert len(items) >= 1  # 至少一筆

    r = client.get("/notes/search/")  # 不帶參數查詢
    assert r.status_code == 200  # 檢查成功

    r = client.get("/notes/search/", params={"q": "Hello"})  # 帶關鍵字查詢
    assert r.status_code == 200  # 檢查成功
    items = r.json()  # 解析結果
    assert len(items) >= 1  # 至少一筆
