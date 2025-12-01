import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 检查密钥
api_key = os.getenv('OPENAI_API_KEY')
print(f"API Key exists: {api_key is not None}")
print(f"API Key length: {len(api_key) if api_key else 'None'}")
print(f"API Key preview: {api_key[:15]}..." if api_key else "No key found")