from semantic_version import Version
import re

bad_patch_re = re.compile(r"(\d)([A-Za-z])$") # 0.1.2b instead of 0.1.2-b >.<

def semver(version):
    try:
        _version = version + ".1" if len(version.split(".")) == 2 else version #fix 0.1 throwing exception
        _version = bad_patch_re.sub(r"\1-\2", _version)
        return Version(_version)
    except ValueError:
        return version #non semver e.g. soundmanger2

def closest_version(haystack, needle, key):
    """
    Find the closest value to a given needle in haystack
    """
    if haystack and len(haystack) == 0: return None
    closest_v = closest_computed = None
    target = semver(key(needle))
    for item in haystack:
        temp = semver(key(item))
        if closest_computed is None or \
                (temp < target and temp > closest_computed) or \
                (temp > target and temp < closest_computed):
            closest_computed = temp
            closest_v = item
    return closest_v if closest_computed != target else None