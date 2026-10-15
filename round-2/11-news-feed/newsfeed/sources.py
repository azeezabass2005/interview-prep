SOURCE_WEIGHTS = {
    "wire-a": 10.0,
    "wire-b": 8.0,
    "partner": 4.0,
    "blog": 1.0,
}


def weight_for(source: str) -> float:
    return SOURCE_WEIGHTS.get(source, 1.0)
