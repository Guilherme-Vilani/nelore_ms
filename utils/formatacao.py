import locale
import decimal
from datetime import datetime

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

def formatar_moeda(valor):
    try:
        valor = float(valor)
        return locale.currency(valor, grouping=True, symbol=True)
    except ValueError:
        return "Valor inválido"

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
