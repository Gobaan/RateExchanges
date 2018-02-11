import json

import utilities


class A(object):
    def __init__(self, value):
        self.value = value
        self.children = []

    def add_child(self, child):
        self.children += [child]


class B(object):
    def __init__(self):
        self.comments = []

    def populate(self, length):
        self.comments = list(range(3)) * length


def test_copy_nested_object():
    first = A("gobi")
    b = B()
    b.populate(3)
    first.add_child(b)

    first_separate = A("gobi")
    b = B()
    b.populate(3)
    first_separate.add_child(b)

    second = 10
    third = []
    fourth = B()
    fifth = None
    sixth = A("skan")
    sixth.add_child(sixth)
    seventh = A("skan")
    seventh.add_child(seventh)

    assert utilities.is_eq(first, first)
    assert utilities.is_eq(second, second)
    assert utilities.is_eq(third, third)
    assert utilities.is_eq(fourth, fourth)
    assert utilities.is_eq(fifth, fifth)
    assert utilities.is_eq(first, first_separate)
    assert utilities.is_eq(seventh, seventh)
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


def test_encoding_object(mocker):
    mocker.patch("uuid.UUID", new=lambda: 1)
    before = A("gobi")
    encoder = utilities.get_encoder(A)
    to_json = json.dumps(before, cls=encoder)
    assert to_json == '{"__name__": "__a__", "value": "gobi", "children": []}'

    after = json.loads(to_json, object_hook=encoder.decode)
    assert after.value == "gobi"
    assert after.children == []
    assert utilities.is_eq(before, after)


def test_encoding_nested_object(mocker):
    mocker.patch("uuid.UUID", new=lambda: 1)
    before = A("gobi")
    b = B()
    b.populate(3)
    before.add_child(b)

    encoder = utilities.get_encoder(A, B)
    to_json = json.dumps(before, cls=encoder)
    assert to_json == '{"__name__": "__a__", "value": "gobi", "children": ' + \
           '[{"__name__": "__b__", "comments": [0, 1, 2, 0, 1, 2, 0, 1, 2]}]}'

    after = json.loads(to_json, object_hook=encoder.decode)
    assert utilities.is_eq(before, after)
