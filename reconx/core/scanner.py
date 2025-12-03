import asyncio
import socket
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor
from reconx.utils.logger import logger

class PortScanner:
    def __init__(self, target: str, ports: Optional[List[int]] = None, 
                 max_workers: int = 100, timeout: float = 1.0):
        self.target = target
        self.ports = ports or self._get_common_ports()
        self.max_workers = max_workers
        self.timeout = timeout
        self.open_ports: Dict[int, str] = {}
        
    def _get_common_ports(self) -> List[int]:
        """قائمة المنافذ الشائعة"""
        return [
            21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445,
            993, 995, 1723, 3306, 3389, 5900, 8080, 8443, 8888, 9000,
            27017, 28017, 5000, 5432, 6379, 9200, 9300
        ]
    
    def _get_service_name(self, port: int) -> str:
        """الحصول على اسم الخدمة المعروفة"""
        service_map = {
            21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP',
            53: 'DNS', 80: 'HTTP', 110: 'POP3', 111: 'RPC',
            135: 'MSRPC', 139: 'NetBIOS', 143: 'IMAP',
            443: 'HTTPS', 445: 'SMB', 993: 'IMAPS',
            995: 'POP3S', 1723: 'PPTP', 3306: 'MySQL',
            3389: 'RDP', 5900: 'VNC', 8080: 'HTTP-Proxy',
            8443: 'HTTPS-Alt', 8888: 'HTTP-Alt', 9000: 'SonarQube',
            27017: 'MongoDB', 28017: 'MongoDB-HTTP',
            5000: 'UPnP', 5432: 'PostgreSQL', 6379: 'Redis',
            9200: 'Elasticsearch', 9300: 'Elasticsearch-Cluster'
        }
        return service_map.get(port, 'Unknown')
    
    async def scan_port(self, port: int) -> Optional[int]:
        """فحص منفذ واحد"""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.target, port),
                timeout=self.timeout
            )
            writer.close()
            await writer.wait_closed()
            return port
        except (ConnectionRefusedError, asyncio.TimeoutError, OSError):
            return None
        except Exception as e:
            logger.debug(f"خطأ في فحص المنفذ {port}: {e}")
            return None
    
    async def scan(self, progress_callback=None) -> Dict[int, str]:
        """فحص جميع المنافذ"""
        logger.info(f"بدء فحص {len(self.ports)} منفذ على {self.target}")
        
        semaphore = asyncio.Semaphore(self.max_workers)
        
        async def scan_with_semaphore(port: int):
            async with semaphore:
                result = await self.scan_port(port)
                if progress_callback:
                    progress_callback()
                return port if result else None
        
        tasks = [scan_with_semaphore(port) for port in self.ports]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # معالجة النتائج
        for result in results:
            if result and isinstance(result, int):
                service = self._get_service_name(result)
                self.open_ports[result] = service
                logger.info(f"منفذ مفتوح: {result} ({service})")
        
        logger.info(f"اكتمل الفحص. المنافذ المفتوحة: {len(self.open_ports)}")
        return self.open_ports