# إنشاء ملف logger.py صحيح
import logging
import sys
from pathlib import Path
from datetime import datetime

def setup_logger(name: str = "reconx", level: int = logging.INFO) -> logging.Logger:
    """إعداد وتسجيل الأحداث"""
    
    # إنشاء المسار للسجلات
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # اسم ملف السجل
    timestamp = datetime.now().strftime("%Y%m%d")
    log_file = log_dir / f"reconx_{timestamp}.log"
    
    # إعداد الـ Logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # منع انتشار السجلات
    logger.propagate = False
    
    # إعداد التنسيق
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # معالج للملف
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # معالج للطرفية
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    
    # إضافة المعالجات
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger

# إنشاء logger افتراضي
logger = setup_logger()
