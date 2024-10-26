# report.py
from fpdf import FPDF
from datetime import datetime
import matplotlib.pyplot as plt
import logging
from utils.utils import formatar_moeda, formatar_data, converter_valor_para_float
from database.database import conectar_banco
import sqlite3

def exportar_para_pdf(lancamentos, nome_arquivo, titulo_relatorio):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    caminho_logo = r'logo.jpg'
    try:
        pdf.image(caminho_logo, x=10, y=8, w=30)
    except:
        logging.error("Erro ao carregar logotipo para o relatório.")

    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, titulo_relatorio.upper(), ln=True, align='C')
    pdf.ln(15)

    data_emissao = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    pdf.set_font('Arial', 'I', 10)
    pdf.cell(0, 10, f"Data de emissão: {data_emissao}", ln=True, align='L')

    colunas = ["Id", "Data", "Empresa", "Atividade", "Tipo", "Valor", "Conta", "Vencimento"]
    col_widths = [20, 30, 60, 60, 10, 25, 40, 25]
    fill = False
    total_credito = total_debito = 0.0

    for row in lancamentos:
        data_formatada = str(formatar_data(row.get('Data', '')))
        tipo_formatado = "C" if row.get('Tipo', '').lower() == 'crédito' else "D"
        pdf.cell(col_widths[0], 10, str(row.get('Id', '')), border=1, align='C', fill=fill)
        pdf.cell(col_widths[1], 10, data_formatada, border=1, align='C', fill=fill)
        pdf.cell(col_widths[2], 10, str(row.get('Empresa', '')), border=1, align='C', fill=fill)
        pdf.cell(col_widths[3], 10, str(row.get('Atividade', '')), border=1, align='C', fill=fill)
        pdf.cell(col_widths[4], 10, tipo_formatado, border=1, align='C', fill=fill)
        pdf.cell(col_widths[5], 10, formatar_moeda(row.get('Valor', 0)).replace('R$', 'R$ '), border=1, align='C', fill=fill)
        fill = not fill
        valor = converter_valor_para_float(row.get('Valor', 0))
        if row.get('Tipo', '').lower() == 'crédito':
            total_credito += valor
        else:
            total_debito += valor
    pdf.output(nome_arquivo)

def gerar_grafico_barras():
    conexao = conectar_banco()
    if conexao is None:
        logging.error("Erro ao conectar ao banco de dados.")
        return

    query = """
        SELECT Conta, 
               SUM(CASE WHEN Tipo = 'C' THEN Valor ELSE 0 END) AS Total_Credito,
               SUM(CASE WHEN Tipo = 'D' THEN Valor ELSE 0 END) AS Total_Debito
        FROM Lancamentos
        GROUP BY Conta
    """
    try:
        cursor = conexao.cursor()
        cursor.execute(query)
        resultados = cursor.fetchall()
        
        contas, totais_credito, totais_debito = zip(*resultados)
        fig, ax = plt.subplots(figsize=(10, 6))
        largura_barra = 0.35
        indices = range(len(contas))
        ax.bar([i - largura_barra / 2 for i in indices], totais_credito, largura_barra, label='Crédito')
        ax.bar([i + largura_barra / 2 for i in indices], totais_debito, largura_barra, label='Débito')
        ax.set_xticks(indices)
        ax.set_xticklabels(contas, rotation=45)
        ax.legend()
        plt.tight_layout()
        plt.show()
    except sqlite3.Error as e:
        logging.error(f"Erro ao gerar gráfico de barras: {e}")
    finally:
        cursor.close()
        conexao.close()
