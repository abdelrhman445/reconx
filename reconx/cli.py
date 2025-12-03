#!/usr/bin/env python3
"""
ReconX - أداة Recon شاملة ومتقدمة
created by NullSpecter
"""

import typer
import asyncio
from pathlib import Path
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from reconx.core.enumerator import SubdomainEnumerator
from reconx.core.scanner import PortScanner
from reconx.core.fingerprint import Fingerprinter
from reconx.core.headers import HeaderAnalyzer
from reconx.core.exporter import DataExporter
from reconx.utils.logger import setup_logger
from reconx.utils.helpers import validate_domain, load_wordlist

app = typer.Typer(help="ReconX - أداة Recon شاملة ومتقدمة")
console = Console()
logger = setup_logger()

@app.command()
def enum(
    domain: str = typer.Argument(..., help="النطاق الرئيسي للبحث"),
    wordlist: Optional[Path] = typer.Option(None, "--wordlist", "-w", help="ملف كلمات للـ brute-force"),
    threads: int = typer.Option(50, "--threads", "-t", help="عدد الثريدات"),
    timeout: int = typer.Option(5, "--timeout", help="وقت الانتظار لكل طلب"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="ملف الإخراج")
):
    """اكتشاف Subdomains من مصادر متعددة"""
    
    if not validate_domain(domain):
        console.print("[red]❌ نطاق غير صالح[/red]")
        raise typer.Exit(1)
    
    console.print(f"[bold cyan]🎯 بدء اكتشاف Subdomains لـ {domain}[/bold cyan]")
    
    # تحميل قائمة الكلمات
    words = []
    if wordlist:
        if wordlist.exists():
            words = load_wordlist(wordlist)
            console.print(f"[green]📚 تم تحميل {len(words)} كلمة من القائمة[/green]")
        else:
            console.print(f"[red]❌ ملف القائمة غير موجود: {wordlist}[/red]")
            raise typer.Exit(1)
    
    # إنشاء Enumerator وتشغيله
    enumerator = SubdomainEnumerator(
        domain=domain,
        wordlist=words,
        max_workers=threads,
        timeout=timeout
    )
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("جاري الاكتشاف...", total=None)
        subdomains = asyncio.run(enumerator.run())
        progress.update(task, completed=True)
    
    # عرض النتائج
    if subdomains:
        table = Table(title=f"Subdomains المكتشفة ({len(subdomains)})")
        table.add_column("الرقم", style="cyan")
        table.add_column("Subdomain", style="green")
        
        for i, subdomain in enumerate(sorted(subdomains), 1):
            table.add_row(str(i), subdomain)
        
        console.print(table)
        
        # حفظ النتائج إذا طُلب
        if output:
            exporter = DataExporter()
            exporter.save(list(subdomains), output, format='auto')
            console.print(f"[green]✅ تم حفظ النتائج في {output}[/green]")
    else:
        console.print("[yellow]⚠️ لم يتم العثور على أي subdomains[/yellow]")

@app.command()
def scan(
    target: str = typer.Argument(..., help="الهدف (IP أو نطاق)"),
    ports: Optional[str] = typer.Option(None, "--ports", "-p", help="قائمة المنافذ (مثال: 80,443,8080)"),
    top_ports: Optional[int] = typer.Option(100, "--top-ports", help="عدد المنافذ الشائعة للمسح"),
    threads: int = typer.Option(100, "--threads", "-t", help="عدد الثريدات"),
    timeout: float = typer.Option(1.0, "--timeout", help="وقت الانتظار لكل منفذ"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="ملف الإخراج")
):
    """فحص المنافذ المفتوحة"""
    
    console.print(f"[bold cyan]🔍 بدء فحص المنافذ لـ {target}[/bold cyan]")
    
    # تحليل قائمة المنافذ
    port_list = []
    if ports:
        try:
            for port in ports.split(','):
                if '-' in port:
                    start, end = map(int, port.split('-'))
                    port_list.extend(range(start, end + 1))
                else:
                    port_list.append(int(port))
        except ValueError:
            console.print("[red]❌ تنسيق المنافذ غير صحيح[/red]")
            raise typer.Exit(1)
    else:
        # استخدام المنافذ الشائعة
        from reconx.utils.helpers import COMMON_PORTS
        port_list = COMMON_PORTS[:top_ports]
    
    scanner = PortScanner(
        target=target,
        ports=port_list,
        max_workers=threads,
        timeout=timeout
    )
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task(f"فحص {len(port_list)} منفذ...", total=len(port_list))
        
        def update_progress():
            progress.update(task, advance=1)
        
        open_ports = asyncio.run(scanner.scan(progress_callback=update_progress))
    
    # عرض النتائج
    if open_ports:
        table = Table(title=f"المنافذ المفتوحة على {target}")
        table.add_column("Port", style="cyan")
        table.add_column("النوع", style="green")
        table.add_column("الخدمة", style="yellow")
        
        for port, service in open_ports.items():
            table.add_row(str(port), "TCP", service)
        
        console.print(table)
        
        # حفظ النتائج
        if output:
            data = [{"port": port, "service": service} for port, service in open_ports.items()]
            exporter = DataExporter()
            exporter.save(data, output, format='auto')
            console.print(f"[green]✅ تم حفظ النتائج في {output}[/green]")
    else:
        console.print("[yellow]⚠️ لم يتم العثور على منافذ مفتوحة[/yellow]")

