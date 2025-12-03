import asyncio
import aiodns
from typing import List, Set, Optional
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse
import httpx
from reconx.utils.logger import logger

class SubdomainEnumerator:
    def __init__(self, domain: str, wordlist: Optional[List[str]] = None, 
                 max_workers: int = 50, timeout: int = 5):
        self.domain = domain.lower().strip()
        self.wordlist = wordlist or self._get_default_wordlist()
        self.max_workers = max_workers
        self.timeout = timeout
        self.found_subdomains: Set[str] = set()
        
    def _get_default_wordlist(self) -> List[str]:
        """قائمة كلمات افتراضية"""
        return [
            'www', 'mail', 'ftp', 'admin', 'test', 'dev', 'staging',
            'api', 'blog', 'webmail', 'cpanel', 'whm', 'webdisk',
            'server', 'ns1', 'ns2', 'ns3', 'ns4', 'm', 'mobile',
            'secure', 'vpn', 'portal', 'app', 'beta', 'demo', 'shop',
            'store', 'support', 'status', 'git', 'svn', 'dns', 'cdn',
            'mx', 'smtp', 'pop', 'imap', 'static', 'assets', 'media',
            'download', 'upload', 'forum', 'community', 'wiki', 'docs',
            'help', 'knowledgebase', 'kb', 'client', 'clients',
            'my', 'account', 'accounts', 'login', 'signin', 'auth',
            'oauth', 'sso', 'idp', 'ldap', 'ad', 'adfs', 'owa',
            'exchange', 'outlook', 'remote', 'ssh', 'ftp', 'sftp',
            'phpmyadmin', 'mysql', 'mariadb', 'postgres', 'mongodb',
            'redis', 'memcached', 'elasticsearch', 'kibana', 'grafana',
            'prometheus', 'alertmanager', 'jenkins', 'gitlab', 'nexus',
            'artifactory', 'sonar', 'sonarqube', 'jira', 'confluence',
            'bitbucket', 'bamboo', 'crowd', 'fisheye', 'crucible'
        ]
    
    async def check_dns(self, subdomain: str, resolver: aiodns.DNSResolver) -> bool:
        """فحص وجود subdomain عبر DNS"""
        try:
            full_domain = f"{subdomain}.{self.domain}"
            await resolver.query(full_domain, 'A')
            return True
        except (aiodns.error.DNSError, Exception):
            return False
    
    async def check_http(self, subdomain: str) -> bool:
        """فحص استجابة HTTP"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                url = f"http://{subdomain}.{self.domain}"
                response = await client.get(url)
                return response.status_code < 500
        except Exception:
            return False
    
    async def passive_enumeration(self) -> Set[str]:
        """اكتشاف سلبي من مصادر عامة"""
        subdomains = set()
        
        # استخدام Google Transparency Report (مثال)
        sources = [
            f"https://crt.sh/?q=%.{self.domain}&output=json",
            f"https://otx.alienvault.com/api/v1/indicators/domain/{self.domain}/passive_dns",
            f"https://api.hackertarget.com/hostsearch/?q={self.domain}",
        ]
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for source in sources:
                try:
                    response = await client.get(source)
                    if response.status_code == 200:
                        # تحليل الاستجابة واستخراج subdomains
                        # (هذا يحتاج إلى معالجة خاصة لكل مصدر)
                        pass
                except Exception as e:
                    logger.debug(f"فشل في المصدر {source}: {e}")
        
        return subdomains
    
    async def brute_force(self) -> Set[str]:
        """هجوم brute force للاكتشاف"""
        found = set()
        resolver = aiodns.DNSResolver()
        
        semaphore = asyncio.Semaphore(self.max_workers)
        
        async def check_with_semaphore(subdomain: str):
            async with semaphore:
                if await self.check_dns(subdomain, resolver):
                    found.add(f"{subdomain}.{self.domain}")
                    logger.info(f"تم العثور على: {subdomain}.{self.domain}")
        
        tasks = [check_with_semaphore(word) for word in self.wordlist]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        return found
    
    async def run(self) -> Set[str]:
        """تشغيل جميع طرق الاكتشاف"""
        logger.info(f"بدء اكتشاف subdomains لـ {self.domain}")
        
        # الاكتشاف السلبي
        logger.info("المرحلة 1: الاكتشاف السلبي...")
        passive_results = await self.passive_enumeration()
        self.found_subdomains.update(passive_results)
        
        # Brute force
        logger.info("المرحلة 2: Brute force...")
        brute_results = await self.brute_force()
        self.found_subdomains.update(brute_results)
        
        # التحقق من الاستجابة HTTP
        logger.info("المرحلة 3: التحقق من استجابة HTTP...")
        http_valid = set()
        semaphore = asyncio.Semaphore(self.max_workers)
        
        async def verify_http(subdomain: str):
            async with semaphore:
                if await self.check_http(subdomain):
                    http_valid.add(subdomain)
        
        tasks = [verify_http(sub) for sub in self.found_subdomains]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # إضافة النطاق الرئيسي نفسه
        self.found_subdomains.add(self.domain)
        
        logger.info(f"اكتمل الاكتشاف. العدد الإجمالي: {len(self.found_subdomains)}")
        return self.found_subdomains