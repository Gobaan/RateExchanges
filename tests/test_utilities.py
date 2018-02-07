import json

import utilities


class A(object):
    def __init__(self, value):
        self.value = value
        self.bs = []

    def add_b(self, b):
        self.bs += [b]


class B(object):
    def __init__(self):
        self.comments = []

    def populate(self, length):
        self.comments = list(range(3)) * length


def test_copy_nested_object():
    first = A("gobi")
    b = B()
    b.populate(3)
    first.add_b(b)

    first_separate = A("gobi")
    b = B()
    b.populate(3)
    first_separate.add_b(b)

    second = 10
    third = []
    fourth = B()
    fifth = None

    assert utilities.is_eq(first, first)
    assert utilities.is_eq(second, second)
    assert utilities.is_eq(third, third)
    assert utilities.is_eq(fourth, fourth)
    assert utilities.is_eq(fifth, fifth)
    assert utilities.is_eq(first, first_separate)
    assert not utilities.is_eq(first, second)
    assert not utilities.is_eq(fifth, first)
    assert not utilities.is_eq(third, first)
    assert not utilities.is_eq(fourth, first_separate)
    assert not utilities.is_eq(second, third)


def test_encoding_simple():
    before = 10

    encoder = utilities.get_encoder()
    to_json = json.dumps(before, cls=encoder)
    assert to_json == "10"

    after = json.loads(to_json, object_hook=encoder.decode)
    assert after == 10
    assert utilities.is_eq(before, after)


def test_encoding_object():
    before = A("gobi")
    encoder = utilities.get_encoder(A)
    to_json = json.dumps(before, cls=encoder)
    assert to_json == '{"__name__": "__a__", "value": "gobi", "bs": []}'

    after = json.loads(to_json, object_hook=encoder.decode)
    assert after.value == "gobi"
    assert after.bs == []
    assert utilities.is_eq(before, after)


def test_encoding_nested_object():
    before = A("gobi")
    b = B()
    b.populate(3)
    before.add_b(b)

    encoder = utilities.get_encoder(A, B)
    to_json = json.dumps(before, cls=encoder)
    assert to_json == '{"__name__": "__a__", "value": "gobi", "bs": ' + \
           '[{"__name__": "__b__", "comments": [0, 1, 2, 0, 1, 2, 0, 1, 2]}]}'

    after = json.loads(to_json, object_hook=encoder.decode)
    assert utilities.is_eq(before, after)
