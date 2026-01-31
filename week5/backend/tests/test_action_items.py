def test_create_and_complete_action_item(client):  # 測試建立與完成行動項目
    payload = {"description": "Ship it"}  # 建立 payload
    r = client.post("/action-items/", json=payload)  # 呼叫建立 API
    assert r.status_code == 201, r.text  # 檢查建立成功
    item = r.json()  # 解析回應
    assert item["completed"] is False  # 預設未完成

    r = client.put(f"/action-items/{item['id']}/complete")  # 呼叫完成 API
    assert r.status_code == 200  # 檢查成功
    done = r.json()  # 解析回應
    assert done["completed"] is True  # 應為完成

    r = client.get("/action-items/")  # 取得清單
    assert r.status_code == 200  # 檢查成功
    items = r.json()  # 解析清單
    assert len(items) == 1  # 應只有一筆
