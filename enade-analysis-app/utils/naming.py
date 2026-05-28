"""
utils/naming.py
---------------
Lógica centralizada de prioridade para nomear um conjunto de filtros
de instituição/localidade no contexto do painel ENADE 2023.

Hierarquia de prioridade (maior → menor):
  1. IES  – 1 selecionada → nome completo; N > 1 → "N IES Selecionadas"
  2. Município – sem IES → "Município X" | "N Municípios"
  3. UF   – sem IES nem município → "UF X" | "N Estados"
  4. Nacional – nenhum filtro geográfico/institucional → "Contagem Nacional"

No modo comparação, quando os dois lados produzem o mesmo rótulo,
a função `disambiguate_names` acrescenta um sufixo de curso ou índice.
"""

from __future__ import annotations
from typing import Sequence


def _list(val) -> list:
    """Normaliza qualquer entrada para list (incluindo None, [], tuple)."""
    if not val:
        return []
    if isinstance(val, str):
        return [val]
    return list(val)


def resolve_institution_name(
    ies: Sequence[str] | None = None,
    municipio: Sequence[str] | None = None,
    uf: Sequence[str] | None = None,
    fallback: str = "Contagem Nacional",
) -> str:
    """
    Retorna o título mais descritivo possível para um lado do painel,
    respeitando a hierarquia IES > Município > UF > Nacional.

    Parâmetros
    ----------
    ies       : lista de IES selecionadas (campo 'Nome da IES*')
    municipio : lista de municípios selecionados
    uf        : lista de UFs selecionadas
    fallback  : texto quando nenhum filtro geográfico/institucional está ativo
    """
    ies_list  = _list(ies)
    mun_list  = _list(municipio)
    uf_list   = _list(uf)

    # 1. IES (prioridade máxima)
    if ies_list:
        n = len(ies_list)
        if n == 1:
            return ies_list[0]
        return f"{n} IES Selecionadas"

    # 2. Município
    if mun_list:
        n = len(mun_list)
        if n == 1:
            return mun_list[0]
        return f"{n} Municípios"

    # 3. UF
    if uf_list:
        n = len(uf_list)
        if n == 1:
            return uf_list[0]
        return f"{n} Estados"

    # 4. Nacional (nenhum filtro geográfico/institucional ativo)
    return fallback


def disambiguate_names(
    nome1: str,
    nome2: str,
    curso1: Sequence[str] | None = None,
    curso2: Sequence[str] | None = None,
    suffix1: str = "(1)",
    suffix2: str = "(2)",
) -> tuple[str, str]:
    """
    Quando nome1 == nome2, diferencia os rótulos usando o curso selecionado
    (se único e diferente) ou sufixos numéricos simples.

    Retorna (nome1_final, nome2_final).
    """
    if nome1 != nome2:
        return nome1, nome2

    c1 = _list(curso1)
    c2 = _list(curso2)

    if len(c1) == 1 and len(c2) == 1 and c1[0] != c2[0]:
        return f"{nome1} ({c1[0]})", f"{nome2} ({c2[0]})"

    return f"{nome1} {suffix1}", f"{nome2} {suffix2}"