@app.command()
def fingerprint(
    url: str = typer.Argument(..., help="URL للفحص"),
    detailed: bool = typer.Option(False, "--detailed", "-d", help="فحص مفصل"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="ملف الإخراج")
):
    """فحص تواقيع الخادم والتقنيات المستخدمة"""
    
    console.print(f"[bold cyan]🔬 بدء فحص التواقيع لـ {url}[/bold cyan]")
    
    fingerprinter = Fingerprinter()
    results = asyncio.run(fingerprinter.analyze(url, detailed=detailed))
    
    # عرض النتائج
    if results and 'error' not in results:
        table = Table(title=f"نتائج Fingerprinting لـ {url}")
        table.add_column("الفئة", style="cyan")
        table.add_column("القيمة", style="green")
        
        for category, data in results.items():
            if isinstance(data, dict):
                for key, value in data.items():
                    table.add_row(f"{category}.{key}", str(value)[:100])
            elif isinstance(data, list):
                table.add_row(category, ", ".join(map(str, data))[:100])
            else:
                table.add_row(category, str(data)[:100])
        
        console.print(table)
        
        # حفظ النتائج
        if output:
            exporter = DataExporter()
            exporter.save(results, output, format='auto')
            console.print(f"[green]✅ تم حفظ النتائج في {output}[/green]")
    else:
        error_msg = results.get('error', 'خطأ غير معروف') if isinstance(results, dict) else 'خطأ غير معروف'
        console.print(f"[red]❌ فشل في الفحص: {error_msg}[/red]")

@app.command()
def headers(
    url: str = typer.Argument(..., help="URL لتحليل الرؤوس"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="ملف الإخراج")
):
    """تحليل رؤوس HTTP للأمان"""
    
    console.print(f"[bold cyan]📋 بدء تحليل الرؤوس لـ {url}[/bold cyan]")
    
    analyzer = HeaderAnalyzer()
    headers, security_info = asyncio.run(analyzer.analyze(url))
    
    # عرض الرؤوس
    if headers:
        table = Table(title=f"رؤوس HTTP لـ {url}")
        table.add_column("الرأس", style="cyan")
        table.add_column("القيمة", style="green")
        
        for header, value in headers.items():
            table.add_row(header, str(value)[:100])
        
        console.print(table)
    
    # عرض معلومات الأمان
    if security_info:
        console.print("\n[bold]معلومات أمنية:[/bold]")
        security_table = Table()
        security_table.add_column("البند", style="cyan")
        security_table.add_column("الحالة", style="green")
        security_table.add_column("التوصية", style="yellow")
        
        for check, data in security_info.items():
            status = "✅" if data['status'] == 'secure' else "❌" if data['status'] == 'insecure' else "⚠️"
            security_table.add_row(check, status, data.get('recommendation', '')[:50])
        
        console.print(security_table)
    
    # حفظ النتائج
    if output and headers:
        data = {
            "url": url,
            "headers": dict(headers),
            "security_analysis": security_info
        }
        exporter = DataExporter()
        exporter.save(data, output, format='auto')
        console.print(f"[green]✅ تم حفظ النتائج في {output}[/green]")

