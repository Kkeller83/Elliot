def count_expected_args(f):
    if hasattr(f,'func_code'):
        # python 2
        n = f.func_code.co_argcount - len(f.func_defaults or [])
        if getattr(f, 'im_self', None):
            n -= 1
    elif hasattr(f, '__code__'):
        # python 3
        n = f.__code__.co_argcount - len(f.__defaults__ or [])
        if getattr(f, '__self__', None):
            n -= 1
    else:
        # doh!
        n = 1
    return n

def represent(field, value, record):
    f = field.represent
    if not callable(f):
        return str(value)
    n = count_expected_args(f)
    if n == 1:
        return f(value)
    elif n == 2:
        return f(value, record)
    else:
        raise RuntimeError("field representation must take 1 or 2 args")
