import locale
import decimal
from datetime import datetime


def formatar_moeda(valor):
    try:
        valor = float(valor)
        return locale.currency(valor, grouping=True, symbol=True)
    except ValueError:
        return "Valor inválido"

# Função para converter valor de string ou decimal para float (corrigido)
def converter_valor_para_float(valor_str):
    try:
        if isinstance(valor_str, (float, int, decimal.Decimal)):
            return float(valor_str)
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
            data_formatada = datetime.strptime(data, '%Y-%m-%d')
            return data_formatada.strftime('%d/%m/%Y')
        except ValueError:
            return data
    return data