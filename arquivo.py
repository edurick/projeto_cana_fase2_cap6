from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

try:
    from .colheita import validar_colheita
except ImportError:
    from colheita import validar_colheita


def registrar_alerta(mensagem: str, caminho: str | Path) -> None:
    caminho_arquivo = Path(caminho)
    caminho_arquivo.parent.mkdir(parents=True, exist_ok=True)

    with caminho_arquivo.open("a", encoding="utf-8") as arquivo:
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        arquivo.write(f"[{timestamp}] {mensagem}\n")


def exportar_json(lista_colheitas: list[dict], caminho: str | Path) -> None:
    caminho_arquivo = Path(caminho)
    caminho_arquivo.parent.mkdir(parents=True, exist_ok=True)

    with caminho_arquivo.open("w", encoding="utf-8") as arquivo:
        json.dump(lista_colheitas, arquivo, ensure_ascii=False, indent=4)


def importar_json(caminho: str | Path) -> list[dict]:
    caminho_arquivo = Path(caminho)

    if not caminho_arquivo.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_arquivo}")

    with caminho_arquivo.open("r", encoding="utf-8") as arquivo:
        conteudo = json.load(arquivo)

    if not isinstance(conteudo, list):
        raise ValueError("O JSON precisa conter uma lista de colheitas.")

    colheitas = []
    for indice, item in enumerate(conteudo, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"O item {indice} do JSON não é um objeto válido.")
        try:
            colheitas.append(validar_colheita(item))
        except ValueError as exc:
            raise ValueError(f"Erro no registro {indice}: {exc}") from exc

    return colheitas
