import tkinter as tk
from ui.lancamentos import adicionar_lancamento_tela, alterar_lancamento_tela, excluir_lancamento_tela
from ui.relatorios import gerar_relatorio_geral, gerar_relatorio_por_conta

root = tk.Tk()

def criar_menu():
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

    btn_relatorio_conta = tk.Button(root, text="Gerar Relatório por Conta Contábil", command=gerar_relatorio_por_conta, width=30)
    btn_relatorio_conta.pack(pady=10)

    btn_sair = tk.Button(root, text="Sair", command=root.quit, width=30)
    btn_sair.pack(pady=10)

    # Chamar o loop principal do Tkinter para exibir a janela
    root.mainloop()
