import re
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse
import ipaddress

def validate_domain(domain: str) -> bool:
    """التحقق من صحة النطاق"""
    pattern = r'^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z]{2,})+$'
    return bool(re.match(pattern, domain))

def validate_ip(ip: str) -> bool:
    """التحقق من صحة عنوان IP"""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def load_wordlist(wordlist_path: Path) -> List[str]:
    """تحميل قائمة الكلمات من ملف"""
    words = []
    try:
        with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                word = line.strip()
                if word and not word.startswith('#'):
                    words.append(word)
    except Exception as e:
        print(f"خطأ في تحميل قائمة الكلمات: {e}")
    
    return words

def extract_domain_from_url(url: str) -> Optional[str]:
    """استخراج النطاق من URL"""
    try:
        parsed = urlparse(url)
        if parsed.netloc:
            return parsed.netloc
    except Exception:
        pass
    return None

def sanitize_filename(filename: str) -> str:
    """تنظيف اسم الملف من الأحرف غير الآمنة"""
    # استبدال الأحرف غير الآمنة
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # إزالة المسافات الزائدة
    filename = re.sub(r'\s+', '_', filename)
    return filename.strip('_.')

# قائمة المنافذ الشائعة
COMMON_PORTS = [
    21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445,
    993, 995, 1723, 3306, 3389, 5900, 8080, 8443, 8888, 9000,
    10000, 11211, 27017, 28017, 5000, 5432, 6379, 9200, 9300,
    8081, 8090, 3000, 4000, 5000, 6000, 7000, 8000, 9001
]