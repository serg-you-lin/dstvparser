import re
from typing import List

def convert_to_float(value: str) -> float:
    """Rimuove eventuali lettere finali e converte la stringa in float"""
    #print(f"Converting: '{value}'")
    cleaned_value = re.sub(r'[a-zA-Z]+$', '', value)
    # if value != cleaned_value:
    #     print(f"Rimuovo la lettera finale: {value[-1]}, valore pulito: {cleaned_value}")
    return float(cleaned_value)