@app.command()
def run(
    domain: str = typer.Argument(..., help="النطاق الرئيسي"),
    pipeline: str = typer.Option("enum,scan,fingerprint", "--pipeline", "-p", 
                               help="سلسلة المهام (enum,scan,fingerprint,headers)"),
    output: Path = typer.Option(Path("reconx_report.json"), "--output", "-o", 
                               help="ملف الإخراج النهائي"),
    threads: int = typer.Option(50, "--threads", "-t", help="عدد الثريدات")
):
    """تشغيل سلسلة مهام متكاملة"""
    
    if not validate_domain(domain):
        console.print("[red]❌ نطاق غير صالح[/red]")
        raise typer.Exit(1)
    
    console.print(f"[bold cyan]🚀 بدء سلسلة Recon على {domain}[/bold cyan]")
    console.print(f"[yellow]📋 خطوات التنفيذ: {pipeline}[/yellow]\n")
    
    results = {"domain": domain, "pipeline": pipeline.split(",")}
    
    tasks = pipeline.split(",")
    
    for task in tasks:
        task = task.strip()
        
        if task == "enum":
            console.print("\n[bold]🔍 مرحلة اكتشاف Subdomains...[/bold]")
            try:
                enumerator = SubdomainEnumerator(domain=domain, max_workers=threads)
                subdomains = asyncio.run(enumerator.run())
                results["subdomains"] = list(subdomains)
                console.print(f"[green]✅ تم اكتشاف {len(subdomains)} subdomain[/green]")
            except Exception as e:
                console.print(f"[red]❌ خطأ في اكتشاف Subdomains: {e}[/red]")
                results["subdomains"] = []
            
        elif task == "scan":
            console.print("\n[bold]🔍 مرحلة فحص المنافذ...[/bold]")
            if "subdomains" in results and results["subdomains"]:
                results["port_scan"] = {}
                for subdomain in list(results["subdomains"])[:5]:  # مسح أول 5 subdomains فقط
                    console.print(f"   فحص {subdomain}...")
                    try:
                        scanner = PortScanner(target=subdomain, max_workers=threads)
                        open_ports = asyncio.run(scanner.scan())
                        if open_ports:
                            results["port_scan"][subdomain] = open_ports
                    except Exception as e:
                        console.print(f"   [red]خطأ في فحص {subdomain}: {e}[/red]")
            else:
                console.print("[yellow]⚠️ تخطي فحص المنافذ (لم يتم اكتشاف subdomains)[/yellow]")
                
        elif task == "fingerprint":
            console.print("\n[bold]🔬 مرحلة Fingerprinting...[/bold]")
            if "subdomains" in results and results["subdomains"]:
                results["fingerprint"] = {}
                fingerprinter = Fingerprinter()
                
                # فحص أول 3 subdomains فقط لتوفير الوقت
                for subdomain in list(results["subdomains"])[:3]:
                    url = f"http://{subdomain}"
                    console.print(f"   فحص {url}...")
                    try:
                        fp_result = asyncio.run(fingerprinter.analyze(url))
                        results["fingerprint"][subdomain] = fp_result
                    except Exception as e:
                        console.print(f"   [red]خطأ في فحص {subdomain}: {e}[/red]")
                        results["fingerprint"][subdomain] = {"error": str(e)}
            else:
                console.print("[yellow]⚠️ تخطي fingerprinting (لم يتم اكتشاف subdomains)[/yellow]")
                
        elif task == "headers":
            console.print("\n[bold]📋 مرحلة تحليل الرؤوس...[/bold]")
            if "subdomains" in results and results["subdomains"]:
                results["headers"] = {}
                analyzer = HeaderAnalyzer()
                
                # تحليل أول subdomain فقط
                main_subdomain = f"http://{results['subdomains'][0]}"
                console.print(f"   تحليل {main_subdomain}...")
                try:
                    headers, security = asyncio.run(analyzer.analyze(main_subdomain))
                    results["headers"][main_subdomain] = {
                        "headers": dict(headers),
                        "security_analysis": security
                    }
                except Exception as e:
                    console.print(f"   [red]خطأ في تحليل الرؤوس: {e}[/red]")
                    results["headers"][main_subdomain] = {"error": str(e)}
    
    # حفظ التقرير النهائي
    try:
        exporter = DataExporter()
        exporter.save(results, output, format='auto')
        
        console.print(f"\n[bold green]🎉 تم الانتهاء من سلسلة Recon![/bold green]")
        console.print(f"[green]📄 تم حفظ التقرير في: {output}[/green]")
        
        # عرض ملخص
        console.print("\n[bold]📊 ملخص النتائج:[/bold]")
        if "subdomains" in results:
            console.print(f"   Subdomains: {len(results['subdomains'])}")
        if "port_scan" in results:
            total_ports = sum(len(ports) for ports in results["port_scan"].values())
            console.print(f"   منافذ مفتوحة: {total_ports}")
        if "fingerprint" in results:
            console.print(f"   خدمات محللة: {len(results['fingerprint'])}")
    except Exception as e:
        console.print(f"[red]❌ خطأ في حفظ التقرير: {e}[/red]")

@app.command()
def export(
    data: Path = typer.Argument(..., help="ملف البيانات المدخل"),
    format: str = typer.Option("json", "--format", "-f", 
                             help="صيغة الإخراج (json, csv, html, txt)"),
    output: Path = typer.Argument(..., help="ملف الإخراج")
):
    """تصدير البيانات إلى صيغ مختلفة"""
    
    if not data.exists():
        console.print(f"[red]❌ الملف {data} غير موجود[/red]")
        raise typer.Exit(1)
    
    console.print(f"[cyan]🔄 تصدير {data} إلى {format.upper()}...[/cyan]")
    
    exporter = DataExporter()
    
    try:
        # قراءة الملف المدخل
        import json
        with open(data, 'r', encoding='utf-8') as f:
            if data.suffix == '.json':
                content = json.load(f)
            else:
                content = f.read()
        
        # التصدير
        exporter.save(content, output, format=format)
        console.print(f"[green]✅ تم التصدير بنجاح إلى {output}[/green]")
        
    except Exception as e:
        console.print(f"[red]❌ خطأ في التصدير: {e}[/red]")
        raise typer.Exit(1)

@app.callback()
def main():
    """
    ReconX - أداة Recon شاملة ومتقدمة
    
    created by NullSpecter
    """
    pass

if __name__ == "__main__":
    app()