def convert(value, newType):
    try:
        return newType(value)
    except ValueError:
        return None
