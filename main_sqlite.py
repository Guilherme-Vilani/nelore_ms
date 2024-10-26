import sqlite3
import logging
from tkinter.simpledialog import askstring
from datetime import datetime
import locale
from tkinter import ttk
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import database.database as database
import utils.export_pdf as utilsPdf
import utils.relatorios as relatorios
import matplotlib.pyplot as plt

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# Configurando o logging para registrar erros
logging.basicConfig(filename='nelore.log', level=logging.ERROR,
                    format='%(asctime)s:%(levelname)s:%(message)s')

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

        database.salvar_lancamento_no_banco(lancamento)
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

def alterar_lancamento_tela(lancamento_id):
    # Busca o lançamento pelo ID
    lancamento = database.buscar_lancamento_por_id(lancamento_id)
    if not lancamento:
        messagebox.showerror("Erro", f"Lançamento com ID {lancamento_id} não encontrado.")
        return
    
    data_original = lancamento.get('Data', '')
    try:
        data_formatada = datetime.strptime(data_original, '%Y-%m-%d').strftime('%d/%m/%Y')
    except ValueError:
        data_formatada = data_original  # Caso a data não esteja no formato esperado

    # Converte a data de vencimento para o formato dd/mm/yyyy
    data_vencimento_original = lancamento.get('Data_Vencimento', '')
    try:
        data_vencimento_formatada = datetime.strptime(data_vencimento_original, '%Y-%m-%d').strftime('%d/%m/%Y')
    except ValueError:
        data_vencimento_formatada = data_vencimento_original 

    # Cria a janela de edição
    modificar_janela = tk.Toplevel(root)
    modificar_janela.title("Modificar Lançamento")
    modificar_janela.geometry("550x550")

    # Campos para exibir e modificar o lançamento
    tk.Label(modificar_janela, text="ID do Lançamento:").pack()
    entry_id = tk.Entry(modificar_janela, width=30)
    entry_id.insert(0, str(lancamento_id))
    entry_id.config(state="disabled")  # ID não deve ser editado
    entry_id.pack()

    tk.Label(modificar_janela, text="Nova Data (dd/mm/yyyy):").pack()
    entry_data = tk.Entry(modificar_janela, width=30)
    entry_data.insert(0, data_formatada)
    entry_data.pack()

    tk.Label(modificar_janela, text="Nova Empresa:").pack()
    entry_empresa = tk.Entry(modificar_janela, width=30)
    entry_empresa.insert(0, str(lancamento.get('Empresa', '')))
    entry_empresa.pack()

    tk.Label(modificar_janela, text="Nova Atividade:").pack()
    entry_atividade = tk.Entry(modificar_janela, width=30)
    entry_atividade.insert(0, str(lancamento.get('Atividade', '')))
    entry_atividade.pack()

    tk.Label(modificar_janela, text="Nova Observacao:").pack()
    entry_observacao = tk.Entry(modificar_janela, width=30)
    entry_observacao.insert(0, str(lancamento.get('Observacao', '')))
    entry_observacao.pack()

    tk.Label(modificar_janela, text="Novo Tipo (C/D):").pack()
    entry_tipo = tk.Entry(modificar_janela, width=30)
    entry_tipo.insert(0, str(lancamento.get('Tipo', '')))
    entry_tipo.pack()

    tk.Label(modificar_janela, text="Novo Valor:").pack()
    entry_valor = tk.Entry(modificar_janela, width=30)
    entry_valor.insert(0, str(lancamento.get('Valor', 0.0)))
    entry_valor.pack()

    # ComboBox para Conta Contábil
    tk.Label(modificar_janela, text="Nova Conta Contábil:").pack()
    contas_contabeis = ["Exposição", "Rodeio/Show", "Venda de Espaço", "Patrocinio", "Ranch Sorting", "Team Penning"]
    entry_conta = ttk.Combobox(modificar_janela, values=contas_contabeis, width=30)
    entry_conta.set(str(lancamento.get('Conta', '')))
    entry_conta.pack()

    # ComboBox para Status
    tk.Label(modificar_janela, text="Status:").pack()
    opcoes_status = ["A receber", "A pagar", "Pago"]
    combo_status = ttk.Combobox(modificar_janela, values=opcoes_status, width=30)
    combo_status.set(str(lancamento.get('Status', '')))
    combo_status.pack()

    # Campo para Data de Vencimento
    tk.Label(modificar_janela, text="Nova Data de Vencimento (dd/mm/yyyy):").pack()
    entry_data_vencimento = tk.Entry(modificar_janela, width=30)
    entry_data_vencimento.insert(0, data_vencimento_formatada)
    entry_data_vencimento.pack()

    # Função para salvar as modificações
    def salvar_alteracoes():
        nova_empresa = entry_empresa.get()
        novo_valor = entry_valor.get()
        # Validação da data
        try:
            data_formatada = datetime.strptime(entry_data.get(), '%d/%m/%Y').strftime('%Y-%m-%d')
        except ValueError:
            messagebox.showwarning("Erro", "Data inválida! Use o formato dd/mm/yyyy.")
            return

        tipo = entry_tipo.get().upper()
        if tipo not in ['C', 'D']:
            messagebox.showwarning("Erro", "Tipo inválido! Use 'C' para crédito ou 'D' para débito.")
            return

        novo_status = combo_status.get()

        try:
            data_vencimento_formatada = datetime.strptime(entry_data_vencimento.get(), '%d/%m/%Y').strftime('%Y-%m-%d')
        except ValueError:
            messagebox.showwarning("Erro", "Data de Vencimento inválida! Use o formato dd/mm/yyyy.")
            return

        lancamento_atualizado = {
            'Data': data_formatada,
            'Empresa': nova_empresa,
            'Atividade': entry_atividade.get(),
            'Observacao': entry_observacao.get(),
            'Tipo': tipo,
            'Valor': float(novo_valor.replace(',', '.')),
            'Conta': entry_conta.get(),
            'Status': novo_status,
            'Data_Vencimento': data_vencimento_formatada
        }

        database.atualizar_lancamento_no_banco(lancamento_id, lancamento_atualizado)
        messagebox.showinfo("Sucesso", "Lançamento atualizado com sucesso!")
        modificar_janela.destroy()

    btn_modificar = tk.Button(modificar_janela, text="Salvar Modificações", command=salvar_alteracoes)
    btn_modificar.pack(pady=10)

