from fastapi.testclient import TestClient
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend/gateway'))

from main import app

client = TestClient(app)

def test_health_check():
    """测试网关的健康检查接口"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "api-gateway"}

# 注意：更复杂的集成测试需要 Mock 数据库和 Redis，这里我们先做最基础的冒烟测试