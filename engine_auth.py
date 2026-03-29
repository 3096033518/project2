# 📄 engine_auth.py (真·SQL数据库驱动版)
import sqlite3
import hashlib
import os

class AuthEngine:
    def __init__(self, db_name="vla_users.db"):
        self.db_name = db_name
        # 引擎启动时，自动执行建表操作
        self._init_db()

    def _init_db(self):
        """核心建表：如果数据库或表不存在，就用 SQL 自动创建"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        # 执行标准 SQL 语句建表 (包含自增 ID、账号、加密密码、注册时间)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def _hash_pwd(self, password):
        """将明文密码转化为 64 位不可逆哈希值"""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def register(self, username, password):
        """执行 SQL INSERT 注册逻辑"""
        if not username or not password:
            return False, "⚠️ 账号或密码不能为空！"
            
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            # 采用参数化查询 (?)，这是大厂严防 SQL 注入攻击的标准写法！
            cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', 
                           (username, self._hash_pwd(password)))
            conn.commit()
            return True, "✅ 注册成功！请切换到登录页面。"
        except sqlite3.IntegrityError:
            # 捕获 UNIQUE 约束异常（用户名已存在）
            return False, "❌ 该用户名已被抢占，换一个吧！"
        finally:
            conn.close()

    def login(self, username, password):
        """执行 SQL SELECT 登录校验"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT password_hash FROM users WHERE username = ?', (username,))
        result = cursor.fetchone() # 获取查询结果的第一行
        conn.close()
        
        if result is None:
            return False, "❌ 用户名不存在！"
            
        if result[0] != self._hash_pwd(password):
            return False, "❌ 密码错误！"
            
        return True, f"🎉 欢迎回来，{username} 长官！"