def editar_lancamento():
    global tree
    selected_item = tree.selection()
    if selected_item:
        item = tree.item(selected_item)
        lancamento_id = item["values"][0]
        alterar_lancamento_tela(lancamento_id)  # Passa o lancamento_id para a função
    else:
        messagebox.showwarning("Aviso", "Por favor, selecione um lançamento para editar.")

def excluir_lancamento_tela():
    def excluir():
        lancamento_id = entry_id.get()
        database.excluir_lancamento_no_banco(lancamento_id)
        excluir_janela.destroy()

    excluir_janela = tk.Toplevel(root)
    excluir_janela.title("Excluir Lançamento")
    excluir_janela.geometry("400x200")

    tk.Label(excluir_janela, text="ID do Lançamento:").pack()
    entry_id = tk.Entry(excluir_janela)
    entry_id.pack()

    btn_excluir = tk.Button(excluir_janela, text="Excluir", command=excluir)
    btn_excluir.pack(pady=10)

# Função para gerar Relatório por Conta Contábil - A Pagar
def gerar_relatorio_conta_a_pagar():
    contas_contabeis = ["Exposição", "Rodeio/Show", "Venda de Espaço", "Patrocinio", "Ranch Sorting", "Team Penning"]

    def filtrar_relatorio():
        conta_escolhida = combo_conta.get().lower()
        if conta_escolhida not in [c.lower() for c in contas_contabeis]:
            messagebox.showwarning("Erro", "Conta contábil inválida!")
            return

        lancamentos = database.buscar_lancamentos_por_status_e_conta("A Pagar", conta_escolhida)
        if not lancamentos:
            messagebox.showinfo("Relatório por Conta - A Pagar", f"Nenhum lançamento com status 'A Pagar' para a conta {conta_escolhida}.")
            return

        nome_arquivo = f"relatorio_{conta_escolhida.replace('/', '-')}_a_pagar.pdf"
        utilsPdf.exportar_para_pdf(lancamentos, nome_arquivo, f"Relatório por Conta - A Pagar ({conta_escolhida})")

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
    lancamentos = database.buscar_lancamentos_por_status("A Receber")
    if not lancamentos:
        messagebox.showinfo("Relatório Geral - A Receber", "Nenhum lançamento com status 'A Receber'.")
        return

    nome_arquivo = askstring("Salvar Relatório", "Digite o nome do arquivo (sem extensão):")
    if not nome_arquivo:
        messagebox.showwarning("Erro", "Nome do arquivo não fornecido. Relatório não será salvo.")
        return
    nome_arquivo += ".pdf" if not nome_arquivo.endswith(".pdf") else ""

    utilsPdf.exportar_para_pdf(lancamentos, nome_arquivo, "Relatório Geral - A Receber")


