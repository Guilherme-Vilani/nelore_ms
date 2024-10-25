# import pyodbc
# import logging
# from tkinter import messagebox

# def conectar_banco():
#     try:
#         conexao = pyodbc.connect(
#             'DRIVER={SQL Server};'
#             'SERVER=DESKTOP-2BE72MC;'
#             'DATABASE=ControleContabil;'
#             'Trusted_Connection=yes;'
#         )
#         return conexao
#     except Exception as e:
#         logging.error(f"Erro ao conectar ao banco de dados: {e}")
#         messagebox.showerror("Erro", "Erro ao conectar ao banco de dados.")
#         return None
