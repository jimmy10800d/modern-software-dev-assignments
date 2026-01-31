def test_create_complete_list_and_patch_action_item(client):  # 測試建立、完成、列表與更新
    payload = {"description": "Ship it"}  # 建立 payload
    r = client.post("/action-items/", json=payload)  # 呼叫建立 API
    assert r.status_code == 201, r.text  # 檢查建立成功
    item = r.json()  # 解析回應
    assert item["completed"] is False  # 預設未完成
    assert "created_at" in item and "updated_at" in item  # 應包含時間欄位

    r = client.put(f"/action-items/{item['id']}/complete")  # 呼叫完成 API
    assert r.status_code == 200  # 檢查成功
    done = r.json()  # 解析回應
    assert done["completed"] is True  # 應為完成

    r = client.get("/action-items/", params={"completed": True, "limit": 5, "sort": "-created_at"})  # 查詢列表
    assert r.status_code == 200  # 檢查成功
    items = r.json()  # 解析清單
    assert len(items) >= 1  # 至少一筆

    r = client.patch(f"/action-items/{item['id']}", json={"description": "Updated"})  # 呼叫更新 API
    assert r.status_code == 200  # 檢查成功
    patched = r.json()  # 解析回應
    assert patched["description"] == "Updated"  # 描述應更新


