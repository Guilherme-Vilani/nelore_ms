import pyodbc
import logging
import tkinter as tk
from tkinter import messagebox
from tkinter.simpledialog import askstring
from fpdf import FPDF
from datetime import datetime
import locale
import decimal
from tkinter import ttk
import matplotlib.pyplot as plt

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# Configurando o logging para registrar erros
logging.basicConfig(filename='erros_sistema_contabil.log', level=logging.ERROR,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Função para conectar ao banco de dados SQLite
def conectar_banco():
    try:
        conexao = pyodbc.connect(
            'DRIVER={SQL Server};'
            'SERVER=DESKTOP-2BE72MC;'  # Altere conforme necessário
            'DATABASE=ControleContabil;'  # Nome do banco de dados
            'Trusted_Connection=yes;'
        )
        return conexao
    except Exception as e:
        logging.error(f"Erro ao conectar ao banco de dados: {e}")
        messagebox.showerror("Erro", "Erro ao conectar ao banco de dados.")
        return None

# Função para formatar o valor em Real Brasileiro
def formatar_moeda(valor):
    try:
        valor = float(valor)  # Garantir que o valor seja float
        return locale.currency(valor, grouping=True, symbol=True)
    except ValueError:
        return "Valor inválido"


# Função para converter valor de string ou decimal para float (corrigido)
def converter_valor_para_float(valor_str):
    try:
        # Verificar se o valor já é um número do tipo Decimal ou float
        if isinstance(valor_str, (float, int, decimal.Decimal)):
            return float(valor_str)
        # Se for uma string, aplicar a conversão de formato
        valor_str = valor_str.replace('.', '').replace(',', '.')
        return float(valor_str)
    except (ValueError, AttributeError):
        return None


# Função para formatar a data para o formato dd/mm/yyyy
def formatar_data(data):
    if isinstance(data, datetime):
        return data.strftime('%d/%m/%Y')
    elif isinstance(data, str):
        try:
            # Caso a data venha no formato yyyy-mm-dd como string
            data_formatada = datetime.strptime(data, '%Y-%m-%d')
            return data_formatada.strftime('%d/%m/%Y')
        except ValueError:
            return data  # Retorna a string original se não conseguir converter
    return data  # Se já estiver no formato correto


# Função para exportar o relatório em PDF com cores, logo, formatação de valores e data corrigida
# Função para exportar o relatório em PDF com cores, logo, formatação de valores e data corrigida
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

    # Espaçamento após o título
    pdf.ln(15)

    # Obter a data e hora atuais
    data_emissao = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    pdf.set_font('Arial', 'I', 10)
    pdf.cell(0, 10, f"Data de emissão: {data_emissao}", ln=True, align='L')

    # Espaçamento
    pdf.ln(5)

    # Definir cores e cabeçalho da tabela
    pdf.set_fill_color(200, 220, 255)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', 'B', 12)

    colunas = ["Id", "Data", "Empresa", "Atividade", "Tipo", "Valor", "Conta", "Data Vencimento"]
    col_widths = [20, 30, 60, 60, 10, 25, 40, 25]  # Ajuste as larguras das colunas conforme necessário

    for col, width in zip(colunas, col_widths):
        pdf.cell(width, 10, col, border=1, align='C', fill=True)
    pdf.ln()

    # Definir cor para o conteúdo
    pdf.set_fill_color(230, 240, 255)  # Cor de fundo alternada para linhas
    pdf.set_text_color(0, 0, 0)  # Cor do texto
    pdf.set_font('Arial', '', 10)

    total_credito = 0.0
    total_debito = 0.0
    fill = False  # Variável para alternar cores de fundo

    for row in lancamentos:
        # Garantir que todas as entradas estejam formatadas corretamente e não sejam None
        data_formatada = str(formatar_data(row.get('Data', '')) or '')
        data_vencimento_formatada = str(formatar_data(row.get('Data_Vencimento', '')) or '')
        tipo_formatado = "C" if row.get('Tipo', '').lower() == 'crédito' else "D"

        pdf.cell(col_widths[0], 10, str(row.get('Id', '')), border=1, align='C', fill=fill)
        pdf.cell(col_widths[1], 10, data_formatada, border=1, align='C', fill=fill)
        pdf.cell(col_widths[2], 10, str(row.get('Empresa', '')), border=1, align='C', fill=fill)
        pdf.cell(col_widths[3], 10, str(row.get('Atividade', '')), border=1, align='C', fill=fill)
        pdf.cell(col_widths[4], 10, tipo_formatado, border=1, align='C', fill=fill)
        pdf.cell(col_widths[5], 10, formatar_moeda(row.get('Valor', 0)).replace('R$', 'R$ '), border=1, align='C', fill=fill)
        pdf.cell(col_widths[6], 10, str(row.get('Conta', '')), border=1, align='C', fill=fill)
        pdf.cell(col_widths[7], 10, data_vencimento_formatada, border=1, align='C', fill=fill)
        pdf.ln()

        # Totalização de créditos e débitos
        valor = converter_valor_para_float(row.get('Valor', 0))
        if row.get('Tipo', '').lower() == 'crédito':
            total_credito += valor
        else:
            total_debito += valor

        fill = not fill  # Alterna a cor de fundo para as próximas linhas

    # Cálculo do saldo
    saldo = total_credito - total_debito

    # Mostrar os totais
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Total Crédito: {formatar_moeda(total_credito)}", ln=True, align='L')
    pdf.cell(0, 10, f"Total Débito: {formatar_moeda(total_debito)}", ln=True, align='L')
    pdf.cell(0, 10, f"Saldo: {formatar_moeda(saldo)}", ln=True, align='L')

    try:
        pdf.output(nome_arquivo)
        messagebox.showinfo("Sucesso", f"Relatório salvo como {nome_arquivo}")
    except Exception as e:
        logging.error(f"Erro ao gerar PDF: {e}")
        messagebox.showerror("Erro", "Erro ao salvar o relatório em PDF.")

# Função para buscar lançamentos por status (A Pagar, A Receber, etc.)
def buscar_lancamentos_por_status(status):
    conexao = conectar_banco()
    if conexao is None:
        return []

    query = """
        SELECT Id, Data, Empresa, Atividade, Observacao, Tipo, Valor, Conta, Status, Data_Vencimento 
        FROM Lancamentos 
        WHERE Status = ?
        ORDER BY Data
    """

    try:
        cursor = conexao.cursor()
        cursor.execute(query, (status,))
        lancamentos = cursor.fetchall()
        if not lancamentos:
            logging.info(f"Nenhum lançamento encontrado com status {status}.")
        return processar_lancamentos(lancamentos)
    except pyodbc.Error as e:
        logging.error(f"Erro ao buscar lançamentos por status: {e}")
        return []
    finally:
        cursor.close()
        conexao.close()


# Função para buscar lançamentos por status e conta contábil
def buscar_lancamentos_por_status_e_conta(status, conta):
    conexao = conectar_banco()
    if conexao is None:
        return []

    query = """
    SELECT Id, Data, Empresa, Atividade, Observacao, Tipo, Valor, Conta, Status, Data_Vencimento 
    FROM Lancamentos 
    WHERE Status = ? AND Conta = ?
    ORDER BY Data
    """

    try:
        cursor = conexao.cursor()
        cursor.execute(query, (status, conta))
        return processar_lancamentos(cursor.fetchall())
    except pyodbc.Error as e:
        logging.error(f"Erro ao buscar lançamentos por status e conta: {e}")
        return []
    finally:
        cursor.close()
        conexao.close()


# Função para processar os lançamentos e retorná-los em um formato legível
def processar_lancamentos(lancamentos):
    lista_lancamentos = []
    for row in lancamentos:
        # Certifique-se de que os índices dos campos estão corretos
        data_formatada = formatar_data(row[1])  # Data
        data_vencimento_formatada = formatar_data(row[9])  # Data de Vencimento

        # Processar e preparar o lançamento em formato de dicionário
        lista_lancamentos.append({
            "Id": row[0],
            "Data": data_formatada,
            "Empresa": row[2],
            "Atividade": row[3],
            "Observacao": row[4],
            "Tipo": "crédito" if row[5] == "C" else "débito",
            "Valor": row[6],
            "Conta": row[7],
            "Status": row[8],
            "Data_Vencimento": data_vencimento_formatada
        })
    return lista_lancamentos

# Função para gerar relatório geral via interface gráfica
def gerar_relatorio_geral():
    lancamentos = buscar_lancamentos_do_banco()
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
    exportar_para_pdf(lancamentos, nome_arquivo, "Relatório Geral de Lançamentos")

# Função para gerar Relatório Geral - A Pagar
def gerar_relatorio_geral_a_pagar():
    lancamentos = buscar_lancamentos_por_status("A Pagar")
    if not lancamentos:
        messagebox.showinfo("Relatório Geral - A Pagar", "Nenhum lançamento com status 'A Pagar'.")
        return

    nome_arquivo = askstring("Salvar Relatório", "Digite o nome do arquivo (sem extensão):")
    if not nome_arquivo:
        messagebox.showwarning("Erro", "Nome do arquivo não fornecido. Relatório não será salvo.")
        return
    nome_arquivo += ".pdf" if not nome_arquivo.endswith(".pdf") else ""

    exportar_para_pdf(lancamentos, nome_arquivo, "Relatório Geral - A Pagar")


# Função para gerar Relatório por Conta Contábil - A Pagar
def gerar_relatorio_conta_a_pagar():
    contas_contabeis = ["Exposição", "Rodeio/Show", "Venda de Espaço", "Patrocinio", "Ranch Sorting", "Team Penning"]

    def filtrar_relatorio():
        conta_escolhida = combo_conta.get().lower()
        if conta_escolhida not in [c.lower() for c in contas_contabeis]:
            messagebox.showwarning("Erro", "Conta contábil inválida!")
            return

        lancamentos = buscar_lancamentos_por_status_e_conta("A Pagar", conta_escolhida)
        if not lancamentos:
            messagebox.showinfo("Relatório por Conta - A Pagar", f"Nenhum lançamento com status 'A Pagar' para a conta {conta_escolhida}.")
            return

        nome_arquivo = f"relatorio_{conta_escolhida.replace('/', '-')}_a_pagar.pdf"
        exportar_para_pdf(lancamentos, nome_arquivo, f"Relatório por Conta - A Pagar ({conta_escolhida})")

    # Interface gráfica para selecionar a conta contábil
    relatorio_janela = tk.Toplevel(root)
    relatorio_janela.title("Relatório por Conta - A Pagar")
    relatorio_janela.geometry("400x200")
    tk.Label(relatorio_janela, text="Escolha a conta contábil:").pack(pady=10)

    combo_conta = ttk.Combobox(relatorio_janela, values=contas_contabeis)
    combo_conta.pack()
    btn_filtrar = tk.Button(relatorio_janela, text="Gerar Relatório", command=filtrar_relatorio)
    btn_filtrar.pack(pady=20)


# Função para gerar Relatório Geral - A Receber
def gerar_relatorio_geral_a_receber():
    lancamentos = buscar_lancamentos_por_status("A Receber")
    if not lancamentos:
        messagebox.showinfo("Relatório Geral - A Receber", "Nenhum lançamento com status 'A Receber'.")
        return

    nome_arquivo = askstring("Salvar Relatório", "Digite o nome do arquivo (sem extensão):")
    if not nome_arquivo:
        messagebox.showwarning("Erro", "Nome do arquivo não fornecido. Relatório não será salvo.")
        return
    nome_arquivo += ".pdf" if not nome_arquivo.endswith(".pdf") else ""

    exportar_para_pdf(lancamentos, nome_arquivo, "Relatório Geral - A Receber")


# Função para gerar Relatório por Conta Contábil - A Receber
def gerar_relatorio_conta_a_receber():
    contas_contabeis = ["Exposição", "Rodeio/Show", "Venda de Espaço", "Patrocinio", "Ranch Sorting", "Team Penning"]

    def filtrar_relatorio():
        conta_escolhida = combo_conta.get().lower()
        if conta_escolhida not in [c.lower() for c in contas_contabeis]:
            messagebox.showwarning("Erro", "Conta contábil inválida!")
            return

        lancamentos = buscar_lancamentos_por_status_e_conta("A Receber", conta_escolhida)
        if not lancamentos:
            messagebox.showinfo("Relatório por Conta - A Receber", f"Nenhum lançamento com status 'A Receber' para a conta {conta_escolhida}.")
            return

        nome_arquivo = f"relatorio_{conta_escolhida.replace('/', '-')}_a_receber.pdf"
        exportar_para_pdf(lancamentos, nome_arquivo, f"Relatório por Conta - A Receber ({conta_escolhida})")

    # Interface gráfica para selecionar a conta contábil
    relatorio_janela = tk.Toplevel(root)
    relatorio_janela.title("Relatório por Conta - A Receber")
    relatorio_janela.geometry("400x200")
    tk.Label(relatorio_janela, text="Escolha a conta contábil:").pack(pady=10)

    combo_conta = ttk.Combobox(relatorio_janela, values=contas_contabeis)
    combo_conta.pack()
    btn_filtrar = tk.Button(relatorio_janela, text="Gerar Relatório", command=filtrar_relatorio)
    btn_filtrar.pack(pady=20)

# Função para gerar relatório por conta contábil
def gerar_relatorio_por_conta():
    contas_contabeis = ["Exposição", "Rodeio/Show", "Venda de Espaço", "Patrocinio", "Ranch Sorting", "Team Penning"]

    def filtrar_relatorio():
        conta_escolhida = combo_conta.get().lower()  # Pegando a seleção do combobox e padronizando para minúsculas

        # Mapear "rodeio" ou "shows" para "rodeio/show"
        if conta_escolhida in ["rodeio", "shows"]:
            conta_escolhida = "rodeio/show"

        # Verificar se a conta é válida (inclui "rodeio/show")
        contas_validas = [c.lower() for c in contas_contabeis] + ["rodeio/show"]

        if conta_escolhida not in contas_validas:
            messagebox.showwarning("Erro", "Conta contábil inválida!")
            return

        # Buscar lançamentos no banco
        lancamentos = buscar_lancamentos_do_banco()
        lancamentos_filtrados = [l for l in lancamentos if l['Conta'].lower() == conta_escolhida]

        if not lancamentos_filtrados:
            messagebox.showinfo("Relatório por Conta", f"Nenhum lançamento encontrado para a conta {conta_escolhida}.")
            return

        # Exportar para PDF
        exportar_para_pdf(lancamentos_filtrados, f"relatorio_{conta_escolhida.replace('/', '-')}.pdf", f"Relatório para a Conta {conta_escolhida}")

    # Criar a janela para filtrar o relatório por conta contábil
    relatorio_janela = tk.Toplevel(root)
    relatorio_janela.title("Relatório por Conta Contábil")
    relatorio_janela.geometry("400x200")

    tk.Label(relatorio_janela, text="Escolha a conta contábil:").pack(pady=10)

    # Usar ComboBox em vez de campo de entrada de texto
    combo_conta = ttk.Combobox(relatorio_janela, values=contas_contabeis)
    combo_conta.pack()

    btn_filtrar = tk.Button(relatorio_janela, text="Gerar Relatório", command=filtrar_relatorio)
    btn_filtrar.pack(pady=20)


# Função para buscar lançamentos do banco de dados
def buscar_lancamentos_do_banco():
    conexao = conectar_banco()
    if conexao is None:
        return []

    cursor = conexao.cursor()
    query = "SELECT Id, Data, Empresa, Atividade, Observacao, Tipo, Valor, Conta, Status, Data_Vencimento FROM Lancamentos ORDER BY Data"

    try:
        cursor.execute(query)
        lancamentos = cursor.fetchall()
        lista_lancamentos = []

        for row in lancamentos:
            data_formatada = formatar_data(row[1])  # Se precisar formatar a data, ajuste aqui
            data_vencimento_formatada = formatar_data(row[9])  # Data de Vencimento também

            lista_lancamentos.append({
                "Id": row[0],
                "Data": data_formatada,
                "Empresa": row[2],
                "Atividade": row[3],
                "Observacao": row[4],
                "Tipo": "crédito" if row[5] == "C" else "débito",
                "Valor": row[6],
                "Conta": row[7],
                "Status": row[8],
                "Data_Vencimento": data_vencimento_formatada
            })

        return lista_lancamentos

    except pyodbc.Error as e:
        logging.error(f"Erro ao buscar lançamentos: {e}")
        messagebox.showerror("Erro", f"Erro ao buscar lançamentos: {e}")
        return []
    finally:
        cursor.close()
        conexao.close()

# Função para salvar o lançamento no banco de dados
def salvar_lancamento_no_banco(lancamento):
    conexao = conectar_banco()
    if conexao is None:
        return

    cursor = conexao.cursor()

    query = '''
    INSERT INTO Lancamentos (Data, Empresa, Atividade, Observacao, Tipo, Valor, Conta, Status, Data_Vencimento)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''

    try:
        cursor.execute(query, (
            lancamento['Data'],
            lancamento['Empresa'],
            lancamento['Atividade'],
            lancamento['Observacao'],
            lancamento['Tipo'],
            lancamento['Valor'],
            lancamento['Conta'],
            lancamento['Status'],
            lancamento['Data_Vencimento']
        ))
        conexao.commit()
        messagebox.showinfo("Sucesso", "Lançamento salvo no banco de dados com sucesso!")
    except pyodbc.Error as e:
        logging.error(f"Erro ao salvar o lançamento: {e}")
        messagebox.showerror("Erro", f"Erro ao salvar o lançamento: {e}")
    finally:
        cursor.close()
        conexao.close()

# Função para atualizar o lançamento no banco de dados
def atualizar_lancamento_no_banco(lancamento_id, lancamento_atualizado):
    conexao = conectar_banco()
    if conexao is None:
        return

    cursor = conexao.cursor()

    query = '''
    UPDATE Lancamentos SET Data = ?, Empresa = ?, Atividade = ?, Observacao = ?, Tipo = ?, Valor = ?, Conta = ?, Status = ?, Data_Vencimento = ?
    WHERE Id = ?
    '''

    try:
        # Log para debug: registrando os valores que serão atualizados no banco de dados
        logging.info(f"Atualizando lançamento ID {lancamento_id} com valores: {lancamento_atualizado}")

        # Executar a query com os valores atualizados
        cursor.execute(query, (
            lancamento_atualizado['Data'],
            lancamento_atualizado['Empresa'],
            lancamento_atualizado['Atividade'],
            lancamento_atualizado['Observacao'],
            lancamento_atualizado['Tipo'],
            lancamento_atualizado['Valor'],
            lancamento_atualizado['Conta'],
            lancamento_atualizado['Status'],
            lancamento_atualizado['Data_Vencimento'],
            lancamento_id
        ))

        # Commitar as alterações
        conexao.commit()

        # Exibir mensagem de sucesso
        messagebox.showinfo("Sucesso", "Lançamento atualizado com sucesso!")

    except Exception as e:
        # Captura e log de erro detalhado
        logging.error(f"Erro ao atualizar o lançamento com ID {lancamento_id}: {e}")
        messagebox.showerror("Erro", f"Erro ao atualizar o lançamento: {e}")

    finally:
        cursor.close()
        conexao.close()

# Função para excluir o lançamento no banco de dados
def excluir_lancamento_no_banco(lancamento_id):
    conexao = conectar_banco()
    if conexao is None:
        return

    cursor = conexao.cursor()

    query = "DELETE FROM Lancamentos WHERE Id = ?"

    try:
        cursor.execute(query, (lancamento_id,))
        conexao.commit()
        messagebox.showinfo("Sucesso", "Lançamento excluído com sucesso!")
    except Exception as e:
        logging.error(f"Erro ao excluir o lançamento: {e}")
        messagebox.showerror("Erro", f"Erro ao excluir o lançamento: {e}")
    finally:
        cursor.close()
        conexao.close()

# Função para adicionar lançamento via interface gráfica
def adicionar_lancamento_tela():
    def salvar():
        data = entry_data.get()
        empresa = entry_empresa.get()
        atividade = entry_atividade.get()
        observacao = entry_observacao.get()
        tipo = entry_tipo.get().upper()
        valor = entry_valor.get()
        conta = combo_conta.get()  # Pegar o valor selecionado no ComboBox
        status = combo_status.get()  # Novo campo Status com Combobox
        data_vencimento = entry_data_vencimento.get()  # Novo campo Data_Vencimento

        # Validar e converter a data de vencimento
        try:
            data_vencimento_formatada = datetime.strptime(data_vencimento, '%d/%m/%Y').strftime('%Y-%m-%d')
        except ValueError:
            messagebox.showwarning("Erro", "Data de Vencimento inválida! Use o formato dd/mm/yyyy.")
            return

        lancamento = {
            'Data': datetime.strptime(data, '%d/%m/%Y').strftime('%Y-%m-%d'),
            'Empresa': empresa,
            'Atividade': atividade,
            'Observacao': observacao,
            'Tipo': tipo,
            'Valor': float(valor.replace(',', '.')),
            'Conta': conta,
            'Status': status,  # Novo campo Status
            'Data_Vencimento': data_vencimento_formatada  # Novo campo Data_Vencimento
        }

        salvar_lancamento_no_banco(lancamento)
        adicionar_janela.destroy()

    adicionar_janela = tk.Toplevel(root)
    adicionar_janela.title("Adicionar Lançamento")
    adicionar_janela.geometry("550x550")

    # Campos de entrada
    tk.Label(adicionar_janela, text="Data (dd/mm/yyyy):").pack()
    entry_data = tk.Entry(adicionar_janela)
    entry_data.pack()

    tk.Label(adicionar_janela, text="Empresa:").pack()
    entry_empresa = tk.Entry(adicionar_janela)
    entry_empresa.pack()

    tk.Label(adicionar_janela, text="Atividade:").pack()
    entry_atividade = tk.Entry(adicionar_janela)
    entry_atividade.pack()
    
    tk.Label(adicionar_janela, text="Observacao:").pack()
    entry_observacao = tk.Entry(adicionar_janela)
    entry_observacao.pack()

    tk.Label(adicionar_janela, text="Tipo (C/D):").pack()
    entry_tipo = tk.Entry(adicionar_janela)
    entry_tipo.pack()

    tk.Label(adicionar_janela, text="Valor:").pack()
    entry_valor = tk.Entry(adicionar_janela)
    entry_valor.pack()

    tk.Label(adicionar_janela, text="Conta Contábil:").pack()
    contas_contabeis = ["Exposição", "Rodeio/Show", "Venda de Espaço", "Patrocinio", "Ranch Sorting", "Team Penning"]
    combo_conta = ttk.Combobox(adicionar_janela, values=contas_contabeis)
    combo_conta.pack()

    # ComboBox para Status
    tk.Label(adicionar_janela, text="Status:").pack()
    opcoes_status = ["A receber", "A Pagar", "Pago"]  # Adicione aqui as opções de status desejadas
    combo_status = ttk.Combobox(adicionar_janela, values=opcoes_status)
    combo_status.pack()

    # Campo de Data de Vencimento
    tk.Label(adicionar_janela, text="Data de Vencimento (dd/mm/yyyy):").pack()
    entry_data_vencimento = tk.Entry(adicionar_janela)
    entry_data_vencimento.pack()

    # Botão para salvar o lançamento
    btn_salvar = tk.Button(adicionar_janela, text="Salvar", command=salvar)
    btn_salvar.pack(pady=10)

# Função para modificar lançamento via interface gráfica
def alterar_lancamento_tela():
    def buscar_lancamento():
        lancamento_id = entry_id.get()

        if not lancamento_id.isdigit():
            messagebox.showwarning("Erro", "Por favor, insira um ID válido.")
            return

        # Função que busca o lançamento no banco de dados
        lancamento = buscar_lancamento_por_id(lancamento_id)

        if lancamento:
            # Preencher os campos com os dados do lançamento existente
            entry_data.delete(0, tk.END)
            entry_data.insert(0, str(lancamento.get('Data', '')))

            entry_empresa.delete(0, tk.END)
            entry_empresa.insert(0, str(lancamento.get('Empresa', '')))

            entry_atividade.delete(0, tk.END)
            entry_atividade.insert(0, str(lancamento.get('Atividade', '')))

            entry_observacao.delete(0, tk.END)
            entry_observacao.insert(0, str(lancamento.get('Observacao', '')))

            entry_tipo.delete(0, tk.END)
            entry_tipo.insert(0, str(lancamento.get('Tipo', '')))

            entry_valor.delete(0, tk.END)
            entry_valor.insert(0, str(lancamento.get('Valor', 0.0)))

            entry_conta.delete(0, tk.END)
            entry_conta.insert(0, str(lancamento.get('Conta', '')))

            combo_status.set(str(lancamento.get('Status', '')))  # Preencher o ComboBox com o status atual

            entry_data_vencimento.delete(0, tk.END)
            entry_data_vencimento.insert(0, str(lancamento.get('Data_Vencimento', '')))
        else:
            messagebox.showwarning("Erro", "Lançamento não encontrado!")

    def modificar():
        lancamento_id = entry_id.get()
        nova_empresa = entry_empresa.get()
        novo_valor = entry_valor.get()

        # Validação da data
        try:
            # Formatar a data do campo para o formato YYYY-MM-DD
            data_formatada = datetime.strptime(entry_data.get(), '%d/%m/%Y').strftime('%Y-%m-%d')
        except ValueError:
            messagebox.showwarning("Erro", "Data inválida! Use o formato dd/mm/yyyy.")
            return

        # Validação do tipo de transação (C para crédito, D para débito)
        tipo = entry_tipo.get().upper()
        if tipo not in ['C', 'D']:
            messagebox.showwarning("Erro", "Tipo inválido! Use 'C' para crédito ou 'D' para débito.")
            return

        # Pegar o valor do ComboBox de Status
        novo_status = combo_status.get()

        # Validação da data de vencimento
        try:
            # Formatar a data de vencimento para o formato YYYY-MM-DD
            data_vencimento_formatada = datetime.strptime(entry_data_vencimento.get(), '%d/%m/%Y').strftime('%Y-%m-%d')
        except ValueError:
            messagebox.showwarning("Erro", "Data de Vencimento inválida! Use o formato dd/mm/yyyy.")
            return

        # Montar o dicionário com os dados atualizados
        lancamento_atualizado = {
            'Data': data_formatada,
            'Empresa': nova_empresa,
            'Atividade': entry_atividade.get(),
            'Observacao': entry_observacao.get(),
            'Tipo': tipo,
            'Valor': float(novo_valor.replace(',', '.')),
            'Conta': entry_conta.get(),
            'Status': novo_status,  # Adicionar o Status atualizado
            'Data_Vencimento': data_vencimento_formatada  # Adicionar Data de Vencimento atualizada
        }

        print(lancamento_atualizado)

        # Função que realiza a atualização no banco de dados
        atualizar_lancamento_no_banco(lancamento_id, lancamento_atualizado)
        modificar_janela.destroy()

    modificar_janela = tk.Toplevel(root)
    modificar_janela.title("Modificar Lançamento")
    modificar_janela.geometry("550x550")

    # ID do Lançamento
    tk.Label(modificar_janela, text="ID do Lançamento:").pack()
    entry_id = tk.Entry(modificar_janela)
    entry_id.pack()

    btn_buscar = tk.Button(modificar_janela, text="Buscar", command=buscar_lancamento)
    btn_buscar.pack(pady=10)

    # Campos para modificar o lançamento
    tk.Label(modificar_janela, text="Nova Data (dd/mm/yyyy):").pack()
    entry_data = tk.Entry(modificar_janela)
    entry_data.pack()

    tk.Label(modificar_janela, text="Nova Empresa:").pack()
    entry_empresa = tk.Entry(modificar_janela)
    entry_empresa.pack()

    tk.Label(modificar_janela, text="Nova Atividade:").pack()
    entry_atividade = tk.Entry(modificar_janela)
    entry_atividade.pack()

    tk.Label(modificar_janela, text="Nova Observacao:").pack()
    entry_observacao = tk.Entry(modificar_janela)
    entry_observacao.pack()

    tk.Label(modificar_janela, text="Novo Tipo (C/D):").pack()
    entry_tipo = tk.Entry(modificar_janela)
    entry_tipo.pack()

    tk.Label(modificar_janela, text="Novo Valor:").pack()
    entry_valor = tk.Entry(modificar_janela)
    entry_valor.pack()

    tk.Label(modificar_janela, text="Nova Conta Contábil:").pack()
    opcoes_status = ["Exposição", "Rodeio/Show", "Venda de Espaço", "Patrocinio", "Ranch Sorting", "Team Penning"]
    entry_conta = ttk.Combobox(modificar_janela, values=opcoes_status)
    entry_conta.pack()

    # ComboBox para Status
    tk.Label(modificar_janela, text="Status:").pack()
    opcoes_status = ["A receber", "A Pagar", "Pago"]
    combo_status = ttk.Combobox(modificar_janela, values=opcoes_status)
    combo_status.pack()

    # Campo para Data de Vencimento
    tk.Label(modificar_janela, text="Nova Data de Vencimento (dd/mm/yyyy):").pack()
    entry_data_vencimento = tk.Entry(modificar_janela)
    entry_data_vencimento.pack()

    btn_modificar = tk.Button(modificar_janela, text="Modificar", command=modificar)
    btn_modificar.pack(pady=10)

# Função para buscar o lançamento por ID (esta função precisa ser implementada para interagir com o banco de dados)
def buscar_lancamento_por_id(lancamento_id):
    conexao = conectar_banco()  # Certifique-se de que esta função já está implementada para conectar ao banco
    if conexao is None:
        messagebox.showerror("Erro", "Erro ao conectar ao banco de dados.")
        return None

    cursor = conexao.cursor()
    query = "SELECT Id, Data, Empresa, Atividade, Observacao, Tipo, Valor, Conta, Status, Data_Vencimento FROM Lancamentos WHERE Id = ?"

    try:
        cursor.execute(query, (lancamento_id,))
        resultado = cursor.fetchone()

        if resultado:
            # Tratar o valor da data para garantir que está no formato correto
            data_formatada = formatar_data(resultado[1])  # Formatar a data corretamente
            data_vencimento_formatada = formatar_data(resultado[9])  # Usar índice 9 para Data de Vencimento

            lancamento = {
                'Data': data_formatada,
                'Empresa': resultado[2],
                'Atividade': resultado[3],
                'Observacao': resultado[4],
                'Tipo': resultado[5],
                'Valor': resultado[6],
                'Conta': resultado[7],
                'Status': resultado[8],  # Status está correto no índice 8
                'Data_Vencimento': data_vencimento_formatada  # Data de Vencimento está no índice 9
            }
            return lancamento
        else:
            messagebox.showinfo("Aviso", f"Lançamento com ID {lancamento_id} não encontrado.")
            return None

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao buscar o lançamento: {e}")
        return None

    finally:
        cursor.close()
        conexao.close()

# Função para atualizar o lançamento no banco de dados (exemplo)
def atualizar_lancamento_no_banco(lancamento_id, lancamento_atualizado):
    conexao = conectar_banco()  # Função para conectar ao banco de dados
    if conexao is None:
        messagebox.showerror("Erro", "Erro ao conectar ao banco de dados.")
        return

    cursor = conexao.cursor()
    query = '''
    UPDATE Lancamentos
    SET Data = ?, Empresa = ?, Atividade = ?, Observacao = ?, Tipo = ?, Valor = ?, Conta = ?
    WHERE Id = ?
    '''

    try:
        # Executa a atualização no banco de dados
        cursor.execute(query, (
            lancamento_atualizado['Data'],
            lancamento_atualizado['Empresa'],
            lancamento_atualizado['Atividade'],
            lancamento_atualizado['Observacao'],
            lancamento_atualizado['Tipo'],
            lancamento_atualizado['Valor'],
            lancamento_atualizado['Conta'],
            lancamento_id  # Certifique-se de passar o ID corretamente
        ))

        conexao.commit()  # Confirmar as alterações no banco de dados
        messagebox.showinfo("Sucesso", f"Lançamento ID {lancamento_id} atualizado com sucesso!")

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao atualizar o lançamento: {e}")
        conexao.rollback()  # Desfazer a transação em caso de erro

    finally:
        cursor.close()
        conexao.close()

# Função para excluir lançamento via interface gráfica
def excluir_lancamento_tela():
    def excluir():
        lancamento_id = entry_id.get()
        excluir_lancamento_no_banco(lancamento_id)
        excluir_janela.destroy()

    excluir_janela = tk.Toplevel(root)
    excluir_janela.title("Excluir Lançamento")
    excluir_janela.geometry("400x200")

    tk.Label(excluir_janela, text="ID do Lançamento:").pack()
    entry_id = tk.Entry(excluir_janela)
    entry_id.pack()

    btn_excluir = tk.Button(excluir_janela, text="Excluir", command=excluir)
    btn_excluir.pack(pady=10)


def gerar_grafico_barras():
    conexao = conectar_banco()
    if conexao is None:
        messagebox.showerror("Erro", "Erro ao conectar ao banco de dados.")
        return

    # Consulta adaptada para SQL Server para obter somas de crédito e débito por conta
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

        # Preparar dados para o gráfico
        contas = []
        totais_credito = []
        totais_debito = []

        for row in resultados:
            contas.append(row[0])
            totais_credito.append(row[1])
            totais_debito.append(row[2])

        # Plotar gráfico de barras
        fig, ax = plt.subplots(figsize=(10, 6))
        largura_barra = 0.35
        indices = range(len(contas))

        # Criação das barras de crédito e débito
        barras_credito = ax.bar([i - largura_barra / 2 for i in indices], totais_credito, largura_barra, label='Crédito')
        barras_debito = ax.bar([i + largura_barra / 2 for i in indices], totais_debito, largura_barra, label='Débito')

        # Adicionar rótulos de valores nas barras
        for i, barra in enumerate(barras_credito):
            ax.text(barra.get_x() + barra.get_width() / 2, barra.get_height(), f'R${totais_credito[i]:,.2f}', 
                    ha='center', va='bottom', fontsize=9)

        for i, barra in enumerate(barras_debito):
            ax.text(barra.get_x() + barra.get_width() / 2, barra.get_height(), f'R${totais_debito[i]:,.2f}', 
                    ha='center', va='bottom', fontsize=9)

        # Configurações do gráfico
        ax.set_xlabel('Contas')
        ax.set_ylabel('Valor Total (R$)')
        ax.set_title('Comparação de Créditos e Débitos por Conta')
        ax.set_xticks(indices)
        ax.set_xticklabels(contas, rotation=45)
        ax.legend()

        plt.tight_layout()
        plt.show()

    except pyodbc.Error as e:
        logging.error(f"Erro ao gerar gráfico de barras: {e}")
        messagebox.showerror("Erro", f"Erro ao gerar gráfico de barras: {e}")
    finally:
        cursor.close()
        conexao.close()

# Função para criar a janela principal com os botões
def criar_menu():
    global root
    root = tk.Tk()
    root.title("Sistema de Controle Contábil")
    root.geometry("600x600")

    # Botão para adicionar lançamento
    btn_adicionar = tk.Button(root, text="Adicionar Lançamento", command=adicionar_lancamento_tela, width=30)
    btn_adicionar.pack(pady=20)

    # Botão para modificar lançamento
    btn_alterar = tk.Button(root, text="Modificar Lançamento", command=alterar_lancamento_tela, width=30)
    btn_alterar.pack(pady=10)

    # Botão para excluir lançamento
    btn_excluir = tk.Button(root, text="Excluir Lançamento", command=excluir_lancamento_tela, width=30)
    btn_excluir.pack(pady=10)

    # Botões para os relatórios gerais
    btn_relatorio_geral = tk.Button(root, text="Gerar Relatório Geral (Pago)", command=gerar_relatorio_geral, width=30)
    btn_relatorio_geral.pack(pady=10)

    btn_relatorio_geral_a_pagar = tk.Button(root, text="Gerar Relatório Geral (A Pagar)", command=gerar_relatorio_geral_a_pagar, width=30)
    btn_relatorio_geral_a_pagar.pack(pady=10)

    btn_relatorio_geral_a_receber = tk.Button(root, text="Gerar Relatório Geral (A Receber)", command=gerar_relatorio_geral_a_receber, width=30)
    btn_relatorio_geral_a_receber.pack(pady=10)

    # Botões para os relatórios por conta contábil
    btn_relatorio_conta = tk.Button(root, text="Relatório por Conta (Pago)", command=gerar_relatorio_por_conta, width=30)
    btn_relatorio_conta.pack(pady=10)

    btn_relatorio_conta_a_pagar = tk.Button(root, text="Relatório por Conta (A Pagar)", command=gerar_relatorio_conta_a_pagar, width=30)
    btn_relatorio_conta_a_pagar.pack(pady=10)

    btn_relatorio_conta_a_receber = tk.Button(root, text="Relatório por Conta (A Receber)", command=gerar_relatorio_conta_a_receber, width=30)
    btn_relatorio_conta_a_receber.pack(pady=10)

    # Dentro da função `criar_menu()`, após os outros botões de relatório
    btn_grafico_barras = tk.Button(root, text="Visualizar Gráfico de Créditos vs Débitos", command=gerar_grafico_barras, width=30)
    btn_grafico_barras.pack(pady=10)

    # Botão para sair do sistema
    btn_sair = tk.Button(root, text="Sair", command=root.quit, width=30)
    btn_sair.pack(pady=20)

    root.mainloop()

# Iniciar o menu principal
    criar_menu()  # Inicia a interface gráfica