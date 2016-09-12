
import io
import jsonlines

import pytest


SAMPLE_BYTES = b'{"a": 1}\n{"b": 2}\n'


def test_reader():
    fp = io.BytesIO(SAMPLE_BYTES)
    with jsonlines.Reader(fp) as reader:
        it = iter(reader)
        assert next(it) == {'a': 1}
        assert next(it) == {'b': 2}
        with pytest.raises(StopIteration):
            next(it)
        with pytest.raises(EOFError):
            reader.read()


def test_writer():
    fp = io.BytesIO()
    with jsonlines.Writer(fp) as writer:
        writer.write({'a': 1})
        writer.write({'b': 2})
    assert fp.getvalue() == SAMPLE_BYTES


def test_invalid_lines():
    data = u'[1, 2'
    with jsonlines.Reader(io.StringIO(data)) as reader:
        with pytest.raises(jsonlines.InvalidLineError) as excinfo:
            reader.read()
        exc = excinfo.value
        assert str(exc).startswith("invalid json")
        assert exc.value == data


def test_typed_reads():
    with jsonlines.Reader(io.StringIO(u'12\n"foo"')) as reader:
        assert reader.read_int() == 12
        with pytest.raises(jsonlines.InvalidLineError) as excinfo:
            reader.read_int()
        exc = excinfo.value
        assert "does not match requested type" in str(exc)
        assert exc.value == "foo"


def test_typed_iteration():
    fp = io.StringIO(u'1\n2\n')
    with jsonlines.Reader(fp) as reader:
        actual = list(reader.iter(type=int))
        assert actual == [1, 2]

    fp = io.StringIO(u'1\n2\n')
    with jsonlines.Reader(fp) as reader:
        it = reader.iter(type=str)
        with pytest.raises(jsonlines.InvalidLineError):
            next(it)


# TODO: jsonlines.open() in a tmpdir
# TODO: text context manager


def test_invalid_mode():
    with pytest.raises(ValueError) as excinfo:
        jsonlines.open('foo', mode='foo')
    assert 'mode' in str(excinfo.value)