# Função para gerar Relatório por Conta Contábil - A Receber
def gerar_relatorio_conta_a_receber():
    contas_contabeis = ["Exposição", "Rodeio/Show", "Venda de Espaço", "Patrocinio", "Ranch Sorting", "Team Penning"]

    def filtrar_relatorio():
        conta_escolhida = combo_conta.get().lower()
        if conta_escolhida not in [c.lower() for c in contas_contabeis]:
            messagebox.showwarning("Erro", "Conta contábil inválida!")
            return

        lancamentos = database.buscar_lancamentos_por_status_e_conta("A Receber", conta_escolhida)
        if not lancamentos:
            messagebox.showinfo("Relatório por Conta - A Receber", f"Nenhum lançamento com status 'A Receber' para a conta {conta_escolhida}.")
            return

        nome_arquivo = f"relatorio_{conta_escolhida.replace('/', '-')}_a_receber.pdf"
        utilsPdf.exportar_para_pdf(lancamentos, nome_arquivo, f"Relatório por Conta - A Receber ({conta_escolhida})")

    # Interface gráfica para selecionar a conta contábil
    relatorio_janela = tk.Toplevel(root)
    relatorio_janela.title("Relatório por Conta - A Receber")
    relatorio_janela.geometry("400x200")
    tk.Label(relatorio_janela, text="Escolha a conta contábil:").pack(pady=10)

    combo_conta = ttk.Combobox(relatorio_janela, values=contas_contabeis)
    combo_conta.pack()
    btn_filtrar = tk.Button(relatorio_janela, text="Gerar Relatório", command=filtrar_relatorio)
    btn_filtrar.pack(pady=20)

def gerar_grafico_barras():
    conexao = database.conectar_banco()
    if conexao is None:
        messagebox.showerror("Erro", "Erro ao conectar ao banco de dados.")
        return

    # Consulta para obter somas de crédito e débito por conta
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

    except sqlite3.Error as e:
        logging.error(f"Erro ao gerar gráfico de barras: {e}")
        messagebox.showerror("Erro", f"Erro ao gerar gráfico de barras: {e}")
    finally:
        cursor.close()
        conexao.close()

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
        lancamentos = database.buscar_lancamentos_do_banco()
        lancamentos_filtrados = [l for l in lancamentos if l['Conta'].lower() == conta_escolhida]

        if not lancamentos_filtrados:
            messagebox.showinfo("Relatório por Conta", f"Nenhum lançamento encontrado para a conta {conta_escolhida}.")
            return

        # Exportar para PDF
        utilsPdf.exportar_para_pdf(lancamentos_filtrados, f"relatorio_{conta_escolhida.replace('/', '-')}.pdf", f"Relatório para a Conta {conta_escolhida}")

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


