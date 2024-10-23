from datetime import datetime
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle

from _useful import convert_string_to_date



def create_report(start_date, end_date ,data, name_group_reference):
    groups = {}
    
    for item in data:
        cards = item['cards']
        name = item['name']
        
        for card in cards:
            value_field_reference = card.get(name_group_reference, None)
            
            if value_field_reference:
                if value_field_reference not in groups:
                    groups[value_field_reference] = {'lists': {}}
                    
                if name not in groups[value_field_reference]['lists']:
                    groups[value_field_reference]['lists'][name] = []
                    
                groups[value_field_reference]['lists'][name].append(card)
            
    path_exe = os.path.dirname(os.path.abspath(__file__))

    path_reports = os.path.join(path_exe, 'reports')

    for arquivo in os.listdir(path_reports):
        if arquivo.endswith('.pdf'):
            file_path = os.path.join(path_reports, arquivo)
            
            try:
                os.remove(file_path)
                
            except Exception as err:
                print(f'Error while deleting file: {err}')
            
    for value_field_reference_item, lists in groups.items():
        file_name = f'{path_reports}/{value_field_reference_item.lower()}.pdf'
        pdf = SimpleDocTemplate(file_name, pagesize=letter)
        story = []

        style_title = ParagraphStyle(
            name='Title', fontSize=14, textColor=colors.ReportLabBlue, spaceAfter=10, alignment=1
        )
        style_subtitle = ParagraphStyle(
            name='Sub Title', fontSize=12, textColor=colors.ReportLabBlue, spaceAfter=8, alignment=1
        )
        style_list = ParagraphStyle(
            name='List', fontSize=10, textColor=colors.ReportLabBlue, spaceAfter=10, alignment=1
        )
        style_title_card = ParagraphStyle(
            name='Title Card', fontSize=11, textColor=colors.darkcyan, spaceAfter=5, alignment=4
        )
        style_data = ParagraphStyle(
            name='Data', fontSize=10, textColor=colors.black, spaceAfter=5, alignment=4
        )
        
        story.append(Paragraph(f"<b>Relatório de Atividades dos Desenvolvedores</b>", style_title))
        story.append(Spacer(1, 1))
        
        story.append(Paragraph(f"Desenvolvedor: {value_field_reference_item}", style_subtitle))
        story.append(Spacer(1, 1))
        
        story.append(Paragraph(
            f"Período entre {start_date.strftime('%d/%m/%y')} e {end_date.strftime('%d/%m/%y')}", style_subtitle
        ))
        
        for list, values in lists['lists'].items():
            cards_list = values
            story.append(Spacer(1, 15))
            story.append(Paragraph(f"<b>{list}</b>", style_list))
            story.append(Spacer(1, 15))

            for card_list in cards_list:
                story.append(Paragraph(f"<b>{card_list['title']}</b>", style_title_card))
                story.append(Spacer(1, 5))
                
                story.append(Paragraph(f"""
                    <b>Etiquetas:</b> {', '.join([etiqueta['name'] for etiqueta in card_list['labels']]) or '--'} 
                """, style_data))
                
                story.append(Paragraph(f"""
                    <b>Suporte:</b> {card_list.get('Suporte', '--')}&nbsp;&nbsp;&nbsp;
                    <b>Módulo:</b> {card_list.get('Módulo', '--')}&nbsp;&nbsp;&nbsp; 
                    <b>Nível:</b> {card_list.get('Nível', '--')}&nbsp;&nbsp;&nbsp; 
                    <b>Prioridade:</b> {card_list.get('Prioridade', '--')}
                """, style_data))
                
                story.append(Paragraph(f"""
                    <b>Tempo de programação:</b> {card_list.get('time_in_program', '--')}&nbsp;&nbsp;&nbsp;
                    <b>Tempo total:</b> {card_list.get('total_time', '--')}                   
                """, style_data))
                
                story.append(Spacer(1, 5))

                table_headers = ['Data', 'Origem', 'Destino']
                table_data = [table_headers]

                for movimento in card_list['movements']:
                    date = convert_string_to_date(movimento.get('date', '--'))
                    origin = movimento.get('origin', '--')
                    destiny = movimento.get('destiny', '--')
                    
                    table_data.append([date, origin, destiny])

                table_movements = Table(table_data, colWidths=[pdf.width / len(table_headers)] * len(table_headers))

                style_table_movements = TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ])

                for i in range(1, len(table_data)):
                    if i % 2 == 0:
                        style_table_movements.add('BACKGROUND', (0, i), (-1, i), colors.lavender)

                table_movements.setStyle(style_table_movements)

                story.append(table_movements)
                story.append(Spacer(1, 60))

        pdf.build(story)