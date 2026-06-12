import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'tutor.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 上传配置
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    # 分页配置
    POSTS_PER_PAGE = 10

    # 管理员账号（优先读环境变量）
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@tutor.com')
