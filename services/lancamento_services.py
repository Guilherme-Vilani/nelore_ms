import utils.utils as utils

def processar_lancamentos(lancamentos):
    lista_lancamentos = []
    for row in lancamentos:
        data_formatada = utils.formatar_data(row[1])
        data_vencimento_formatada = utils.formatar_data(row[9])

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