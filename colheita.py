from __future__ import annotations

from collections import defaultdict
from datetime import datetime

LIMITES_PERDA = {
    "manual": (5.0, 10.0),
    "mecanica": (10.0, 15.0),
}

STATUS_COM_ICONES = {
    "Aceitável": "✅ Aceitável",
    "Atenção": "⚠️ Atenção",
    "Crítico": "🚨 Crítico",
}


def calcular_perda(estimada: float, realizada: float) -> float:
    """Calcula o percentual de perda com base na produção estimada e realizada."""
    estimada = float(estimada)
    realizada = float(realizada)

    if estimada <= 0:
        raise ValueError("A produção estimada deve ser maior que zero.")

    if realizada < 0:
        raise ValueError("A produção realizada não pode ser negativa.")

    if realizada > estimada:
        raise ValueError("A produção realizada não pode ser maior que a produção estimada.")

    percentual = ((estimada - realizada) / estimada) * 100
    return round(percentual, 2)


def classificar_perda(percentual: float, tipo: str) -> str:
    """Classifica a perda conforme o tipo de colheita."""
    tipo_normalizado = normalizar_tipo_colheita(tipo)
    limite_aceitavel, limite_critico = LIMITES_PERDA[tipo_normalizado]

    if percentual <= limite_aceitavel:
        return "Aceitável"
    if percentual <= limite_critico:
        return "Atenção"
    return "Crítico"


def normalizar_tipo_colheita(tipo: str) -> str:
    tipo_normalizado = str(tipo).strip().lower()
    if tipo_normalizado not in LIMITES_PERDA:
        raise ValueError("O tipo de colheita deve ser 'manual' ou 'mecanica'.")
    return tipo_normalizado


def validar_data(data_colheita: str) -> str:
    try:
        return datetime.strptime(str(data_colheita).strip(), "%d/%m/%Y").strftime("%d/%m/%Y")
    except ValueError as exc:
        raise ValueError("A data da colheita deve estar no formato DD/MM/AAAA.") from exc


def validar_numero_positivo(valor: object, nome_campo: str) -> float:
    try:
        numero = float(str(valor).strip())
    except (TypeError, ValueError) as exc:
        raise ValueError(f"O campo '{nome_campo}' deve ser numérico.") from exc

    if numero <= 0:
        raise ValueError(f"O campo '{nome_campo}' deve ser maior que zero.")
    return round(numero, 2)


def validar_colheita(dados: dict) -> dict:
    """Valida, normaliza e enriquece uma colheita com perda e status."""
    campos_obrigatorios = (
        "id_talhao",
        "area_ha",
        "producao_estimada_ton",
        "producao_realizada_ton",
        "tipo_colheita",
        "data_colheita",
    )

    for campo in campos_obrigatorios:
        if campo not in dados:
            raise ValueError(f"O campo '{campo}' é obrigatório.")

        valor = dados[campo]
        if valor is None or str(valor).strip() == "":
            raise ValueError(f"O campo '{campo}' não pode ser vazio.")

    id_talhao = str(dados["id_talhao"]).strip().upper()
    area_ha = validar_numero_positivo(dados["area_ha"], "area_ha")
    producao_estimada = validar_numero_positivo(
        dados["producao_estimada_ton"], "producao_estimada_ton"
    )
    producao_realizada = validar_numero_positivo(
        dados["producao_realizada_ton"], "producao_realizada_ton"
    )
    tipo_colheita = normalizar_tipo_colheita(dados["tipo_colheita"])
    data_colheita = validar_data(dados["data_colheita"])

    percentual_perda = calcular_perda(producao_estimada, producao_realizada)
    status_perda = classificar_perda(percentual_perda, tipo_colheita)

    colheita_validada = {
        "id_talhao": id_talhao,
        "area_ha": area_ha,
        "producao_estimada_ton": producao_estimada,
        "producao_realizada_ton": producao_realizada,
        "tipo_colheita": tipo_colheita,
        "data_colheita": data_colheita,
        "percentual_perda": percentual_perda,
        "status_perda": status_perda,
    }

    id_colheita = dados.get("id_colheita")
    if id_colheita not in (None, ""):
        try:
            colheita_validada["id_colheita"] = int(id_colheita)
        except (TypeError, ValueError) as exc:
            raise ValueError("O campo 'id_colheita' deve ser inteiro quando informado.") from exc

    return colheita_validada


