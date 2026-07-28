import polars as pl
import pytest


@pytest.fixture
def sample_df() -> pl.DataFrame:
    return pl.DataFrame(
        {
            'col_a': [1, 2, 3],
            'col b': [4, 5, 6],
            '123_num': [7, 8, 9],
            '': [10, 11, 12],
        }
    )


@pytest.fixture
def sample_lazy_df(sample_df: pl.DataFrame) -> pl.LazyFrame:
    return sample_df.lazy()
