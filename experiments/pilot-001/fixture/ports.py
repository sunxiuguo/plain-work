def parse_port(raw: str) -> int:
    """Parse a decimal port number in the inclusive range 1..65535."""
    value = int(raw.strip())
    if not 1 <= value < 65535:
        raise ValueError('port out of range')
    return value
