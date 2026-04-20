def normalize_score(value):
    try:
        score = float(value)
    except:
        return 0

    if score <= 1:
        return round(score * 100)

    if score <= 10:
        return round(score * 10)

    if score <= 100:
        return round(score)

    return 0