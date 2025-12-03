# إصلاح ملف fingerprint.py
import httpx
import re
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class Fingerprinter:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        
    async def analyze(self, url: str, detailed: bool = False) -> Dict[str, Any]:
        """تحليل التواقيع"""
        if not url.startswith(('http://', 'https://')):
            url = f"http://{url}"
        
        results = {
            "url": url,
            "server_info": {},
            "technologies": [],
            "security_headers": {},
            "page_info": {}
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                
                # تحليل رأس Server
                if 'Server' in response.headers:
                    results['server_info']['server'] = response.headers['Server']
                
                # تحليل رأس X-Powered-By
                if 'X-Powered-By' in response.headers:
                    results['server_info']['x_powered_by'] = response.headers['X-Powered-By']
                
                # اكتشاف التقنيات
                results['technologies'] = await self._detect_technologies(response)
                
                # تحليل الصفحة
                if detailed:
                    results['page_info'] = await self._analyze_page(response)
                
                # تحليل رؤوس الأمان
                security_headers = ['X-Frame-Options', 'Content-Security-Policy', 
                                  'X-Content-Type-Options', 'Strict-Transport-Security',
                                  'Referrer-Policy']
                for header in security_headers:
                    if header in response.headers:
                        results['security_headers'][header] = response.headers[header]
                
                # معلومات أساسية
                results['status_code'] = response.status_code
                results['content_type'] = response.headers.get('Content-Type', '')
                results['content_length'] = len(response.content)
                
        except Exception as e:
            logger.error(f"خطأ في تحليل {url}: {e}")
            results['error'] = str(e)
        
        return results
    
    async def _detect_technologies(self, response: httpx.Response) -> List[str]:
        """اكتشاف التقنيات المستخدمة"""
        technologies = []
        content = response.text.lower()
        headers = {k.lower(): v for k, v in response.headers.items()}
        
        # اكتشاف خوادم الويب
        server_patterns = {
            'Apache': ['apache', 'httpd'],
            'Nginx': ['nginx'],
            'IIS': ['microsoft-iis', 'iis'],
            'Cloudflare': ['cloudflare'],
            'CloudFront': ['cloudfront']
        }
        
        for tech, patterns in server_patterns.items():
            for pattern in patterns:
                if pattern in content or any(pattern in v.lower() for v in response.headers.values()):
                    technologies.append(tech)
                    break
        
        return list(set(technologies))
    
    async def _analyze_page(self, response: httpx.Response) -> Dict[str, Any]:
        """تحليل مفصل للصفحة"""
        page_info = {}
        
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # العناوين
            page_info['title'] = soup.title.string if soup.title else None
            
            # وسم Meta
            meta_tags = {}
            for meta in soup.find_all('meta'):
                if meta.get('name'):
                    meta_tags[meta.get('name')] = meta.get('content', '')
                elif meta.get('property'):
                    meta_tags[meta.get('property')] = meta.get('content', '')
            page_info['meta_tags'] = meta_tags
            
        except Exception as e:
            logger.debug(f"خطأ في تحليل الصفحة: {e}")
        
        return page_info