def chave_duplicidade(colheita: dict) -> tuple:
    return (
        str(colheita["id_talhao"]).strip().upper(),
        round(float(colheita["area_ha"]), 2),
        round(float(colheita["producao_estimada_ton"]), 2),
        round(float(colheita["producao_realizada_ton"]), 2),
        normalizar_tipo_colheita(colheita["tipo_colheita"]),
        validar_data(colheita["data_colheita"]),
    )


def filtrar_colheitas(
    lista_colheitas: list[dict],
    id_talhao: str | None = None,
    tipo_colheita: str | None = None,
    status_perda: str | None = None,
) -> list[dict]:
    resultado = list(lista_colheitas)

    if id_talhao:
        talhao = id_talhao.strip().upper()
        resultado = [item for item in resultado if item["id_talhao"] == talhao]

    if tipo_colheita:
        tipo = normalizar_tipo_colheita(tipo_colheita)
        resultado = [item for item in resultado if item["tipo_colheita"] == tipo]

    if status_perda:
        status = status_perda.strip().lower()
        resultado = [
            item for item in resultado if item["status_perda"].strip().lower() == status
        ]

    return resultado


def formatar_status(status: str) -> str:
    return STATUS_COM_ICONES.get(status, status)


def _rotulo_grupo(colheita: dict, agrupamento: str) -> str:
    if agrupamento == "tipo":
        return colheita["tipo_colheita"].capitalize()

    data_obj = datetime.strptime(colheita["data_colheita"], "%d/%m/%Y")
    return data_obj.strftime("%m/%Y")


def _data_ordenacao(colheita: dict) -> datetime:
    return datetime.strptime(colheita["data_colheita"], "%d/%m/%Y")


def exibir_relatorio(lista_colheitas: list[dict], agrupamento: str = "mensal") -> None:
    """Imprime um relatório formatado agrupado por mês/ano ou tipo de colheita."""
    if not lista_colheitas:
        print("\nNenhuma colheita disponível para o relatório.\n")
        return

    agrupamento = agrupamento.strip().lower()
    if agrupamento not in {"mensal", "tipo"}:
        raise ValueError("O agrupamento do relatório deve ser 'mensal' ou 'tipo'.")

    grupos: dict[str, list[dict]] = defaultdict(list)
    for colheita in lista_colheitas:
        grupos[_rotulo_grupo(colheita, agrupamento)].append(colheita)

    print("\n" + "=" * 84)
    print("RELATÓRIO DE PERDAS — COLHEITA DE CANA")
    print("=" * 84)

    for grupo in sorted(grupos):
        itens = grupos[grupo]
        media_grupo = sum(item["percentual_perda"] for item in itens) / len(itens)
        print(f"\nGrupo: {grupo}")
        print("-" * 84)
        print(
            f"{'Talhão':<12}{'Tipo':<12}{'Data':<14}{'Est.(t)':<12}"
            f"{'Real.(t)':<12}{'Perda %':<10}Status"
        )

        for item in sorted(itens, key=_data_ordenacao):
            print(
                f"{item['id_talhao']:<12}{item['tipo_colheita']:<12}"
                f"{item['data_colheita']:<14}{item['producao_estimada_ton']:<12.2f}"
                f"{item['producao_realizada_ton']:<12.2f}"
                f"{item['percentual_perda']:<10.2f}{formatar_status(item['status_perda'])}"
            )

        print(
            f"Média do grupo: {media_grupo:.2f}% | Total de colheitas no grupo: {len(itens)}"
        )

    media_geral = sum(item["percentual_perda"] for item in lista_colheitas) / len(lista_colheitas)
    print("-" * 84)
    print(f"Média geral de perda: {media_geral:.2f}%")
    print(f"Total de colheitas registradas: {len(lista_colheitas)}")
    print("=" * 84 + "\n")
