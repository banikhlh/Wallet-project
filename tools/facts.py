# tools/facts.py
import random
from typing import Optional
from crud.transaction import TransactionCRUD

PRICES = {
    "gold_per_gram": 6500,
    "coffee": 200,
    "iphone": 120000,
    "musk_wealth": 1_700_000_000_000,
    "pizza": 500,
    "netflix_monthly": 400,
    "rent_monthly": 40000,
    "flight_msk_sochi": 7000,
    "macbook_pro": 200000,
    "tesla_model_3": 3_500_000,
}

FACT_TEMPLATES = [
    {
        "template": "На общую сумму операций можно купить {count:.1f} г чистого золота.",
        "price_key": "gold_per_gram",
        "min_value": 1
    },
    {
        "template": "Это эквивалентно {count:.0f} чашкам кофе.",
        "price_key": "coffee",
        "min_value": 1
    },
    {
        "template": "Хватило бы на {count:.0f} новых iPhone.",
        "price_key": "iphone",
        "min_value": 0.5
    },
    {
        "template": "Вы могли бы оплатить {count:.0f} месяцев Netflix.",
        "price_key": "netflix_monthly",
        "min_value": 1
    },
    {
        "template": "Это как {count:.0f} пицц.",
        "price_key": "pizza",
        "min_value": 1
    },
    {
        "template": "Ваш финансовый оборот составляет {percent:.8f}% от состояния Илона Маска.",
        "compare_key": "musk_wealth",
        "min_percent": 0.000001
    },
    {
        "template": "Можно снять квартиру на {count:.1f} месяца(ев).",
        "price_key": "rent_monthly",
        "min_value": 0.5
    },
    {
        "template": "Это как {count:.0f} перелётов Москва–Сочи туда-обратно.",
        "price_key": "flight_msk_sochi",
        "min_value": 1
    },
    {
        "template": "Хватило бы на {count:.1f} MacBook Pro.",
        "price_key": "macbook_pro",
        "min_value": 0.3
    },
    {
        "template": "Это {percent:.6f}% от стоимости Tesla Model 3.",
        "compare_key": "tesla_model_3",
        "min_percent": 0.001
    },
]

async def generate_fact(db, user_id: int) -> Optional[str]:
    crud = TransactionCRUD(db)
    volume = await crud.get_total_volume(user_id, "month")
    if volume == 0:
        return None

    templates = random.sample(FACT_TEMPLATES, len(FACT_TEMPLATES))

    for fact in templates:
        if "compare_key" in fact:
            compare_value = PRICES[fact["compare_key"]]
            percent = (volume / compare_value) * 100
            min_percent = fact.get("min_percent", 0.0001)
            if percent >= min_percent:
                return fact["template"].format(percent=percent)
        else:
            price = PRICES[fact["price_key"]]
            if fact.get("unit_kg"):
                count = volume / price
            else:
                count = volume / price
            if count >= fact.get("min_value", 1):
                return fact["template"].format(count=count)

    return None