# SUAP Escola (Django)

Sistema escolar com frontend suave e backend funcional (CRUD real).

## Funcionalidades

- Painel com métricas e gráfico por turma
- Gestão de alunos (criar, editar, excluir, filtrar)
- Gestão de turmas e disciplinas vinculadas
- Matrículas com persistência em banco
- Lançamento e atualização de notas
- Registro e atualização de frequência
- Timeline e avisos acadêmicos

## Rotas principais

- `/` painel
- `/alunos/`
- `/turmas/`
- `/matriculas/`
- `/notas/`
- `/frequencia/`
- `/agenda/`

## Como executar

```bash
python -m venv .venv
.venv\Scripts\activate
pip install django
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

## Corrigir conflito de banco antigo

Se o banco antigo conflitar com o novo modelo, rode:

```bash
python manage.py reset_school_db --yes
```

Esse comando:
- remove `db.sqlite3`
- remove migrações antigas do app `core` (mantendo `__init__.py`)
- cria migrações novas
- aplica `migrate`

Depois inicie normalmente:

```bash
python manage.py runserver
```
