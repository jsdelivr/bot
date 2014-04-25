def closest_version(haystack, needle, key):
    """
    Find the closest value to a given needle in a sorted ascending haystack
    """
    if len(haystack) == 0: return None
    if len(haystack) == 1: return haystack[0]
    closest_idx = 0
    closest_computed = None
    for idx, item in enumerate(haystack):
        temp = key(item)
        if closest_computed is None or needle >= temp:
            closest_computed = temp
            closest_idx = idx
        else:
            break
    return haystack[closest_idx]