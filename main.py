from __future__ import annotations

from pathlib import Path

try:
    from .arquivo import exportar_json, importar_json, registrar_alerta
    from .banco import (
        BancoIndisponivelError,
        atualizar_colheita_oracle,
        excluir_colheita_oracle,
        inserir_colheita_oracle,
        listar_colheitas_oracle,
    )
    from .colheita import (
        calcular_perda,
        chave_duplicidade,
        classificar_perda,
        exibir_relatorio,
        filtrar_colheitas,
        formatar_status,
        validar_colheita,
    )
except ImportError:
    from arquivo import exportar_json, importar_json, registrar_alerta
    from banco import (
        BancoIndisponivelError,
        atualizar_colheita_oracle,
        excluir_colheita_oracle,
        inserir_colheita_oracle,
        listar_colheitas_oracle,
    )
    from colheita import (
        calcular_perda,
        chave_duplicidade,
        classificar_perda,
        exibir_relatorio,
        filtrar_colheitas,
        formatar_status,
        validar_colheita,
    )

BASE_DIR = Path(__file__).resolve().parent
DADOS_DIR = BASE_DIR / "dados"
CAMINHO_JSON_PADRAO = DADOS_DIR / "colheitas.json"
CAMINHO_ALERTAS = DADOS_DIR / "alertas.txt"


def exibir_menu() -> None:
    print("=" * 68)
    print("SISTEMA DE GESTÃO DE PERDAS NA COLHEITA DE CANA-DE-AÇÚCAR")
    print("=" * 68)
    print("1. Registrar colheita")
    print("2. Listar colheitas")
    print("3. Calcular perdas")
    print("4. Atualizar colheita")
    print("5. Excluir colheita")
    print("6. Gerar relatório")
    print("7. Exportar dados")
    print("8. Importar dados")
    print("9. Sair")


def carregar_colheitas_iniciais() -> list[dict]:
    try:
        colheitas = listar_colheitas_oracle()
        print(f"\n{len(colheitas)} colheita(s) carregada(s) do Oracle.\n")
        return colheitas
    except BancoIndisponivelError as exc:
        print(f"\nOracle indisponível no início da sessão: {exc}")
        print("A aplicação seguirá com a lista em memória, JSON e log de alertas.\n")
        return []


def coletar_filtros() -> dict:
    print("\nDeixe em branco para não aplicar o filtro.")
    id_talhao = input("Filtrar por talhão: ").strip()
    tipo_colheita = input("Filtrar por tipo (manual/mecanica): ").strip()
    status_perda = input("Filtrar por status (Aceitável/Atenção/Crítico): ").strip()

    filtros = {}
    if id_talhao:
        filtros["id_talhao"] = id_talhao
    if tipo_colheita:
        filtros["tipo_colheita"] = tipo_colheita
    if status_perda:
        filtros["status_perda"] = status_perda
    return filtros


def exibir_colheitas(lista_colheitas: list[dict]) -> None:
    if not lista_colheitas:
        print("\nNenhuma colheita encontrada.\n")
        return

    print("\n" + "-" * 120)
    print(
        f"{'Nº':<4}{'ID DB':<8}{'Talhão':<12}{'Área(ha)':<10}{'Est.(t)':<12}"
        f"{'Real.(t)':<12}{'Tipo':<12}{'Data':<12}{'Perda %':<10}Status"
    )
    print("-" * 120)

    for indice, colheita in enumerate(lista_colheitas, start=1):
        id_banco = colheita.get("id_colheita", "-")
        print(
            f"{indice:<4}{str(id_banco):<8}{colheita['id_talhao']:<12}"
            f"{colheita['area_ha']:<10.2f}{colheita['producao_estimada_ton']:<12.2f}"
            f"{colheita['producao_realizada_ton']:<12.2f}{colheita['tipo_colheita']:<12}"
            f"{colheita['data_colheita']:<12}{colheita['percentual_perda']:<10.2f}"
            f"{formatar_status(colheita['status_perda'])}"
        )

    print("-" * 120 + "\n")


def selecionar_colheita(lista_colheitas: list[dict], acao: str) -> int | None:
    if not lista_colheitas:
        print(f"\nNenhuma colheita disponível para {acao}.\n")
        return None

    exibir_colheitas(lista_colheitas)

    while True:
        escolha = input(
            f"Informe o número da colheita para {acao} "
            "(ou pressione Enter para cancelar): "
        ).strip()

        if escolha == "":
            return None

        if not escolha.isdigit():
            print("Digite um número válido.")
            continue

        indice = int(escolha) - 1
        if 0 <= indice < len(lista_colheitas):
            return indice

        print("Índice fora da faixa exibida.")


