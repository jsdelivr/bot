def closest_version(haystack, needle, key):
    """
    Find the closest value to a given needle in a sorted ascending haystack
    """
    if haystack and len(haystack) == 0: return None
    closest_v = None
    closest_computed = None
    for item in haystack:
        temp = key(item)
        if closest_computed is None or needle >= temp:
            closest_computed = temp
            closest_v = item
        else:
            break
    return closest_v