def abrir_tela_listagem():
    # Função para abrir a tela de listagem de lançamentos
    listagem_janela = tk.Toplevel()
    listagem_janela.title("Listagem de Lançamentos")
    listagem_janela.geometry("700x400")

    # Campo de entrada e botão de filtro
    filtro_frame = tk.Frame(listagem_janela)
    filtro_frame.pack(pady=10)

    tk.Label(filtro_frame, text="Filtrar por Empresa:").pack(side=tk.LEFT)
    entry_filtro = tk.Entry(filtro_frame, width=30)
    entry_filtro.pack(side=tk.LEFT, padx=5)

    def aplicar_filtro():
        # Obter o texto digitado e filtrar os lançamentos
        nome_empresa = entry_filtro.get().lower()
        lancamentos_filtrados = [l for l in database.buscar_todos_lancamentos() if nome_empresa in l.get("Empresa", "").lower()]

        # Limpar a Treeview antes de inserir os novos resultados
        for item in tree.get_children():
            tree.delete(item)

        # Inserir os dados filtrados na Treeview
        for lancamento in lancamentos_filtrados:
            tree.insert("", "end", values=(
                lancamento.get("Id", ""),
                lancamento.get("Empresa", ""),
                lancamento.get("Atividade", ""),
                lancamento.get("Tipo", ""),
                lancamento.get("Conta", "")
            ))

    btn_filtro = tk.Button(filtro_frame, text="Filtrar", command=aplicar_filtro)
    btn_filtro.pack(side=tk.LEFT, padx=5)

    # Configura a Treeview com colunas adicionais
    colunas = ("Id", "Empresa", "Atividade", "Tipo", "Conta")
    tree = ttk.Treeview(listagem_janela, columns=colunas, show="headings")

    # Configura cada coluna com um nome e largura específica
    tree.heading("Id", text="ID")
    tree.column("Id", width=25)  # Largura menor para o ID

    tree.heading("Empresa", text="Empresa")
    tree.column("Empresa", width=200)  # Ajuste a largura conforme necessário

    tree.heading("Atividade", text="Atividade")
    tree.column("Atividade", width=200)
    
    tree.heading("Tipo", text="Tipo")
    tree.column("Tipo", width=25)

    tree.heading("Conta", text="Conta")
    tree.column("Conta", width=150)

    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Função para carregar e exibir todos os lançamentos na Treeview
    def carregar_lancamentos():
    # Limpar todos os itens da Treeview
        for item in tree.get_children():
            tree.delete(item)
        
        # Carregar os lançamentos do banco de dados e inserir na Treeview
        lancamentos = database.buscar_todos_lancamentos()
        for lancamento in lancamentos:
            tree.insert("", "end", values=(
                lancamento.get("Id", ""),
                lancamento.get("Empresa", ""),
                lancamento.get("Atividade", ""),
                lancamento.get("Tipo", ""),
                lancamento.get("Conta", "")
            ))


    # Carrega os dados iniciais
    carregar_lancamentos()

    # Carregar o ícone de modificação (substitua pelo caminho do seu ícone)
    icon_image = Image.open("edit_icon.png").resize((16, 16))  # Ícone de 16x16
    icon = ImageTk.PhotoImage(icon_image)
    
    # Carregar o ícone de modificação (substitua pelo caminho do seu ícone)
    icon_delete_image = Image.open("delete_icon.png").resize((16, 16))  # Ícone de 16x16
    icon_delete = ImageTk.PhotoImage(icon_delete_image)

    # Função para editar o lançamento selecionado
    def editar_lancamento():
        selected_item = tree.selection()
        if selected_item:
            item = tree.item(selected_item)
            lancamento_id = item["values"][0]
            alterar_lancamento_tela(lancamento_id)
            carregar_lancamentos()

    def excluir_lancamento():
        selected_item = tree.selection()
        if selected_item:
            item = tree.item(selected_item)
            lancamento_id = item["values"][0]
            
            # Excluir o lançamento do banco de dados
            database.excluir_lancamento_no_banco(lancamento_id)
            
            # Recarregar a lista para atualizar a Treeview
            carregar_lancamentos()


    # Botão de edição com ícone
    # Cria um frame para colocar os botões lado a lado
    button_frame = tk.Frame(listagem_janela)
    button_frame.pack(pady=10)

    # Botão de edição com ícone
    btn_editar = tk.Button(button_frame, image=icon, command=editar_lancamento)
    btn_editar.icon = icon  # Necessário manter uma referência ao ícone para evitar descarte
    btn_editar.pack(side=tk.LEFT, padx=5)

    # Botão de exclusão com ícone
    btn_delete = tk.Button(button_frame, image=icon_delete, command=excluir_lancamento)
    btn_delete.icon = icon_delete  # Necessário manter uma referência ao ícone para evitar descarte
    btn_delete.pack(side=tk.LEFT, padx=5)

def criar_menu():
    global root
    root = tk.Tk()
    root.title("Sistema de Controle Contábil")
    root.geometry("600x600")

    btn_listagem = tk.Button(root, text="Abrir Listagem de Lançamentos", width=30, command=abrir_tela_listagem)
    btn_listagem.pack(pady=10)

    # Botão para adicionar lançamento
    btn_adicionar = tk.Button(root, text="Adicionar Lançamento", command=adicionar_lancamento_tela, width=30)
    btn_adicionar.pack(pady=10)

    # Botões para os relatórios gerais
    btn_relatorio_geral = tk.Button(root, text="Gerar Relatório Geral (Pago)", command=relatorios.gerar_relatorio_geral, width=30)
    btn_relatorio_geral.pack(pady=10)

    btn_relatorio_geral_a_pagar = tk.Button(root, text="Gerar Relatório Geral (A Pagar)", command=relatorios.gerar_relatorio_geral_a_pagar, width=30)
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