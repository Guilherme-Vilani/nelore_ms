import utils.utils as utils
from fpdf import FPDF
import logging
from datetime import datetime
from tkinter import ttk, messagebox

# Função para exportar o relatório em PDF com cores, logo, formatação de valores e data corrigida
def exportar_para_pdf(lancamentos, nome_arquivo, titulo_relatorio):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Adicionar o logotipo
    caminho_logo = r'logo.jpg'
    try:
        pdf.image(caminho_logo, x=10, y=8, w=30)
    except:
        logging.error(f"Erro ao carregar logotipo para o relatório.")

    # Título do relatório
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, titulo_relatorio.upper(), ln=True, align='C')

    pdf.ln(15)

    # Obter a data e hora atuais
    data_emissao = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    pdf.set_font('Arial', 'I', 10)
    pdf.cell(0, 10, f"Data de emissão: {data_emissao}", ln=True, align='L')

    pdf.ln(5)

    # Definir cores e cabeçalho da tabela
    pdf.set_fill_color(200, 220, 255)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', 'B', 12)

    colunas = ["Id", "Data", "Empresa", "Atividade", "Tipo", "Valor", "Conta", "Vencimento"]
    col_widths = [20, 30, 60, 60, 10, 25, 40, 25]

    for col, width in zip(colunas, col_widths):
        pdf.cell(width, 10, col, border=1, align='C', fill=True)
    pdf.ln()

    pdf.set_fill_color(230, 240, 255)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 10)

    total_credito = 0.0
    total_debito = 0.0
    fill = False

    for row in lancamentos:
        data_formatada = str(utils.formatar_data(row.get('Data', '')) or '')
        data_vencimento_formatada = str(utils.formatar_data(row.get('Data_Vencimento', '')) or '')
        tipo_formatado = "C" if row.get('Tipo', '').lower() == 'crédito' else "D"

        pdf.cell(col_widths[0], 10, str(row.get('Id', '')), border=1, align='C', fill=fill)
        pdf.cell(col_widths[1], 10, data_formatada, border=1, align='C', fill=fill)
        pdf.cell(col_widths[2], 10, str(row.get('Empresa', '')), border=1, align='C', fill=fill)
        pdf.cell(col_widths[3], 10, str(row.get('Atividade', '')), border=1, align='C', fill=fill)
        pdf.cell(col_widths[4], 10, tipo_formatado, border=1, align='C', fill=fill)
        pdf.cell(col_widths[5], 10, utils.formatar_moeda(row.get('Valor', 0)).replace('R$', 'R$ '), border=1, align='C', fill=fill)
        pdf.cell(col_widths[6], 10, str(row.get('Conta', '')), border=1, align='C', fill=fill)
        pdf.cell(col_widths[7], 10, data_vencimento_formatada, border=1, align='C', fill=fill)
        pdf.ln()

        valor = utils.converter_valor_para_float(row.get('Valor', 0))
        if row.get('Tipo', '').lower() == 'crédito':
            total_credito += valor
        else:
            total_debito += valor

        fill = not fill

    saldo = total_credito - total_debito

    pdf.ln(10)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Total Crédito: {utils.formatar_moeda(total_credito)}", ln=True, align='L')
    pdf.cell(0, 10, f"Total Débito: {utils.formatar_moeda(total_debito)}", ln=True, align='L')
    pdf.cell(0, 10, f"Saldo: {utils.formatar_moeda(saldo)}", ln=True, align='L')

    try:
        pdf.output(nome_arquivo)
        messagebox.showinfo("Sucesso", f"Relatório salvo como {nome_arquivo}")
    except Exception as e:
        logging.error(f"Erro ao gerar PDF: {e}")
        messagebox.showerror("Erro", "Erro ao salvar o relatório em PDF.")