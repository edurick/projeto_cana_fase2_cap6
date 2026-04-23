from __future__ import annotations

import os

try:
    import oracledb
except ModuleNotFoundError:
    oracledb = None


class BancoIndisponivelError(RuntimeError):
    """Erro para falhas de driver, configuração ou conexão do Oracle."""


def obter_conexao():
    if oracledb is None:
        raise BancoIndisponivelError(
            "Biblioteca 'oracledb' não encontrada. Instale o driver para habilitar o Oracle."
        )

    configuracao = {
        "ORACLE_USER": os.getenv("ORACLE_USER"),
        "ORACLE_PASSWORD": os.getenv("ORACLE_PASSWORD"),
        "ORACLE_DSN": os.getenv("ORACLE_DSN"),
    }
    faltantes = [nome for nome, valor in configuracao.items() if not valor]
    if faltantes:
        raise BancoIndisponivelError(
            "Defina as variáveis de ambiente: " + ", ".join(faltantes)
        )

    try:
        return oracledb.connect(
            user=configuracao["ORACLE_USER"],
            password=configuracao["ORACLE_PASSWORD"],
            dsn=configuracao["ORACLE_DSN"],
        )
    except Exception as exc:
        raise BancoIndisponivelError(f"Falha ao conectar ao Oracle: {exc}") from exc


def _mapear_linha_para_colheita(linha) -> dict:
    return {
        "id_colheita": int(linha[0]),
        "id_talhao": str(linha[1]).strip(),
        "area_ha": round(float(linha[2]), 2),
        "producao_estimada_ton": round(float(linha[3]), 2),
        "producao_realizada_ton": round(float(linha[4]), 2),
        "tipo_colheita": str(linha[5]).strip().lower(),
        "data_colheita": linha[6],
        "percentual_perda": round(float(linha[7]), 2),
        "status_perda": str(linha[8]).strip(),
    }


def _parametros_colheita(colheita: dict) -> dict:
    return {
        "id_talhao": colheita["id_talhao"],
        "area_ha": colheita["area_ha"],
        "producao_estimada": colheita["producao_estimada_ton"],
        "producao_realizada": colheita["producao_realizada_ton"],
        "tipo_colheita": colheita["tipo_colheita"],
        "data_colheita": colheita["data_colheita"],
        "percentual_perda": colheita["percentual_perda"],
        "status_perda": colheita["status_perda"],
    }


def listar_colheitas_oracle(filtros: dict | None = None) -> list[dict]:
    filtros = filtros or {}
    parametros = {}
    consulta = [
        "SELECT",
        "    ID_COLHEITA,",
        "    ID_TALHAO,",
        "    AREA_HA,",
        "    PRODUCAO_ESTIMADA,",
        "    PRODUCAO_REALIZADA,",
        "    TIPO_COLHEITA,",
        "    TO_CHAR(DATA_COLHEITA, 'DD/MM/YYYY') AS DATA_COLHEITA_FORMATADA,",
        "    PERCENTUAL_PERDA,",
        "    STATUS_PERDA",
        "FROM TB_COLHEITA",
        "WHERE 1 = 1",
    ]

    if filtros.get("id_talhao"):
        consulta.append("AND UPPER(ID_TALHAO) = :id_talhao")
        parametros["id_talhao"] = str(filtros["id_talhao"]).strip().upper()

    if filtros.get("tipo_colheita"):
        consulta.append("AND LOWER(TIPO_COLHEITA) = :tipo_colheita")
        parametros["tipo_colheita"] = str(filtros["tipo_colheita"]).strip().lower()

    if filtros.get("status_perda"):
        consulta.append("AND STATUS_PERDA = :status_perda")
        parametros["status_perda"] = str(filtros["status_perda"]).strip()

    consulta.append("ORDER BY DATA_COLHEITA DESC, ID_COLHEITA DESC")
    conexao = obter_conexao()
    cursor = conexao.cursor()

    try:
        cursor.execute("\n".join(consulta), parametros)
        return [_mapear_linha_para_colheita(linha) for linha in cursor.fetchall()]
    except Exception as exc:
        raise BancoIndisponivelError(f"Erro ao listar colheitas no Oracle: {exc}") from exc
    finally:
        cursor.close()
        conexao.close()


def inserir_colheita_oracle(colheita: dict) -> int:
    parametros = _parametros_colheita(colheita)
    conexao = obter_conexao()
    cursor = conexao.cursor()

    try:
        id_retorno = cursor.var(int)
        cursor.execute(
            """
            INSERT INTO TB_COLHEITA (
                ID_TALHAO,
                AREA_HA,
                PRODUCAO_ESTIMADA,
                PRODUCAO_REALIZADA,
                TIPO_COLHEITA,
                DATA_COLHEITA,
                PERCENTUAL_PERDA,
                STATUS_PERDA
            ) VALUES (
                :id_talhao,
                :area_ha,
                :producao_estimada,
                :producao_realizada,
                :tipo_colheita,
                TO_DATE(:data_colheita, 'DD/MM/YYYY'),
                :percentual_perda,
                :status_perda
            )
            RETURNING ID_COLHEITA INTO :id_colheita
            """,
            {**parametros, "id_colheita": id_retorno},
        )
        conexao.commit()

        novo_id = id_retorno.getvalue()
        if isinstance(novo_id, list):
            novo_id = novo_id[0]
        return int(novo_id)
    except Exception as exc:
        raise BancoIndisponivelError(f"Erro ao inserir colheita no Oracle: {exc}") from exc
    finally:
        cursor.close()
        conexao.close()


def atualizar_colheita_oracle(id_colheita: int, colheita: dict) -> None:
    parametros = _parametros_colheita(colheita)
    parametros["id_colheita"] = int(id_colheita)
    conexao = obter_conexao()
    cursor = conexao.cursor()

    try:
        cursor.execute(
            """
            UPDATE TB_COLHEITA
               SET ID_TALHAO = :id_talhao,
                   AREA_HA = :area_ha,
                   PRODUCAO_ESTIMADA = :producao_estimada,
                   PRODUCAO_REALIZADA = :producao_realizada,
                   TIPO_COLHEITA = :tipo_colheita,
                   DATA_COLHEITA = TO_DATE(:data_colheita, 'DD/MM/YYYY'),
                   PERCENTUAL_PERDA = :percentual_perda,
                   STATUS_PERDA = :status_perda
             WHERE ID_COLHEITA = :id_colheita
            """,
            parametros,
        )

        if cursor.rowcount == 0:
            raise BancoIndisponivelError(
                f"Nenhuma colheita foi encontrada com ID_COLHEITA={id_colheita}."
            )

        conexao.commit()
    except BancoIndisponivelError:
        raise
    except Exception as exc:
        raise BancoIndisponivelError(f"Erro ao atualizar colheita no Oracle: {exc}") from exc
    finally:
        cursor.close()
        conexao.close()


def excluir_colheita_oracle(id_colheita: int) -> None:
    conexao = obter_conexao()
    cursor = conexao.cursor()

    try:
        cursor.execute(
            "DELETE FROM TB_COLHEITA WHERE ID_COLHEITA = :id_colheita",
            {"id_colheita": int(id_colheita)},
        )

        if cursor.rowcount == 0:
            raise BancoIndisponivelError(
                f"Nenhuma colheita foi encontrada com ID_COLHEITA={id_colheita}."
            )

        conexao.commit()
    except BancoIndisponivelError:
        raise
    except Exception as exc:
        raise BancoIndisponivelError(f"Erro ao excluir colheita no Oracle: {exc}") from exc
    finally:
        cursor.close()
        conexao.close()
