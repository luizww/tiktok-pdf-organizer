"""Extração segura dos códigos de rastreio usados no pareamento."""

import re


# Exatamente 13 dígitos, começando por 332, sem fazer parte de um número maior.
TRACKING_PATTERN = re.compile(r"(?<!\d)(332\d{10})(?!\d)")


def extract_trackings(text: str) -> tuple[str, ...]:
    """Retorna os trackings únicos encontrados, preservando a ordem."""

    return tuple(dict.fromkeys(TRACKING_PATTERN.findall(text)))
