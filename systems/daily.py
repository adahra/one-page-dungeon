"""Daily challenge: fixed seed + rotating modifier, derived from the date."""
import random
from datetime import date

MODIFIERS = {
    "none": "No modifier. Pure skill.",
    "double_damage": "Double damage: all enemy hits x2!",
    "no_healing": "Ascetic: no HP/MP healing!",
    "no_shops": "Barren: shops are abandoned!",
}


def daily_info(day=None):
    day = day or date.today()
    seed = int(day.strftime("%Y%m%d"))
    rng = random.Random(seed)
    modifier = rng.choice(list(MODIFIERS))
    return {"date": day.isoformat(), "seed": seed, "modifier": modifier}
