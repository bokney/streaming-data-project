
import pytest


def test_simple_maths():
    assert 1 + 2 == 3


def test_wrong_maths():
    with pytest.raises(AssertionError):
        assert 2 + 2 == 5, 'Maths is wrong'
