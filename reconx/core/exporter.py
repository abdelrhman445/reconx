import json
import csv
import pandas as pd
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime
from reconx.utils.logger import logger

class DataExporter:
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def save(self, data: Any, output_path: Path, format: str = 'auto'):
        """حفظ البيانات بتنسيقات مختلفة"""
        
        if format == 'auto':
            format = output_path.suffix[1:] if output_path.suffix else 'json'
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format.lower() == 'json':
            self._save_json(data, output_path)
        elif format.lower() == 'csv':
            self._save_csv(data, output_path)
        elif format.lower() == 'txt':
            self._save_txt(data, output_path)
        elif format.lower() == 'html':
            self._save_html(data, output_path)
        else:
            raise ValueError(f"تنسيق غير مدعوم: {format}")
    
    def _save_json(self, data: Any, path: Path):
        """حفظ بتنسيق JSON"""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"تم حفظ JSON في {path}")
    
    def _save_csv(self, data: Any, path: Path):
        """حفظ بتنسيق CSV"""
        if isinstance(data, list):
            if data and isinstance(data[0], dict):
                df = pd.DataFrame(data)
                df.to_csv(path, index=False, encoding='utf-8')
            else:
                with open(path, 'w', encoding='utf-8') as f:
                    for item in data:
                        f.write(f"{item}\n")
        elif isinstance(data, dict):
            # تحويل القاموس إلى قائمة من القواميس
            rows = []
            for key, value in data.items():
                if isinstance(value, dict):
                    row = {'key': key}
                    row.update(value)
                    rows.append(row)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            item['key'] = key
                            rows.append(item)
                        else:
                            rows.append({'key': key, 'value': item})
                else:
                    rows.append({'key': key, 'value': value})
            
            if rows:
                df = pd.DataFrame(rows)
                df.to_csv(path, index=False, encoding='utf-8')
        logger.info(f"تم حفظ CSV في {path}")
    
    def _save_txt(self, data: Any, path: Path):
        """حفظ بتنسيق نصي"""
        with open(path, 'w', encoding='utf-8') as f:
            if isinstance(data, list):
                for item in data:
                    f.write(f"{item}\n")
            elif isinstance(data, dict):
                for key, value in data.items():
                    f.write(f"{key}: {value}\n")
            else:
                f.write(str(data))
        logger.info(f"تم حفظ TXT في {path}")
    
    def _save_html(self, data: Any, path: Path):
        """حفظ بتنسيق HTML"""
        html_content = self._generate_html(data)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logger.info(f"تم حفظ HTML في {path}")
    
    def _generate_html(self, data: Any) -> str:
        """إنشاء تقرير HTML"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html = f"""
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>تقرير ReconX - {timestamp}</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 0 20px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    border-bottom: 3px solid #007bff;
                    padding-bottom: 20px;
                    margin-bottom: 30px;
                }}
                .header h1 {{
                    color: #007bff;
                    margin: 0;
                }}
                .header .subtitle {{
                    color: #666;
                    font-size: 1.1em;
                }}
                .section {{
                    margin-bottom: 30px;
                    padding: 20px;
                    background: #f8f9fa;
                    border-radius: 5px;
                    border-right: 4px solid #007bff;
                }}
                .section h2 {{
                    color: #343a40;
                    margin-top: 0;
                }}
                .data-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 10px;
                }}
                .data-table th {{
                    background: #007bff;
                    color: white;
                    padding: 12px;
                    text-align: right;
                }}
                .data-table td {{
                    padding: 10px;
                    border: 1px solid #dee2e6;
                }}
                .data-table tr:nth-child(even) {{
                    background: #f2f2f2;
                }}
                .status-secure {{ color: green; font-weight: bold; }}
                .status-insecure {{ color: red; font-weight: bold; }}
                .status-warning {{ color: orange; font-weight: bold; }}
                .footer {{
                    text-align: center;
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #dee2e6;
                    color: #666;
                    font-size: 0.9em;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎯 تقرير ReconX</h1>
                    <div class="subtitle">أداة Recon شاملة ومتقدمة - created by NullSpecter</div>
                    <div class="subtitle">تاريخ التقرير: {timestamp}</div>
                </div>
        """
        
        if isinstance(data, dict):
            for key, value in data.items():
                html += f"""
                <div class="section">
                    <h2>{key}</h2>
                """
                
                if isinstance(value, list):
                    html += f"<p>عدد العناصر: {len(value)}</p>"
                    if value and isinstance(value[0], (str, int, float)):
                        html += "<ul>"
                        for item in value[:50]:  # عرض أول 50 عنصر فقط
                            html += f"<li>{item}</li>"
                        html += "</ul>"
                        if len(value) > 50:
                            html += f"<p>... وعناصر أخرى ({len(value) - 50})</p>"
                    elif value and isinstance(value[0], dict):
                        # جدول للبيانات المعقدة
                        if value:
                            keys = value[0].keys()
                            html += """
                            <table class="data-table">
                                <thead>
                                    <tr>
                            """
                            for k in keys:
                                html += f"<th>{k}</th>"
                            html += """
                                    </tr>
                                </thead>
                                <tbody>
                            """
                            for item in value[:20]:  # عرض أول 20 صف
                                html += "<tr>"
                                for k in keys:
                                    cell_value = item.get(k, '')
                                    if isinstance(cell_value, (list, dict)):
                                        cell_value = str(cell_value)[:100] + "..."
                                    html += f"<td>{cell_value}</td>"
                                html += "</tr>"
                            html += """
                                </tbody>
                            </table>
                            """
                            if len(value) > 20:
                                html += f"<p>... وصفوف أخرى ({len(value) - 20})</p>"
                elif isinstance(value, dict):
                    html += "<table class='data-table'><tbody>"
                    for k, v in value.items():
                        html += f"""
                        <tr>
                            <td><strong>{k}</strong></td>
                            <td>{v}</td>
                        </tr>
                        """
                    html += "</tbody></table>"
                else:
                    html += f"<p>{value}</p>"
                
                html += "</div>"
        
        html += f"""
                <div class="footer">
                    <p>تم إنشاء هذا التقرير بواسطة ReconX</p>
                    <p>created by NullSpecter</p>
                    <p>ملاحظة: هذا التقرير لأغراض تعليمية واختبارية فقط</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html