import re

EMAIL = re.compile(r"([A-Za-z0-9._%+-])[A-Za-z0-9._%+-]*(@[A-Za-z0-9.-]+)")
PHONE = re.compile(r"\+?\d{8,15}")


def mask(value: str) -> str:
    """For logs: keep enough to recognise a contact, never the whole thing."""
    value = EMAIL.sub(lambda m: f"{m.group(1)}***{m.group(2)}", value)
    return PHONE.sub(lambda m: "*" * (len(m.group(0)) - 2) + m.group(0)[-2:], value)
