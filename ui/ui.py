from tkinter import ttk, messagebox, Tk, Toplevel
from datetime import datetime
from database import database

def adicionar_lancamento_tela(root):
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
            'Status': status,
            'Data_Vencimento': data_vencimento_formatada
        }

        database.salvar_lancamento_no_banco(lancamento)
        adicionar_janela.destroy()

    # Cria a janela para adicionar o lançamento
    adicionar_janela = Toplevel(root)
    adicionar_janela.title("Adicionar Lançamento")
    adicionar_janela.geometry("550x550")

    # Campos de entrada
    ttk.Label(adicionar_janela, text="Data (dd/mm/yyyy):").pack()
    entry_data = ttk.Entry(adicionar_janela)
    entry_data.pack()

    ttk.Label(adicionar_janela, text="Empresa:").pack()
    entry_empresa = ttk.Entry(adicionar_janela)
    entry_empresa.pack()

    ttk.Label(adicionar_janela, text="Atividade:").pack()
    entry_atividade = ttk.Entry(adicionar_janela)
    entry_atividade.pack()
    
    ttk.Label(adicionar_janela, text="Observação:").pack()
    entry_observacao = ttk.Entry(adicionar_janela)
    entry_observacao.pack()

    ttk.Label(adicionar_janela, text="Tipo (C/D):").pack()
    entry_tipo = ttk.Entry(adicionar_janela)
    entry_tipo.pack()

    ttk.Label(adicionar_janela, text="Valor:").pack()
    entry_valor = ttk.Entry(adicionar_janela)
    entry_valor.pack()

    ttk.Label(adicionar_janela, text="Conta Contábil:").pack()
    contas_contabeis = ["Exposição", "Rodeio/Show", "Venda de Espaço", "Patrocinio", "Ranch Sorting", "Team Penning"]
    combo_conta = ttk.Combobox(adicionar_janela, values=contas_contabeis)
    combo_conta.pack()

    ttk.Label(adicionar_janela, text="Status:").pack()
    opcoes_status = ["A receber", "A Pagar", "Pago"]
    combo_status = ttk.Combobox(adicionar_janela, values=opcoes_status)
    combo_status.pack()

    ttk.Label(adicionar_janela, text="Data de Vencimento (dd/mm/yyyy):").pack()
    entry_data_vencimento = ttk.Entry(adicionar_janela)
    entry_data_vencimento.pack()

    btn_salvar = ttk.Button(adicionar_janela, text="Salvar", command=salvar)
    btn_salvar.pack(pady=10)

# Inicializa a janela principal
root = Tk()
root.title("Sistema de Controle Contábil")
root.geometry("600x600")

# Botão para abrir a janela de adicionar lançamento
btn_adicionar = ttk.Button(root, text="Adicionar Lançamento", command=lambda: adicionar_lancamento_tela(root))
btn_adicionar.pack(pady=10)

root.mainloop()