from semantic_version import Version

def closest_version(haystack, needle, key):
    """
    Find the closest value to a given needle in haystack
    """
    if haystack and len(haystack) == 0: return None
    closest_v = None
    closest_computed = None
    target = Version(key(needle))
    for item in haystack:
        temp = Version(key(item))
        if closest_computed is None or (temp < needle and temp > closest_v):
            closest_computed = temp
            closest_v = item
    return closest_v