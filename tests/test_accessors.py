import pytest
import polaroids  # Registers dataframe and lazyframe namespaces
import polars as pl


def test_dataframe_expression_accessor():
    df = pl.DataFrame({'col_a': [1, 2], 'col_b': [3, 4]})
    res = df.select(df.x.col_a + df.x.col_b)
    assert res.to_dict(as_series=False) == {'col_a': [4, 6]}
    assert dir(df.x) == ['col_a', 'col_b']


def test_lazyframe_expression_accessor():
    ldf = pl.DataFrame({'x': [10, 20], 'y': [30, 40]}).lazy()
    res = ldf.select(ldf.x.x * ldf.x.y).collect()
    assert res.to_dict(as_series=False) == {'x': [300, 800]}
    assert dir(ldf.x) == ['x', 'y']


def test_dataframe_name_accessor():
    df = pl.DataFrame({'first_name': ['Alice'], 'last_name': ['Smith']})
    assert df.n.first_name == 'first_name'
    assert df.n.last_name == 'last_name'
    assert dir(df.n) == ['first_name', 'last_name']


def test_lazyframe_name_accessor():
    ldf = pl.DataFrame({'cat': ['A'], 'val': [1]}).lazy()
    assert ldf.n.cat == 'cat'
    assert ldf.n.val == 'val'
    assert dir(ldf.n) == ['cat', 'val']


def test_dataframe_series_accessor():
    df = pl.DataFrame({'col_a': [1, 2], 'col_b': [3, 4]})
    s_a = df.s.col_a
    s_b = df.s.col_b
    assert isinstance(s_a, pl.Series)
    assert isinstance(s_b, pl.Series)
    assert s_a.to_list() == [1, 2]
    assert s_b.to_list() == [3, 4]
    assert dir(df.s) == ['col_a', 'col_b']


def test_lazyframe_has_no_series_accessor():
    ldf = pl.DataFrame({'col_a': [1]}).lazy()
    assert not hasattr(ldf, 's')


def test_missing_column_attribute_errors():
    df = pl.DataFrame({'col_a': [1]})
    with pytest.raises(AttributeError):
        _ = df.x.nonexistent
    with pytest.raises(AttributeError):
        _ = df.n.nonexistent
    with pytest.raises(AttributeError):
        _ = df.s.nonexistent

    ldf = df.lazy()
    with pytest.raises(AttributeError):
        _ = ldf.x.nonexistent
    with pytest.raises(AttributeError):
        _ = ldf.n.nonexistent


def test_hasattr_behavior():
    df = pl.DataFrame({'col_a': [1]})
    assert hasattr(df.x, 'col_a')
    assert not hasattr(df.x, 'missing')
    assert not hasattr(df.x, '__deepcopy__')

    assert hasattr(df.n, 'col_a')
    assert not hasattr(df.n, 'missing')

    assert hasattr(df.s, 'col_a')
    assert not hasattr(df.s, 'missing')

    ldf = df.lazy()
    assert hasattr(ldf.x, 'col_a')
    assert not hasattr(ldf.x, 'missing')
    assert hasattr(ldf.n, 'col_a')
    assert not hasattr(ldf.n, 'missing')
