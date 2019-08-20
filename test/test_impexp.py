"""Unit pytests for import module."""
import pytest

import src.impexp as impexp

GOOD_DATA = """
title, year, minutes, notes,
Hamlet, 1996, 242, ,
Revanche, 2008, 122, 'Oscar nominated,
"""
NO_TITLE = 'year, director, minutes, notes,'
NO_YEAR = 'title, director, minutes, notes,'
BAD_COLUMN = 'garbage,'
BAD_FIELD = """
title, year, director, minutes, notes,
Hamlet, 1996, Branagh, 242, this always will be, garbage,
"""
VIOLATION_DATA = """
title, year
Hamlet, 1996
Hamlet, 1996
"""


@pytest.fixture(scope='session')
def path(tmpdir_factory):
    """Create a temporary directory."""
    path = tmpdir_factory.mktemp('tempdir')
    return path


def test_title_validation(path):
    """Test validation of compulsory field 'title'. """
    expected = f"Required column 'title' is missing from header record."
    no_title_fn = path / 'no_title.csv'
    no_title_fn.write(NO_TITLE)
    with pytest.raises(ValueError) as exception:
        impexp.import_movies(no_title_fn)
    assert exception.type is ValueError
    assert exception.value.args == expected


def test_year_validation(path):
    """Test validation of compulsory field 'title'. """
    expected = f"Required column 'year' is missing from header record."
    no_year_fn = path / 'no_year.csv'
    no_year_fn.write(NO_TITLE)
    with pytest.raises(ValueError) as exception:
        impexp.import_movies(no_year_fn)
    assert exception.type is ValueError
    assert exception.value.args == expected


def test_invalid_field_validation(path):
    """Test validation of invalid field."""
    expected = f"Invalid column name '{BAD_COLUMN.strip(',')}'."
    bad_column_fn = path / 'bad_column.csv'
    bad_column_fn.write(NO_TITLE)
    with pytest.raises(ValueError) as exception:
        impexp.import_movies(bad_column_fn)
    assert exception.type is ValueError
    assert exception.value.args == expected


def test_row_length_validation(path):
    """Test validation of correct number of fields in data row."""
    bad_field_fn = path / 'bad_field.csv'
    bad_field_fn.write(BAD_FIELD)
    reject_fn = path / 'bad_field.reject'
    impexp.import_movies(bad_field_fn)
    assert reject_fn.read() == BAD_FIELD


def test_add_movie_called(path, monkeypatch):
    """Test database.add_movie called."""
    expected = [dict(title='Revanche', year='2008', minutes='122', notes='Oscar nominated'),
                dict(title='Hamlet', year='1996', minutes='242', notes='')]
    calls = []

    def mock_add_movie(*args, **kwargs):
        """Accumulate the arguments of each call in an external list. """
        calls.append((args, kwargs))

    monkeypatch.setattr(impexp.database, 'add_movie', mock_add_movie, raising=True)
    good_data_fn = path / 'good_data.csv'
    good_data_fn.write(GOOD_DATA)

    impexp.import_movies(good_data_fn)
    assert calls == expected


def test_database_integrity_violation(path):
    """Test database integrity violation causes record rejection."""
    violation_data_fn = path / 'violation_data.csv'
    violation_data_fn.write(VIOLATION_DATA)
    reject_fn = path / 'violation_data.reject'
    impexp.import_movies(violation_data_fn)
    assert reject_fn.read() == VIOLATION_DATA