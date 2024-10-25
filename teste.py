
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

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# Configurando o logging para registrar erros
logging.basicConfig(filename='erros_sistema_contabil.log', level=logging.ERROR,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Função para conectar ao banco de dados SQL Server
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
def exportar_para_pdf(lancamentos, nome_arquivo, titulo_relatorio):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Adicionar o logotipo
    caminho_logo = r'C:\Users\user\PycharmProjects\pythonProject\logo.jpg'  # Substitua pelo caminho correto
    pdf.image(caminho_logo, x=10, y=8, w=30)  # Posição (x=10, y=8) e largura de 30mm

    # Título do relatório
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, titulo_relatorio.upper(), ln=True, align='C')

    # Espaçamento após o título
    pdf.ln(15)

    # Obter a data e hora atuais (posicionar abaixo da logo)
    data_emissao = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    pdf.set_font('Arial', 'I', 10)
    pdf.cell(0, 10, f"Data de emissão: {data_emissao}", ln=True, align='L')

    # Espaçamento
    pdf.ln(5)

    # Definir cores e cabeçalho da tabela
    pdf.set_fill_color(200, 220, 255)  # Cor de fundo para o cabeçalho
    pdf.set_text_color(0, 0, 0)  # Cor preta para o texto
    pdf.set_font('Arial', 'B', 12)

    colunas = ["Id", "Data", "Origem", "Empresa", "Tipo", "Valor", "Conta"]
    col_widths = [20, 30, 70, 70, 20, 25, 40]

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
        # Formatando a data para o formato dd/mm/yyyy
        data_formatada = formatar_data(row['Data'])

        pdf.cell(col_widths[0], 10, str(row['Id']), border=1, align='C', fill=fill)
        pdf.cell(col_widths[1], 10, data_formatada, border=1, align='C', fill=fill)
        pdf.cell(col_widths[2], 10, row['Origem'], border=1, align='C', fill=fill)
        pdf.cell(col_widths[3], 10, row['Empresa'], border=1, align='C', fill=fill)
        pdf.cell(col_widths[4], 10, row['Tipo'], border=1, align='C', fill=fill)
        pdf.cell(col_widths[5], 10, formatar_moeda(float(row['Valor'])).replace('R$', 'R$ '), border=1, align='C',
                 fill=fill)
        pdf.cell(col_widths[6], 10, row['Conta'], border=1, align='C', fill=fill)
        pdf.ln()

        # Totalização de créditos e débitos (correção aplicada)
        valor = converter_valor_para_float(row['Valor'])
        if row['Tipo'].lower() == 'crédito':
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

    # Salvar o PDF com o nome especificado
    pdf.output(nome_arquivo)
    messagebox.showinfo("Sucesso", f"Relatório salvo como {nome_arquivo}")

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


