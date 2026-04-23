# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href= "https://www.fiap.com.br/"><img src="assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Administração Paulista" border="0" width=40% height=40%></a>
</p>

<br>

# Sistema de Gestão de Perdas na Colheita de Cana-de-Açúcar

## Nome do grupo

## 👨‍🎓 Integrantes:
- <a href="https://www.linkedin.com/company/inova-fusca">Nome do integrante 1</a>
- <a href="https://www.linkedin.com/company/inova-fusca">Nome do integrante 2</a>
- <a href="https://www.linkedin.com/company/inova-fusca">Nome do integrante 3</a>
- <a href="https://www.linkedin.com/company/inova-fusca">Nome do integrante 4</a>
- <a href="https://www.linkedin.com/company/inova-fusca">Nome do integrante 5</a>

## 👩‍🏫 Professores:

### Tutor(a)
- <a href="https://www.linkedin.com/company/inova-fusca">Nome do Tutor</a>

### Coordenador(a)
- <a href="https://www.linkedin.com/company/inova-fusca">Nome do Coordenador</a>

## 📜 Descrição

CLI em Python para registrar, monitorar e analisar perdas na colheita de cana-de-açúcar por talhão, com exportação/importação em JSON, log de alertas críticos em `.txt` e CRUD completo no Oracle via `oracledb`.

O sistema foi projetado para apoiar o controle de perdas em operações de colheita manual e mecanizada. Cada colheita registra produção estimada, produção realizada, percentual de perda e classificação operacional para apoiar a tomada de decisão do produtor.

**Funcionalidades principais:**
- Registrar colheita com validação completa de entrada
- Listar colheitas com filtros por talhão, tipo e status
- Calcular e exibir perdas de uma colheita específica
- Atualizar e excluir colheitas
- Gerar relatório agrupado por mês ou por tipo de colheita
- Exportar e importar histórico em JSON
- Registrar alertas críticos com data e hora em `dados/alertas.txt`
- Persistir dados no Oracle usando a tabela `TB_COLHEITA`

**Regras de cálculo:**

```text
percentual_perda = ((producao_estimada - producao_realizada) / producao_estimada) * 100
```

Classificação por tipo de colheita:

| Tipo     | Aceitável | Atenção   | Crítico     |
|----------|-----------|-----------|-------------|
| Manual   | até 5%    | até 10%   | acima de 10% |
| Mecânica | até 10%   | até 15%   | acima de 15% |

## 📁 Estrutura de pastas

Dentre os arquivos e pastas presentes na raiz do projeto, definem-se:

- <b>assets</b>: aqui estão os arquivos relacionados a elementos não-estruturados deste repositório, como imagens.
- <b>dados</b>: pasta gerada em tempo de execução contendo os arquivos de dados persistidos localmente — `colheitas.json` (histórico de registros) e `alertas.txt` (log de alertas críticos).
- <b>src / projeto_cana</b>: todo o código-fonte do projeto, organizado nos módulos abaixo:
  - `main.py` — ponto de entrada da aplicação e menu interativo
  - `colheita.py` — lógica de negócio, cálculo de perdas e classificação
  - `arquivo.py` — exportação e importação de dados em JSON
  - `banco.py` — integração com Oracle via `oracledb`
- <b>create_table.sql</b>: script SQL para criação da tabela `TB_COLHEITA` no Oracle.
- <b>README.md</b>: arquivo que serve como guia e explicação geral sobre o projeto (o mesmo que você está lendo agora).

```text
projeto_cana/
├── main.py
├── colheita.py
├── arquivo.py
├── banco.py
├── create_table.sql
├── dados/
│   ├── colheitas.json
│   └── alertas.txt
└── README.md
```

## 🔧 Como executar o código

### Pré-requisitos

- Python 3.12+
- Biblioteca `oracledb`
- Acesso a uma instância Oracle Database (opcional — o sistema funciona sem ela)

### Fase 1 — Configuração do ambiente

Instale a dependência necessária:

```bash
pip install oracledb
```

Configure as variáveis de ambiente para conexão com o Oracle:

```bash
export ORACLE_USER=seu_usuario
export ORACLE_PASSWORD=sua_senha
export ORACLE_DSN=host:porta/servico
```

> Se o Oracle estiver indisponível, o programa continua funcionando com lista em memória, JSON e log de alertas.

### Fase 2 — Criação da tabela no banco de dados

```sql
@create_table.sql
```

### Fase 3 — Execução

A partir da pasta do projeto:

```bash
python main.py
```

Ou a partir da pasta acima:

```bash
python projeto_cana/main.py
```

## 🗃 Histórico de lançamentos

* 0.5.0 - XX/XX/2024
    *
* 0.4.0 - XX/XX/2024
    *
* 0.3.0 - XX/XX/2024
    *
* 0.2.0 - XX/XX/2024
    *
* 0.1.0 - XX/XX/2024
    *

## 📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/agodoi/template">MODELO GIT FIAP</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">Fiap</a> está licenciado sobre <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>