def ler_campo(rotulo: str, valor_atual: object | None = None) -> str:
    if valor_atual is None:
        return input(f"{rotulo}: ").strip()

    entrada = input(f"{rotulo} [{valor_atual}]: ").strip()
    return entrada if entrada else str(valor_atual)


def coletar_dados_colheita(colheita_atual: dict | None = None) -> dict:
    return {
        "id_talhao": ler_campo(
            "ID do talhão",
            colheita_atual["id_talhao"] if colheita_atual else None,
        ),
        "area_ha": ler_campo(
            "Área colhida em hectares",
            colheita_atual["area_ha"] if colheita_atual else None,
        ),
        "producao_estimada_ton": ler_campo(
            "Produção estimada (t)",
            colheita_atual["producao_estimada_ton"] if colheita_atual else None,
        ),
        "producao_realizada_ton": ler_campo(
            "Produção realizada (t)",
            colheita_atual["producao_realizada_ton"] if colheita_atual else None,
        ),
        "tipo_colheita": ler_campo(
            "Tipo de colheita (manual/mecanica)",
            colheita_atual["tipo_colheita"] if colheita_atual else None,
        ),
        "data_colheita": ler_campo(
            "Data da colheita (DD/MM/AAAA)",
            colheita_atual["data_colheita"] if colheita_atual else None,
        ),
    }


def registrar_alerta_critico(colheita: dict) -> None:
    if colheita["status_perda"] != "Crítico":
        return

    mensagem = (
        f"Talhão {colheita['id_talhao']} com perda crítica de "
        f"{colheita['percentual_perda']:.2f}% "
        f"({colheita['tipo_colheita']}) em {colheita['data_colheita']}."
    )
    registrar_alerta(mensagem, CAMINHO_ALERTAS)


def registrar_colheita(lista_colheitas: list[dict]) -> None:
    print("\nCadastro de nova colheita")
    dados = coletar_dados_colheita()

    try:
        colheita = validar_colheita(dados)
    except ValueError as exc:
        print(f"Erro de validação: {exc}\n")
        return

    try:
        colheita["id_colheita"] = inserir_colheita_oracle(colheita)
        print("Colheita registrada no Oracle com sucesso.")
    except BancoIndisponivelError as exc:
        print(f"Oracle indisponível: {exc}")
        print("A colheita será mantida apenas em memória nesta sessão.")

    lista_colheitas.append(colheita)
    registrar_alerta_critico(colheita)
    print("Colheita registrada com sucesso.\n")


def listar_colheitas(lista_colheitas: list[dict]) -> None:
    filtros = coletar_filtros()
    try:
        resultado = filtrar_colheitas(lista_colheitas, **filtros)
    except ValueError as exc:
        print(f"Erro ao aplicar filtros: {exc}\n")
        return

    exibir_colheitas(resultado)


def calcular_perdas_colheita(lista_colheitas: list[dict]) -> None:
    indice = selecionar_colheita(lista_colheitas, "calcular a perda")
    if indice is None:
        print()
        return

    colheita = lista_colheitas[indice]
    percentual = calcular_perda(
        colheita["producao_estimada_ton"], colheita["producao_realizada_ton"]
    )
    status = classificar_perda(percentual, colheita["tipo_colheita"])

    print("\nResumo da colheita selecionada")
    print(f"Talhão: {colheita['id_talhao']}")
    print(f"Tipo: {colheita['tipo_colheita']}")
    print(f"Data: {colheita['data_colheita']}")
    print(f"Perda calculada: {percentual:.2f}%")
    print(f"Classificação: {formatar_status(status)}\n")


def atualizar_colheita(lista_colheitas: list[dict]) -> None:
    indice = selecionar_colheita(lista_colheitas, "atualizar")
    if indice is None:
        print()
        return

    colheita_atual = lista_colheitas[indice]
    print("\nInforme os novos valores. Pressione Enter para manter o valor atual.")
    dados = coletar_dados_colheita(colheita_atual)

    try:
        colheita_atualizada = validar_colheita(
            {**dados, "id_colheita": colheita_atual.get("id_colheita")}
        )
    except ValueError as exc:
        print(f"Erro de validação: {exc}\n")
        return

    id_colheita = colheita_atual.get("id_colheita")
    if id_colheita is not None:
        try:
            atualizar_colheita_oracle(id_colheita, colheita_atualizada)
            print("Colheita atualizada no Oracle.")
        except BancoIndisponivelError as exc:
            print(f"Oracle indisponível: {exc}")
            print("A alteração será mantida apenas em memória nesta sessão.")

    lista_colheitas[indice] = colheita_atualizada
    registrar_alerta_critico(colheita_atualizada)
    print("Colheita atualizada com sucesso.\n")