# Função para gerar relatório por conta contábil
def gerar_relatorio_por_conta():
    contas_contabeis = ["Exposição", "Rodeio", "Shows", "Vendas de Terrenos", "Patrocinio", "Provas de Equinos"]

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
# Função para buscar lançamentos do banco de dados
def buscar_lancamentos_do_banco():
    conexao = conectar_banco()
    if conexao is None:
        return []

    cursor = conexao.cursor()
    query = "SELECT Id, Data, Origem, Empresa, Tipo, Valor, Conta FROM Lancamentos"

    try:
        cursor.execute(query)
        lancamentos = cursor.fetchall()
        lista_lancamentos = []

        for row in lancamentos:
            # Se a data já estiver em formato string, não usar strftime
            data = row[1]
            if isinstance(data, datetime):
                data_formatada = data.strftime('%d/%m/%Y')
            else:
                data_formatada = data  # Presumir que a data já está formatada corretamente como string

            lista_lancamentos.append({
                "Id": row[0],
                "Data": data_formatada,
                "Origem": row[2],
                "Empresa": row[3],
                "Tipo": "crédito" if row[4] == "C" else "débito",
                "Valor": row[5],
                "Conta": row[6]
            })

        return lista_lancamentos

    except Exception as e:
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
    INSERT INTO Lancamentos (Data, Origem, Empresa, Tipo, Valor, Conta)
    VALUES (?, ?, ?, ?, ?, ?)
    '''

    try:
        cursor.execute(query, (
            lancamento['Data'],
            lancamento['Origem'],
            lancamento['Empresa'],
            lancamento['Tipo'],
            lancamento['Valor'],
            lancamento['Conta']
        ))
        conexao.commit()
        messagebox.showinfo("Sucesso", "Lançamento salvo no banco de dados com sucesso!")
    except Exception as e:
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
    UPDATE Lancamentos SET Data = ?, Origem = ?, Empresa = ?, Tipo = ?, Valor = ?, Conta = ?
    WHERE Id = ?
    '''

    try:
        cursor.execute(query, (
            lancamento_atualizado['Data'],
            lancamento_atualizado['Origem'],
            lancamento_atualizado['Empresa'],
            lancamento_atualizado['Tipo'],
            lancamento_atualizado['Valor'],
            lancamento_atualizado['Conta'],
            lancamento_id
        ))
        conexao.commit()
        messagebox.showinfo("Sucesso", "Lançamento atualizado com sucesso!")
    except Exception as e:
        logging.error(f"Erro ao atualizar o lançamento: {e}")
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
        origem = entry_origem.get()
        empresa = entry_empresa.get()
        tipo = entry_tipo.get().upper()
        valor = entry_valor.get()
        conta = combo_conta.get()  # Pegar o valor selecionado no ComboBox

        # Se a conta selecionada for "Rodeio" ou "Shows", gravar como "rodeio/show"
        if conta in ["Rodeio", "Shows"]:
            conta = "rodeio/show"

        # Validar e converter a data
        try:
            data_formatada = datetime.strptime(data, '%d/%m/%Y').strftime('%Y-%m-%d')
        except ValueError:
            messagebox.showwarning("Erro", "Data inválida! Use o formato dd/mm/yyyy.")
            return

        if tipo not in ['C', 'D']:
            messagebox.showwarning("Erro", "Tipo inválido! Use 'C' para crédito ou 'D' para débito.")
            return

        lancamento = {
            'Data': data_formatada,
            'Origem': origem,
            'Empresa': empresa,
            'Tipo': tipo,
            'Valor': float(valor.replace(',', '.')),
            'Conta': conta
        }

        salvar_lancamento_no_banco(lancamento)
        adicionar_janela.destroy()

    adicionar_janela = tk.Toplevel(root)
    adicionar_janela.title("Adicionar Lançamento")
    adicionar_janela.geometry("400x400")

    # Campos de entrada
    tk.Label(adicionar_janela, text="Data (dd/mm/yyyy):").pack()
    entry_data = tk.Entry(adicionar_janela)
    entry_data.pack()

    tk.Label(adicionar_janela, text="Origem:").pack()
    entry_origem = tk.Entry(adicionar_janela)
    entry_origem.pack()

    tk.Label(adicionar_janela, text="Empresa:").pack()
    entry_empresa = tk.Entry(adicionar_janela)
    entry_empresa.pack()

    tk.Label(adicionar_janela, text="Tipo (C/D):").pack()
    entry_tipo = tk.Entry(adicionar_janela)
    entry_tipo.pack()

    tk.Label(adicionar_janela, text="Valor:").pack()
    entry_valor = tk.Entry(adicionar_janela)
    entry_valor.pack()

    tk.Label(adicionar_janela, text="Conta Contábil:").pack()

    # ComboBox para contas contábeis
    contas_contabeis = ["Exposição", "Rodeio", "Shows", "Vendas de Terrenos", "Patrocinio", "Provas de Equinos"]
    combo_conta = ttk.Combobox(adicionar_janela, values=contas_contabeis)
    combo_conta.pack()

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
            entry_data.insert(0, lancamento['Data'])

            entry_origem.delete(0, tk.END)
            entry_origem.insert(0, lancamento['Origem'])

            entry_empresa.delete(0, tk.END)
            entry_empresa.insert(0, lancamento['Empresa'])

            entry_tipo.delete(0, tk.END)
            entry_tipo.insert(0, lancamento['Tipo'])

            entry_valor.delete(0, tk.END)
            entry_valor.insert(0, str(lancamento['Valor']))

            entry_conta.delete(0, tk.END)
            entry_conta.insert(0, lancamento['Conta'])
        else:
            messagebox.showwarning("Erro", "Lançamento não encontrado!")

    def modificar():
        lancamento_id = entry_id.get()
        nova_origem = entry_origem.get()
        novo_valor = entry_valor.get()

        try:
            data_formatada = datetime.strptime(entry_data.get(), '%d/%m/%Y').strftime('%Y-%m-%d')
        except ValueError:
            messagebox.showwarning("Erro", "Data inválida! Use o formato dd/mm/yyyy.")
            return

        tipo = entry_tipo.get().upper()
        if tipo not in ['C', 'D']:
            messagebox.showwarning("Erro", "Tipo inválido! Use 'C' para crédito ou 'D' para débito.")
            return

        lancamento_atualizado = {
            'Data': data_formatada,
            'Origem': nova_origem,
            'Empresa': entry_empresa.get(),
            'Tipo': tipo,
            'Valor': float(novo_valor.replace(',', '.')),
            'Conta': entry_conta.get()
        }

        atualizar_lancamento_no_banco(lancamento_id, lancamento_atualizado)
        modificar_janela.destroy()

    modificar_janela = tk.Toplevel(root)
    modificar_janela.title("Modificar Lançamento")
    modificar_janela.geometry("400x400")

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

    tk.Label(modificar_janela, text="Nova Origem:").pack()
    entry_origem = tk.Entry(modificar_janela)
    entry_origem.pack()

    tk.Label(modificar_janela, text="Nova Empresa:").pack()
    entry_empresa = tk.Entry(modificar_janela)
    entry_empresa.pack()

    tk.Label(modificar_janela, text="Novo Tipo (C/D):").pack()
    entry_tipo = tk.Entry(modificar_janela)
    entry_tipo.pack()

    tk.Label(modificar_janela, text="Novo Valor:").pack()
    entry_valor = tk.Entry(modificar_janela)
    entry_valor.pack()

    tk.Label(modificar_janela, text="Nova Conta Contábil:").pack()
    entry_conta = tk.Entry(modificar_janela)
    entry_conta.pack()

    btn_modificar = tk.Button(modificar_janela, text="Modificar", command=modificar)
    btn_modificar.pack(pady=10)


