#
# Copyright (c) 2012-2024 Snowflake Computing Inc. All rights reserved.
#

import modin.pandas as pd
import pandas as native_pd
import pytest

import snowflake.snowpark.modin.plugin  # noqa: F401
from tests.integ.modin.sql_counter import SqlCounter, sql_count_checker


@pytest.mark.parametrize(
    "lhs, rhs, expected",
    [
        ([], [], True),  # empty indices
        ([None], [None], True),  # none indices
        ([1, 2, 3], [1, 2, 3], True),
        ([1, 2, None], [1, 2, None], True),  # nulls are considered equal
        ([1, 2, 3], [1.0, 2.0, 3.0], True),  # type is ignored
        ([1, 2, 3], [1, 3, 2], False),  # different order
        ([1, 2, 3], [1, 2, 3, 4], False),  # extra value in right
        ([1, 2, 3, 4], [1, 2, 3], False),  # extra value in left
    ],
)
def test_index_equals(lhs, rhs, expected):
    with SqlCounter(query_count=2, join_count=2):
        native_result = native_pd.Index(lhs).equals(native_pd.Index(rhs))
        assert native_result == expected

        snow_result = pd.Index(lhs).equals(pd.Index(rhs))
        assert snow_result == expected

        mixed_result = pd.Index(lhs).equals(native_pd.Index(rhs))
        assert mixed_result == expected


@sql_count_checker(query_count=1, join_count=1)
def test_index_equals_mismatched_name():
    # equals ignore index names.
    data = [1, 2, 3]
    native_result = native_pd.Index(data, name="X").equals(
        native_pd.Index(data, name="Y")
    )
    assert native_result is True

    snow_result = pd.Index(data, name="X").equals(pd.Index(data, name="Y"))
    assert snow_result is True


@sql_count_checker(query_count=0)
def test_index_equals_other_types():
    index = pd.Index([1, 2])
    series = pd.Series([1, 2])
    assert index.equals(series) is False


@sql_count_checker(query_count=0)
def test_index_columns_self_compare():
    # Bug SNOW-1478684
    df = pd.DataFrame([1])
    assert df.columns.equals(df.columns)
