import sqlite3  # Substituir pyodbc por sqlite3
import logging
from tkinter import messagebox
import services.lancamento_services

# Função para conectar ao banco de dados SQLite
def conectar_banco():
    try:
        conexao = sqlite3.connect("nelore.db")  # Nome do banco de dados SQLite
        return conexao
    except Exception as e:
        logging.error(f"Erro ao conectar ao banco de dados: {e}")
        messagebox.showerror("Erro", "Erro ao conectar ao banco de dados.")
        return None
    
# Atualizada para ordenar os lançamentos por data
def buscar_lancamentos_do_banco():
    conexao = conectar_banco()
    if conexao is None:
        return []

    # Adiciona ORDER BY Data para ordenar pela data do lançamento
    query = "SELECT Id, Data, Empresa, Atividade, Observacao, Tipo, Valor, Conta, Status, Data_Vencimento FROM Lancamentos ORDER BY Data"

    try:
        cursor = conexao.cursor()
        cursor.execute(query)
        lancamentos = cursor.fetchall()
        return services.lancamento_services.processar_lancamentos(lancamentos)
    except sqlite3.Error as e:
        logging.error(f"Erro ao buscar lançamentos: {e}")
        return []
    finally:
        cursor.close()
        conexao.close()

# Atualizada para ordenar os lançamentos por data
def buscar_lancamentos_por_status(status):
    conexao = conectar_banco()
    if conexao is None:
        return []

    # Adiciona ORDER BY Data para ordenar pela data do lançamento
    query = "SELECT Id, Data, Empresa, Atividade, Observacao, Tipo, Valor, Conta, Status, Data_Vencimento FROM Lancamentos WHERE Status = ? ORDER BY Data"
    
    try:
        cursor = conexao.cursor()
        cursor.execute(query, (status,))
        lancamentos = cursor.fetchall()
        return lancamentos.processar_lancamentos(lancamentos)
    except sqlite3.Error as e:
        logging.error(f"Erro ao buscar lançamentos por status: {e}")
        return []
    finally:
        cursor.close()
        conexao.close()

# Atualizada para ordenar os lançamentos por data
def buscar_lancamentos_por_status_e_conta(status, conta):
    conexao = conectar_banco()
    if conexao is None:
        return []

    # Adiciona ORDER BY Data para ordenar pela data do lançamento
    query = "SELECT Id, Data, Empresa, Atividade, Observacao, Tipo, Valor, Conta, Status, Data_Vencimento FROM Lancamentos WHERE Status = ? AND Conta = ? ORDER BY Data"

    try:
        cursor = conexao.cursor()
        cursor.execute(query, (status, conta))
        return services.lancamento_services.processar_lancamentos(cursor.fetchall())
    except sqlite3.Error as e:
        logging.error(f"Erro ao buscar lançamentos por status e conta: {e}")
        return []
    finally:
        cursor.close()
        conexao.close()

def salvar_lancamento_no_banco(lancamento):
    conexao = conectar_banco()
    if conexao is None:
        return

    query = '''
    INSERT INTO Lancamentos (Data, Empresa, Atividade, Observacao, Tipo, Valor, Conta, Status, Data_Vencimento)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''

    try:
        cursor = conexao.cursor()
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
    except sqlite3.Error as e:
        logging.error(f"Erro ao salvar o lançamento: {e}")
        messagebox.showerror("Erro", f"Erro ao salvar o lançamento: {e}")
    finally:
        cursor.close()
        conexao.close()

def atualizar_lancamento_no_banco(lancamento_id, lancamento_atualizado):
    conexao = conectar_banco()
    if conexao is None:
        return

    query = '''
    UPDATE Lancamentos SET Data = ?, Empresa = ?, Atividade = ?, Observacao = ?, Tipo = ?, Valor = ?, Conta = ?, Status = ?, Data_Vencimento = ?
    WHERE Id = ?
    '''

    print(lancamento_atualizado)

    try:
        cursor = conexao.cursor()
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
        conexao.commit()
        messagebox.showinfo("Sucesso", "Lançamento atualizado com sucesso!")
    except sqlite3.Error as e:
        logging.error(f"Erro ao atualizar o lançamento: {e}")
        messagebox.showerror("Erro", f"Erro ao atualizar o lançamento: {e}")
    finally:
        cursor.close()
        conexao.close()

def excluir_lancamento_no_banco(lancamento_id):
    conexao = conectar_banco()
    if conexao is None:
        return

    query = "DELETE FROM Lancamentos WHERE Id = ?"

    try:
        cursor = conexao.cursor()
        cursor.execute(query, (lancamento_id,))
        conexao.commit()
        messagebox.showinfo("Sucesso", "Lançamento excluído com sucesso!")
    except sqlite3.Error as e:
        logging.error(f"Erro ao excluir o lançamento: {e}")
        messagebox.showerror("Erro", f"Erro ao excluir o lançamento: {e}")
    finally:
        cursor.close()
        conexao.close()