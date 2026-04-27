"""
tools/prompt_styles.py
Шаблоны продвинутых стилей промптинга для LLM-инструментов.
"""

from __future__ import annotations

import os


def _style() -> str:
    return os.getenv("PROMPT_STYLE", "default").strip().lower()


def _business_context() -> str:
    return (
        "Бизнес-контекст:\n"
        "- Задача: предсказать зарплату вакансии по данным HH.ru.\n"
        "- Вход: данные по интересующей вакансии (name, experience, employment, schedule, city, skills и др.).\n"
        "- Выход (target): ожидаемая зарплата в рублях.\n"
        "- Приоритет: реалистичность прогноза, устойчивость к шуму и отсутствие утечек таргета.\n"
        "- Не используй признаки, недоступные на момент предсказания новой вакансии.\n\n"
    )


def _prefix_for_style(style: str) -> str:
    if style == "role_based":
        return (
            f"{_business_context()}"
            "Роль: Principal ML Engineer + Data Quality Auditor + Product Analyst.\n"
            "Требования:\n"
            "1) Любое решение обоснуй через влияние на точность и бизнес-интерпретацию зарплаты.\n"
            "2) Явно учитывай региональный фактор (city) и seniority (experience/name).\n"
            "3) Проверяй, что признаки из skills создаются без утечки и одинаково в train/inference.\n"
            "4) Если данные неоднозначны, выбирай консервативное решение и фиксируй риски.\n\n"
        )

    if style == "react":
        return (
            f"{_business_context()}"
            "Работай в стиле ReAct++:\n"
            "- PLAN: сформулируй гипотезы, какие факторы двигают зарплату.\n"
            "- ACT: реализуй кодом ровно один шаг, минимально необходимый для прогресса.\n"
            "- OBSERVE: зафиксируй результат шага (метрики/статистики).\n"
            "- CHECK: добавь sanity checks (NaN, shape, leakage, диапазоны зарплат).\n"
            "- REVISE: если гипотеза не подтвердилась, сделай безопасную альтернативу.\n"
            "Сгенерируй только Python-код.\n\n"
        )

    if style == "contrastive":
        return (
            f"{_business_context()}"
            "Применяй контрастный подход (Weak vs Strong):\n"
            "- Явно избегай слабых практик: target leakage, хардкод, игнор дисбаланса и выбросов.\n"
            "- Выбирай сильную альтернативу: robust preprocessing, валидация, проверка стабильности.\n"
            "- Для каждого решения показывай trade-off: точность vs интерпретируемость vs риск переобучения.\n"
            "- Если есть выбор, предпочитай вариант с лучшей обобщающей способностью на новых вакансиях.\n\n"
        )

    if style == "multi_agent":
        return (
            f"{_business_context()}"
            "Сымитируй multi-agent цикл Planner -> FeatureEngineer -> Modeler -> Critic:\n"
            "- Planner: формирует стратегию для входа 'вакансия' и выхода 'зарплата'.\n"
            "- FeatureEngineer: строит признаки из name/skills/city/experience, совместимые с inference.\n"
            "- Modeler: обучает и сравнивает модели по MAE/RMSE/R2.\n"
            "- Critic: проверяет утечки, нестабильность и нереалистичные прогнозы.\n"
            "Сделай минимум 2 итерации внутренней критики перед финальным ответом.\n\n"
        )

    if style == "self_consistency":
        return (
            f"{_business_context()}"
            "Применяй self-consistency:\n"
            "- Сформируй 3 независимые гипотезы пайплайна (фичи/модель/препроцессинг).\n"
            "- Оставь только те решения, которые согласуются хотя бы в 2 из 3 гипотез.\n"
            "- Если гипотезы расходятся, выбирай более робастный и интерпретируемый вариант.\n\n"
        )

    if style == "calibrated":
        return (
            f"{_business_context()}"
            "Применяй uncertainty-aware подход:\n"
            "- Помимо point estimate зарплаты, оцени доверительный диапазон (например, по квантилям ошибок).\n"
            "- Для экстремальных вакансий (редкие навыки/редкий город) повышай осторожность прогноза.\n"
            "- Избегай чрезмерно уверенных выводов без статистического основания.\n\n"
        )

    return ""


def compose_prompt(base_prompt: str) -> str:
    """
    Добавляет префикс выбранного стиля к базовому промпту.
    Доступные стили:
      - default
      - role_based
      - react
      - contrastive
      - multi_agent
      - self_consistency
      - calibrated
    """
    style = _style()
    return f"{_prefix_for_style(style)}{base_prompt}"
