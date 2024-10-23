import os
import platform
import subprocess
import json
from datetime import datetime, timedelta
from tkinter import messagebox


def convert_string_to_date(date_in_string):
    try:
        data = datetime.fromisoformat(date_in_string.replace("Z", "+00:00"))
        
        return data.strftime('%d/%m/%y %H:%M:%S')
    
    except Exception as err:
        print(f'Error while converting string to date. {err}')
        
        return '--'
    
    
def format_timedelta_display(value):
    total_seconds = int(value.total_seconds())
    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    return f"{abs(days)}d {hours:02}:{minutes:02}:{seconds:02}"
    
    
def calculate_working_hours(start, end):
    work_start = start.replace(hour=8, minute=0, second=0, microsecond=0)
    work_end = start.replace(hour=18, minute=0, second=0, microsecond=0)
    
    if start < work_start:
        start = work_start
    
    if end > work_end:
        end = work_end

    if start >= work_end or end <= work_start:
        return timedelta()

    return end - start

    
def load_json_data(path):
    try:
        with open(path) as f:
            data = json.load(f)
        
        return data
    
    except Exception as err:
        print(f'Error while loading data from {path}. {err}')
        
        return {}


def save_json_data(data, path):
    try:
        with open(path, 'w') as f:
            json.dump(data, f)
            
    except Exception as err:
        print(f'Error while saving data: {err}')
        
        
def open_pdfs(path):
    sistema = platform.system()
    
    try:
        pdfs = [f for f in os.listdir(path) if f.endswith('.pdf')]

        if not pdfs:
            messagebox.showinfo("Info", "Nenhum PDF encontrado na pasta.")

            return

        for pdf in pdfs:
            path_pdf = os.path.join(path, pdf)
            
            if sistema == "Windows":
                os.startfile(path_pdf)
            
            elif sistema == "Darwin":
                subprocess.run(["open", path_pdf])
            
            elif sistema == "Linux":
                subprocess.run(["xdg-open", path_pdf])
            
            else:
                messagebox.showerror("Erro", f"Sistema operacional {sistema} não suportado.")
            
                break

            
    except Exception as err:
        messagebox.showerror("Erro", f"Não foi possível abrir o arquivo PDF: {err}")
