import database.database as database
from tkinter import ttk, messagebox
import utils.export_pdf as utilsPdf
from tkinter.simpledialog import askstring

def gerar_relatorio_geral():
    lancamentos = database.buscar_lancamentos_do_banco()
    if not lancamentos:
        messagebox.showinfo("Relatório Geral", "Nenhum lançamento foi registrado.")
        return

    # Perguntar o nome do arquivo ao usuário
    nome_arquivo = askstring("Salvar Relatório", "Digite o nome do arquivo (sem extensão):")

    # Verificar se o nome do arquivo foi fornecido
    if not nome_arquivo:
        messagebox.showwarning("Erro", "Nome do arquivo não fornecido. Relatório não será salvo.")
        return

    # Adicionar extensão .pdf ao nome do arquivo, caso não tenha sido fornecido
    if not nome_arquivo.endswith(".pdf"):
        nome_arquivo += ".pdf"

    # Exportar para PDF com o nome fornecido
    utilsPdf.exportar_para_pdf(lancamentos, nome_arquivo, "Relatório Geral de Lançamentos")

# Função para gerar Relatório Geral - A Pagar
def gerar_relatorio_geral_a_pagar():
    lancamentos = database.buscar_lancamentos_por_status("A Pagar")
    if not lancamentos:
        messagebox.showinfo("Relatório Geral - A Pagar", "Nenhum lançamento com status 'A Pagar'.")
        return

    nome_arquivo = askstring("Salvar Relatório", "Digite o nome do arquivo (sem extensão):")
    if not nome_arquivo:
        messagebox.showwarning("Erro", "Nome do arquivo não fornecido. Relatório não será salvo.")
        return
    nome_arquivo += ".pdf" if not nome_arquivo.endswith(".pdf") else ""

    utilsPdf.exportar_para_pdf(lancamentos, nome_arquivo, "Relatório Geral - A Pagar")