import httpx
from typing import Dict, Any, Tuple
from reconx.utils.logger import logger

class HeaderAnalyzer:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
    
    async def analyze(self, url: str) -> Tuple[Dict[str, str], Dict[str, Dict]]:
        """تحليل رؤوس HTTP"""
        if not url.startswith(('http://', 'https://')):
            url = f"http://{url}"
        
        headers = {}
        security_info = {}
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url)
                
                # جمع جميع الرؤوس
                for key, value in response.headers.items():
                    headers[key] = value
                
                # تحليل الأمان
                security_info = self._analyze_security_headers(headers)
                
                # معلومات إضافية
                security_info['https_redirect'] = {
                    'status': 'secure' if url.startswith('https') else 'insecure',
                    'recommendation': 'استخدام HTTPS إلزامي'
                }
                
        except Exception as e:
            logger.error(f"خطأ في تحليل الرؤوس لـ {url}: {e}")
        
        return headers, security_info
    
    def _analyze_security_headers(self, headers: Dict[str, str]) -> Dict[str, Dict]:
        """تحليل رؤوس الأمان"""
        security = {}
        
        # Content-Security-Policy
        if 'Content-Security-Policy' in headers:
            security['csp'] = {
                'status': 'secure',
                'value': headers['Content-Security-Policy'][:100],
                'recommendation': 'CSP موجود - جيد'
            }
        else:
            security['csp'] = {
                'status': 'insecure',
                'recommendation': 'إضافة Content-Security-Policy'
            }
        
        # X-Frame-Options
        if 'X-Frame-Options' in headers:
            security['x_frame_options'] = {
                'status': 'secure',
                'value': headers['X-Frame-Options'],
                'recommendation': 'محمي من clickjacking'
            }
        else:
            security['x_frame_options'] = {
                'status': 'insecure',
                'recommendation': 'إضافة X-Frame-Options: DENY أو SAMEORIGIN'
            }
        
        # X-Content-Type-Options
        if 'X-Content-Type-Options' in headers and headers['X-Content-Type-Options'] == 'nosniff':
            security['x_content_type_options'] = {
                'status': 'secure',
                'recommendation': 'MIME sniffing معطل'
            }
        else:
            security['x_content_type_options'] = {
                'status': 'insecure',
                'recommendation': 'إضافة X-Content-Type-Options: nosniff'
            }
        
        # Strict-Transport-Security
        if 'Strict-Transport-Security' in headers:
            security['hsts'] = {
                'status': 'secure',
                'value': headers['Strict-Transport-Security'][:100],
                'recommendation': 'HSTS مفعل'
            }
        else:
            security['hsts'] = {
                'status': 'insecure',
                'recommendation': 'إضافة Strict-Transport-Security header'
            }
        
        # Referrer-Policy
        if 'Referrer-Policy' in headers:
            security['referrer_policy'] = {
                'status': 'secure',
                'value': headers['Referrer-Policy'],
                'recommendation': 'سياسة Referrer موجودة'
            }
        else:
            security['referrer_policy'] = {
                'status': 'insecure',
                'recommendation': 'إضافة Referrer-Policy'
            }
        
        # X-XSS-Protection
        if 'X-XSS-Protection' in headers:
            security['xss_protection'] = {
                'status': 'warning' if headers['X-XSS-Protection'] == '0' else 'secure',
                'value': headers['X-XSS-Protection'],
                'recommendation': 'تفعيل X-XSS-Protection' if headers['X-XSS-Protection'] == '0' else 'XSS protection مفعل'
            }
        else:
            security['xss_protection'] = {
                'status': 'insecure',
                'recommendation': 'إضافة X-XSS-Protection: 1; mode=block'
            }
        
        return security