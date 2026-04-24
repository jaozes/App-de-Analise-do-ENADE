import pandas as pd


def format_br_number(value: float, decimal_places: int = 0) -> str:
    """Formata número para o padrão brasileiro (ponto para milhares, vírgula para decimal)."""
    if pd.isna(value):
        return ""
    if decimal_places == 0:
        return f"{int(value):,}".replace(",", ".")
    else:
        return f"{value:,.{decimal_places}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_br_percentage(value: float) -> str:
    """Formata percentual para o padrão brasileiro."""
    if pd.isna(value):
        return ""
    return f"{value:.2f}%".replace(".", ",")

