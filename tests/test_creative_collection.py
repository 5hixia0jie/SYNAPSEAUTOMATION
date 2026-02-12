"""测试创意采集功能"""
import requests
import time

# 测试采集抖音视频
print("测试创意采集功能...")

# 提交采集任务
url = "http://localhost:7000/api/v1/creative_collection/collect"
data = {
    "video_url": "https://v.douyin.com/ie1oNqK8/"
}

response = requests.post(url, json=data)
print(f"提交采集任务响应: {response.json()}")

if response.status_code == 200:
    task_id = response.json().get("data", {}).get("task_id")
    if task_id:
        print(f"任务ID: {task_id}")
        
        # 查询任务状态
        status_url = f"http://localhost:7000/api/v1/creative_collection/status/{task_id}"
        
        for i in range(10):
            time.sleep(3)
            status_response = requests.get(status_url)
            status_data = status_response.json()
            print(f"任务状态: {status_data.get('data', {}).get('status')}")
            print(f"任务进度: {status_data.get('data', {}).get('progress')}%")
            
            if status_data.get('data', {}).get('status') in ['completed', 'failed']:
                break
        
        # 获取采集列表
        list_url = "http://localhost:7000/api/v1/creative_collection/list"
        list_response = requests.get(list_url)
        list_data = list_response.json()
        print(f"采集列表: {list_data}")
