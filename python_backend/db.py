"""
数据库连接池 & 自动建库建表
"""
import mysql.connector
from mysql.connector import pooling

from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

# ---- 基础连接配置（不含库名，用于建库） ----
base_config = {
    "host": DB_HOST,
    "user": DB_USER,
    "password": DB_PASSWORD,
}

# ---- 带库名的连接池配置 ----
db_config = {
    **base_config,
    "database": DB_NAME,
    "pool_name": "mypool",
    "pool_size": 5,
}

connection_pool = None


def init_db():
    """初始化数据库和表（幂等：重复执行安全）"""
    global connection_pool

    # ① 确保数据库存在
    conn = mysql.connector.connect(**base_config)
    cursor = conn.cursor()
    cursor.execute(
        f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
        "DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )
    cursor.close()
    conn.close()

    # ② 创建连接池
    connection_pool = pooling.MySQLConnectionPool(**db_config)
    conn = connection_pool.get_connection()
    cursor = conn.cursor()

    # ③ 建表
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS sessions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL DEFAULT '新对话',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            session_id INT NOT NULL,
            role ENUM('user', 'assistant') NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
            INDEX idx_session_created (session_id, created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""
    )

    conn.commit()
    cursor.close()
    conn.close()
    print("MySQL 数据库 & 表已就绪（sessions, messages）")


def get_connection():
    """从连接池获取连接"""
    return connection_pool.get_connection()