# Função para buscar o lançamento por ID (esta função precisa ser implementada para interagir com o banco de dados)
def buscar_lancamento_por_id(lancamento_id):
    conexao = conectar_banco()  # Certifique-se de que esta função já está implementada para conectar ao banco
    if conexao is None:
        messagebox.showerror("Erro", "Erro ao conectar ao banco de dados.")
        return None

    cursor = conexao.cursor()
    query = "SELECT Id, Data, Origem, Empresa, Tipo, Valor, Conta FROM Lancamentos WHERE Id = ?"

    try:
        cursor.execute(query, (lancamento_id,))
        resultado = cursor.fetchone()

        if resultado:
            # Tratar o valor da data para garantir que está no formato correto
            if isinstance(resultado[1], datetime):
                data_formatada = resultado[1].strftime('%d/%m/%Y')
            elif isinstance(resultado[1], str):
                # Caso já seja uma string, verificar se está no formato esperado
                try:
                    # Tenta converter a string para o formato dd/mm/yyyy
                    data_formatada = datetime.strptime(resultado[1], '%Y-%m-%d').strftime('%d/%m/%Y')
                except ValueError:
                    # Caso a string esteja em um formato inesperado, apenas usa como está
                    data_formatada = resultado[1]
            else:
                data_formatada = str(resultado[1])

            lancamento = {
                'Data': data_formatada,  # Data formatada corretamente
                'Origem': resultado[2],
                'Empresa': resultado[3],
                'Tipo': resultado[4],
                'Valor': resultado[5],
                'Conta': resultado[6]
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
    SET Data = ?, Origem = ?, Empresa = ?, Tipo = ?, Valor = ?, Conta = ?
    WHERE Id = ?
    '''

    try:
        # Executa a atualização no banco de dados
        cursor.execute(query, (
            lancamento_atualizado['Data'],
            lancamento_atualizado['Origem'],
            lancamento_atualizado['Empresa'],
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

# Função para criar a janela principal com os botões
def criar_menu():
    global root
    root = tk.Tk()
    root.title("Sistema de Controle Contábil")
    root.geometry("400x400")

    btn_adicionar = tk.Button(root, text="Adicionar Lançamento", command=adicionar_lancamento_tela, width=30)
    btn_adicionar.pack(pady=20)

    btn_alterar = tk.Button(root, text="Modificar Lançamento", command=alterar_lancamento_tela, width=30)
    btn_alterar.pack(pady=10)

    btn_excluir = tk.Button(root, text="Excluir Lançamento", command=excluir_lancamento_tela, width=30)
    btn_excluir.pack(pady=10)

    btn_relatorio_geral = tk.Button(root, text="Gerar Relatório Geral", command=gerar_relatorio_geral, width=30)
    btn_relatorio_geral.pack(pady=10)

    btn_relatorio_conta = tk.Button(root, text="Gerar Relatório por Conta Contábil", command=gerar_relatorio_por_conta,
                                    width=30)
    btn_relatorio_conta.pack(pady=10)

    btn_sair = tk.Button(root, text="Sair", command=root.quit, width=30)
    btn_sair.pack(pady=10)

    root.mainloop()

# Iniciar o menu principal
criar_menu()