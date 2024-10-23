from datetime import datetime
import os
import tkinter as tk
from tkinter import messagebox

from _loaders import load_lists
from _reports import create_report
from _useful import load_json_data, open_pdfs, save_json_data


LISTS = [
    {'id': '66e0749ddb6a32316530692a', 'name': 'EM PRODUÇÃO'},
    {'id': '670fc77885ff716704c2a3de', 'name': 'PRODUÇÃO SEMANAL'},
    {'id': '66e07495c3b75dd83ce0ea6f', 'name': 'AGUARDANDO VERSÃO'},
    {'id': '66e0748b63da4f3aed540531', 'name': 'EM TESTE'},
    {'id': '66e074e453a926f220482ae2', 'name': 'REVISÃO'},
    {'id': '66e07481a2a22071d85ec0ca', 'name': 'ANDAMENTO'},
    {'id': '66e07457aada4acc60ac9ec1', 'name': 'BACKLOG'},
    {'id': '66e0747a04554f59b86fb0ee', 'name': 'PAUSADAS'},
    {'id': '66e074738b985de2f3df5544', 'name': 'RETORNO'},
]


def load_data():
    name_list_in_program = entry_name_list_in_program.get()
    
    if not name_list_in_program:
        messagebox.showerror("Error", "Lista em programação não informada.")
        
        return
    
    lists = load_lists(LISTS, name_list_in_program)
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    if 'dist' in current_dir:
        path_exe = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        
    else:
        path_exe = os.path.abspath(os.path.join(os.path.dirname(__file__)))

    path_reports = os.path.join(path_exe, 'data')
    
    save_json_data(lists, f'{path_reports}/lists.json')
    
    messagebox.showinfo("Info", "Dados carregados com sucesso.")
    

def generate_report():
    start_date = entry_start_date.get()
    end_date = entry_end_date.get()
    name_group_reference = entry_name_group_reference.get()
        
    if not start_date:
        messagebox.showerror("Error", "Data de início não informada.")
        
        return
    
    else:
        try:
            start_date = datetime.strptime(start_date, '%d/%m/%Y')
    
        except Exception as err:
            messagebox.showerror('Error', f'Data de inicio com formato inválido, DD/MM/YYYY.')
            
            return
        
    if not end_date:
        messagebox.showerror("Error", "Data do fim não informada.")
    
        return
    
    else:
        try:
            end_date = datetime.strptime(end_date, '%d/%m/%Y')
            
        except Exception as err:
            messagebox.showerror('Error', f'Data do fim com formato inválido, DD/MM/YYYY.')
            
            return
    
    if not name_group_reference:
        messagebox.showerror("Error", "Agrupamento não informado.")
        
        return
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    if 'dist' in current_dir:
        path_exe = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        
    else:
        path_exe = os.path.abspath(os.path.join(os.path.dirname(__file__)))
        
    path_reports = os.path.join(path_exe, 'reports')
    path_data_json = os.path.join(path_exe, 'data')
    
    lists = load_json_data(f'{path_data_json}/lists.json')
    
    if not lists:
        messagebox.showerror("Error", "Nenhuma informação encontrada.")
        
        return
    
    create_report(start_date, end_date, lists, name_group_reference)
    
    open_pdfs(path_reports)
    
    messagebox.showinfo("Info", "Relatórios gerados com sucesso.")
    
    
def toggle_fullscreen(event=None):
    janela.attributes("-fullscreen", not janela.attributes("-fullscreen"))

def exit_fullscreen(event=None):
    janela.attributes("-fullscreen", False)
    

janela = tk.Tk()

toggle_fullscreen()

janela.bind("<Escape>", exit_fullscreen)

janela.title("Gerador de Relatórios do Trello")
janela.geometry("600x600")
janela.configure(bg='#f0f0f0')

label_title = tk.Label(janela, text="Bem vindo(a) ao gerador de relatórios do Trello.", font=("Verdana", 16), bg='#f0f0f0')
label_title.pack(pady=30)

label_start_date = tk.Label(janela, text="Data de início:", font=('Verdana', 16), bg='#f0f0f0')
label_start_date.pack()
entry_start_date = tk.Entry(janela, font=('Verdana', 12), width=30)
entry_start_date.insert(0, datetime.now().strftime('%d/%m/%Y'))
entry_start_date.pack(pady=10)

label_end_date = tk.Label(janela, text="Data do fim:", font=('Verdana', 16), bg='#f0f0f0')
label_end_date.pack()
entry_end_date = tk.Entry(janela, font=('Verdana', 12), width=30)
entry_end_date.insert(0, datetime.now().strftime('%d/%m/%Y'))
entry_end_date.pack(pady=10)

label_name_list_in_program = tk.Label(janela, text="Lista em Programação:", font=('Verdana', 16), bg='#f0f0f0')
label_name_list_in_program.pack()
entry_name_list_in_program = tk.Entry(janela, font=('Verdana', 12), width=30)
entry_name_list_in_program.insert(0, 'ANDAMENTO')
entry_name_list_in_program.pack(pady=10)

label_name_group_reference = tk.Label(janela, text="Agrupamento:", font=('Verdana', 16), bg='#f0f0f0')
label_name_group_reference.pack()
entry_name_group_reference = tk.Entry(janela, font=('Verdana', 12), width=30)
entry_name_group_reference.insert(0, 'Desenvolvimento')
entry_name_group_reference.pack(pady=10)

frame = tk.Frame(janela)
frame.pack()

button_print = tk.Button(frame, text="Carregar", command=load_data)
button_print.grid(row=0, column=0)

button_load = tk.Button(frame, text="Imprimir", command=generate_report)
button_load.grid(row=0, column=1)

janela.mainloop()