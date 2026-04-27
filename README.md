# hse_smadimo_gp3

## Запуск

```bash
python agent.py
```

## Стили промптинга

В проект добавлены переключаемые продвинутые стили промптинга для LLM-инструментов.
Переключение через `.env`:

```bash
PROMPT_STYLE=default
```

Доступные значения `PROMPT_STYLE`:
- `default` — базовый стиль
- `role_based` — ролевой стиль (Senior ML Engineer + Data Quality Auditor)
- `react` — ReAct (plan -> act -> check)
- `contrastive` — контрастный стиль (избегание слабых решений)
- `multi_agent` — имитация ролей Planner -> Executor -> Critic
