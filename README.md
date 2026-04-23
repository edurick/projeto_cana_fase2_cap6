# Sistema de Gestão de Perdas na Colheita de Cana-de-Açúcar

CLI em Python para registrar, monitorar e analisar perdas na colheita de cana-de-açúcar por talhão, com exportação/importação em JSON, log de alertas críticos em `.txt` e CRUD completo no Oracle via `oracledb`.

## Problema

O sistema foi projetado para apoiar o controle de perdas em operações de colheita manual e mecanizada. Cada colheita registra produção estimada, produção realizada, percentual de perda e classificação operacional para apoiar a tomada de decisão do produtor.

## Funcionalidades

- Registrar colheita com validação completa de entrada
- Listar colheitas com filtros por talhão, tipo e status
- Calcular e exibir perdas de uma colheita específica
- Atualizar e excluir colheitas
- Gerar relatório agrupado por mês ou por tipo de colheita
- Exportar e importar histórico em JSON
- Registrar alertas críticos com data e hora em `dados/alertas.txt`
- Persistir dados no Oracle usando a tabela `TB_COLHEITA`

## Estrutura

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

## Requisitos

- Python 3.12+
- Biblioteca `oracledb`
- Variáveis de ambiente para conexão Oracle:

```bash
export ORACLE_USER=seu_usuario
export ORACLE_PASSWORD=sua_senha
export ORACLE_DSN=host:porta/servico
```

Se o Oracle estiver indisponível, o programa continua funcionando com lista em memória, JSON e log de alertas.

## Como executar

1. Crie a tabela no Oracle:

```sql
@create_table.sql
```

2. Execute o sistema:

```bash
python main.py
```

Ou, a partir da pasta acima:

```bash
python projeto_cana/main.py
```

## Regras de cálculo

```text
percentual_perda = ((producao_estimada - producao_realizada) / producao_estimada) * 100
```

Classificação:

- Manual: até 5% = Aceitável, até 10% = Atenção, acima de 10% = Crítico
- Mecânica: até 10% = Aceitável, até 15% = Atenção, acima de 15% = Crítico

## Arquivos de dados

- `dados/colheitas.json`: exemplo com 3 registros válidos
- `dados/alertas.txt`: log dos alertas críticos registrados durante a execução

## Observações

- Os limites de perda ficam em uma estrutura imutável por tipo em `colheita.py`
- Cada colheita é representada por um dicionário
- A sessão mantém as colheitas em uma lista em memória
- Erros de conexão e configuração do Oracle são tratados com mensagens claras no terminal
