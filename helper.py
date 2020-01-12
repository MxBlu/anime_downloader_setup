from collections import OrderedDict

def input_or(prompt, default):
    entry = input("{:s} [{:s}]: ".format(prompt, str(default)))
    if entry.strip() == "":
        return default
    else:
        return entry

def exists(func, iterable):
    return any(map(func, iterable))