def excluir_colheita(lista_colheitas: list[dict]) -> None:
    indice = selecionar_colheita(lista_colheitas, "excluir")
    if indice is None:
        print()
        return

    colheita = lista_colheitas[indice]
    confirmacao = input(
        f"Confirma a exclusão do talhão {colheita['id_talhao']}? (s/n): "
    ).strip().lower()
    if confirmacao != "s":
        print("Exclusão cancelada.\n")
        return

    id_colheita = colheita.get("id_colheita")
    if id_colheita is not None:
        try:
            excluir_colheita_oracle(id_colheita)
            lista_colheitas.pop(indice)
            print("Colheita removida do Oracle e da sessão.\n")
        except BancoIndisponivelError as exc:
            print(f"Não foi possível excluir do Oracle: {exc}")
            print("O registro foi mantido em memória para evitar inconsistência.\n")
        return

    lista_colheitas.pop(indice)
    print("Colheita removida da sessão.\n")


def gerar_relatorio(lista_colheitas: list[dict]) -> None:
    if not lista_colheitas:
        print("\nNenhuma colheita disponível para o relatório.\n")
        return

    print("\nEscolha o agrupamento do relatório:")
    print("1. Mensal")
    print("2. Tipo de colheita")
    opcao = input("Opção: ").strip()

    agrupamento = "mensal" if opcao != "2" else "tipo"
    exibir_relatorio(lista_colheitas, agrupamento=agrupamento)


def exportar_dados(lista_colheitas: list[dict]) -> None:
    destino = input(
        f"Caminho do arquivo JSON [{CAMINHO_JSON_PADRAO}]: "
    ).strip()
    caminho = Path(destino) if destino else CAMINHO_JSON_PADRAO

    try:
        exportar_json(lista_colheitas, caminho)
        print(f"Dados exportados com sucesso para {caminho}.\n")
    except OSError as exc:
        print(f"Erro ao exportar o JSON: {exc}\n")


def importar_dados(lista_colheitas: list[dict]) -> None:
    origem = input(
        f"Caminho do arquivo JSON [{CAMINHO_JSON_PADRAO}]: "
    ).strip()
    caminho = Path(origem) if origem else CAMINHO_JSON_PADRAO

    try:
        colheitas_importadas = importar_json(caminho)
    except (FileNotFoundError, ValueError, OSError) as exc:
        print(f"Erro ao importar dados: {exc}\n")
        return

    chaves_existentes = {chave_duplicidade(item) for item in lista_colheitas}
    adicionadas = 0
    ignoradas = 0
    erro_oracle: str | None = None

    for colheita in colheitas_importadas:
        chave = chave_duplicidade(colheita)
        if chave in chaves_existentes:
            ignoradas += 1
            continue

        if erro_oracle is None:
            try:
                colheita["id_colheita"] = inserir_colheita_oracle(colheita)
            except BancoIndisponivelError as exc:
                erro_oracle = str(exc)

        lista_colheitas.append(colheita)
        chaves_existentes.add(chave)
        adicionadas += 1
        registrar_alerta_critico(colheita)

    print(
        f"Importação concluída: {adicionadas} nova(s) colheita(s), "
        f"{ignoradas} ignorada(s) por duplicidade."
    )
    if erro_oracle:
        print(f"Oracle indisponível durante a importação: {erro_oracle}")
        print("Os registros novos foram mantidos apenas em memória.")
    print()


def main() -> None:
    DADOS_DIR.mkdir(parents=True, exist_ok=True)
    lista_colheitas = carregar_colheitas_iniciais()

    while True:
        exibir_menu()
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            registrar_colheita(lista_colheitas)
        elif opcao == "2":
            listar_colheitas(lista_colheitas)
        elif opcao == "3":
            calcular_perdas_colheita(lista_colheitas)
        elif opcao == "4":
            atualizar_colheita(lista_colheitas)
        elif opcao == "5":
            excluir_colheita(lista_colheitas)
        elif opcao == "6":
            gerar_relatorio(lista_colheitas)
        elif opcao == "7":
            exportar_dados(lista_colheitas)
        elif opcao == "8":
            importar_dados(lista_colheitas)
        elif opcao == "9":
            print("\nEncerrando o sistema.\n")
            break
        else:
            print("Opção inválida. Tente novamente.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExecução interrompida pelo usuário.\n")
