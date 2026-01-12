"""
Модуль генерации PDF-отчетов о контрагентах.
С поддержкой кириллицы через шрифт DejaVuSans.
"""

import os
from datetime import datetime
from typing import Dict, Any
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from risk_analyzer import analyze_risks

# Путь для сохранения отчетов
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

# Регистрируем шрифт с поддержкой кириллицы
FONT_PATH = os.path.join(os.path.dirname(__file__), "DejaVuSans.ttf")
FONT_BOLD_PATH = os.path.join(os.path.dirname(__file__), "DejaVuSans-Bold.ttf")

if os.path.exists(FONT_PATH):
    pdfmetrics.registerFont(TTFont('DejaVuSans', FONT_PATH))
if os.path.exists(FONT_BOLD_PATH):
    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', FONT_BOLD_PATH))


def generate_pdf_report(data: Dict[str, Any], user_id: int) -> str:
    """
    Генерирует PDF-отчет о компании.
    Возвращает путь к созданному файлу.
    """
    inn = data.get('inn', 'unknown')
    filename = f"report_{inn}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(REPORTS_DIR, filename)
    
    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # Используем DejaVuSans для кириллицы
    font_name = 'DejaVuSans' if os.path.exists(FONT_PATH) else 'Helvetica'
    font_bold = 'DejaVuSans-Bold' if os.path.exists(FONT_BOLD_PATH) else 'Helvetica-Bold'
    
    # Кастомные стили с кириллическим шрифтом
    title_style = ParagraphStyle(
        'CustomTitle',
        fontName=font_bold,
        fontSize=16,
        spaceAfter=30,
        alignment=1  # Center
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        fontName=font_bold,
        fontSize=12,
        spaceAfter=12,
        spaceBefore=20
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        fontName=font_name,
        fontSize=10,
        spaceAfter=6
    )
    
    # Собираем данные
    name = data.get('name', {}).get('full_with_opf') or data.get('name', {}).get('short_with_opf') or 'Неизвестно'
    inn = data.get('inn', 'Н/Д')
    ogrn = data.get('ogrn', 'Н/Д')
    kpp = data.get('kpp', 'Н/Д')
    address = data.get('address', {}).get('value', 'Не указан') if isinstance(data.get('address'), dict) else 'Не указан'
    manager_name = data.get('management', {}).get('name', 'Не указан')
    manager_post = data.get('management', {}).get('post', '')
    okved = data.get('okved', 'Н/Д')
    
    # Анализ рисков
    overall_emoji, overall_text, factors = analyze_risks(data)
    
    # Элементы документа
    elements = []
    
    # Заголовок
    elements.append(Paragraph("ОТЧЕТ О ПРОВЕРКЕ КОНТРАГЕНТА", title_style))
    elements.append(Paragraph(f"Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M')}", normal_style))
    elements.append(Spacer(1, 20))
    
    # Общая оценка
    elements.append(Paragraph(f"<b>ОБЩАЯ ОЦЕНКА: {overall_text.upper()}</b>", heading_style))
    elements.append(Spacer(1, 10))
    
    # Основная информация
    elements.append(Paragraph("<b>ОСНОВНЫЕ СВЕДЕНИЯ</b>", heading_style))
    
    info_data = [
        ["Наименование:", name],
        ["ИНН:", inn],
        ["ОГРН:", ogrn],
        ["КПП:", kpp],
        ["Юридический адрес:", address],
        ["Руководитель:", f"{manager_name}" + (f" ({manager_post})" if manager_post else "")],
        ["Основной ОКВЭД:", okved],
    ]
    
    info_table = Table(info_data, colWidths=[5*cm, 12*cm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.grey),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(info_table)
    
    # Светофор рисков
    elements.append(Paragraph("<b>АНАЛИЗ РИСКОВ</b>", heading_style))
    
    risk_data = [["Показатель", "Значение", "Статус"]]
    for factor in factors:
        status = "OK" if factor['emoji'] == "🟢" else ("ВНИМАНИЕ" if factor['emoji'] == "🟡" else "РИСК")
        risk_data.append([factor['name'], factor['value'], status])
    
    risk_table = Table(risk_data, colWidths=[5*cm, 8*cm, 4*cm])
    risk_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTNAME', (0, 0), (-1, 0), font_bold),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(risk_table)
    
    # Подпись
    elements.append(Spacer(1, 40))
    elements.append(Paragraph("_" * 60, normal_style))
    footer_style = ParagraphStyle('Footer', fontName=font_name, fontSize=8, textColor=colors.grey)
    elements.append(Paragraph("Отчет сформирован автоматически системой проверки контрагентов", footer_style))
    
    # Генерируем PDF
    doc.build(elements)
    
    return filepath
