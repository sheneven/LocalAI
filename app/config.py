class Config:
    SECRET_KEY = 'c108b8c37b6f4580b5ca1fc0df85b4e2'  # Generated secure key
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # CSRF保护
    WTF_CSRF_ENABLED = True
    
    # LLM API配置
    DEFAULT_LLM_URL = 'http://localhost:11434/api/chat'
    
    # RPA配置
    CHROME_DRIVER_PATH = '/snap/bin/chromium.chromedriver'#h '/path/to/chromedriver'
    
    # 其他配置项
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB 
    
    # Ollama配置
    OLLAMA_HOST = "127.0.0.1"
    OLLAMA_PORT = 11434
    OLLAMA_API_BASE = "/api/chat"
    DEFAULT_MODEL = "deepseek-coder:latest"  # 或其他您想使用的模型 