import polaroids  # Registers dataframe and lazyframe namespaces ('c' and 's')
import polars as pl


def test_dataframe_column_accessor():
    df = pl.DataFrame({'col_a': [1, 2], 'col_b': [3, 4]})
    res = df.select(df.c.col_a + df.c.col_b)
    assert res.to_dict(as_series=False) == {'col_a': [4, 6]}
    assert dir(df.c) == ['col_a', 'col_b']


def test_lazyframe_column_accessor():
    ldf = pl.DataFrame({'x': [10, 20], 'y': [30, 40]}).lazy()
    res = ldf.select(ldf.c.x * ldf.c.y).collect()
    assert res.to_dict(as_series=False) == {'x': [300, 800]}
    assert dir(ldf.c) == ['x', 'y']


def test_dataframe_string_accessor():
    df = pl.DataFrame({'first_name': ['Alice'], 'last_name': ['Smith']})
    assert df.s.first_name == 'first_name'
    assert df.s.last_name == 'last_name'
    assert dir(df.s) == ['first_name', 'last_name']


def test_lazyframe_string_accessor():
    ldf = pl.DataFrame({'cat': ['A'], 'val': [1]}).lazy()
    assert ldf.s.cat == 'cat'
    assert ldf.s.val == 'val'
    assert dir(ldf.s) == ['cat', 'val']
