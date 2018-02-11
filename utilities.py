import json


def get_encoder(*cls_hooks):
    hooks = {
        "__%s__" % hook.__name__.lower(): hook
        for hook in cls_hooks
    }

    class GenericEncoder(json.JSONEncoder):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def default(self, obj):
            if hasattr(obj, '__dict__'):
                name = type(obj).__name__.lower()
                return {**{"__name__": f"__{name}__"},
                        **{key: self.default(value) for key, value
                           in vars(obj).items()}}
            try:
                return json.JSONEncoder.default(self, obj)
            except TypeError:
                return obj

        @staticmethod
        def decode(dct):
            try:
                base_class = hooks[dct['__name__']]
            except (KeyError, TypeError):
                return dct
            obj = base_class.__new__(base_class)
            for key, value in dct.items():
                if key == '__name__':
                    continue
                setattr(obj, key, GenericEncoder.decode(value))
            return obj

    return GenericEncoder


def is_eq(*objects):
    compared = set()

    def is_eq_dictionary(dct, other):
        if dct.keys() != other.keys():
            return False

        for key in dct:
            if not is_eq_helper(dct[key], other[key]):
                return False

        return True

    def is_eq_iterable(obj, other):
        for left, right in zip(obj, other):
            if not is_eq_helper(left, right):
                return False
        return True

    def is_eq_primitive(obj, other):
        if obj == other:
            return True

        if hasattr(obj, '__dict__') or hasattr(other, '__dict__') or type(obj) != type(other):
            return False

        try:
            return is_eq_dictionary(obj, other)
        except AttributeError:
            pass

        try:
            return is_eq_iterable(obj, other)
        except AttributeError:
            return False

    def is_eq_helper(obj, other):
        if is_eq_primitive(obj, other):
            return True

        if obj.__class__ is not other.__class__:
            return False

        if (obj, other) in compared:
            return True

        compared.update([(obj, other), (other, obj)])
        return is_eq_dictionary(vars(obj), vars(other))

    for first, second in zip(objects, objects[1:]):
        if not is_eq_helper(first, second):
            return False
    return True
