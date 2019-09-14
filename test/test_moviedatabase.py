"""Tests for moviedatabase."""

#  Copyright© 2019. Stephen Rigden.
#  Last modified 9/14/19, 10:19 AM by stephen.
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import io
from contextlib import redirect_stdout
from dataclasses import dataclass

import pytest

import moviedatabase

TEST_FN = 'test_filename.csv'


@pytest.mark.usefixtures('monkeypatch')
class TestMain:
    def test_start_up_called(self, monkeypatch):
        calls = []
        monkeypatch.setattr(moviedatabase, 'start_up',
                            lambda *args, **kwargs: calls.append((args, kwargs)))
        monkeypatch.setattr(moviedatabase, 'close_down', lambda: None)
        moviedatabase.main()
        assert len(calls) == 1
    
    def test_close_down_called(self, monkeypatch):
        monkeypatch.setattr(moviedatabase, 'start_up', lambda: None)
        calls = []
        monkeypatch.setattr(moviedatabase, 'close_down',
                            lambda *args, **kwargs: calls.append((args, kwargs)))
        moviedatabase.main()
        assert len(calls) == 1


@pytest.mark.usefixtures('monkeypatch')
class TestStartUp:
    def test_start_logger_called(self, monkeypatch):
        expected_path = 'movies'
        expected_filename = 'moviedatabase'
        calls = []
        monkeypatch.setattr(moviedatabase, 'start_logger',
                            lambda *args, **kwargs: calls.append((args, kwargs)))
        moviedatabase.start_up()
        path_filename, _ = calls[0]
        path, filename = path_filename
        assert path[-6:] == expected_path
        assert filename == expected_filename


@pytest.mark.usefixtures('monkeypatch')
class TestCloseDown:
    def test_start_logger_called(self, monkeypatch):
        calls = []
        monkeypatch.setattr(moviedatabase.logging, 'shutdown',
                            lambda *args, **kwargs: calls.append((args, kwargs)))
        moviedatabase.close_down()
        assert len(calls) == 1


def test_start_logger(monkeypatch):
    log_root = 'log dir'
    log_fn = 'filename'
    expected = dict(format='{asctime} {levelname:8} {lineno:4d} {module:20} {message}',
                    style='{',
                    level='INFO',
                    filename=f"{log_root}/{log_fn}.log",
                    filemode='w')
    calls = []
    monkeypatch.setattr(moviedatabase.logging, 'basicConfig',
                        lambda *args, **kwargs: calls.append((args, kwargs)))
    moviedatabase.start_logger(log_root, log_fn)
    _, format_args = calls[0]
    print('t300', format_args)
    assert format_args == expected


@dataclass
class ArgParser:
    """Test dummy for Argument Parser"""
    verbosity: int = 0
    import_csv: str = None
    database: str = None
    
    def __call__(self):
        return self


@pytest.mark.usefixtures('monkeypatch')
class TestCommand:
    def test_missing_filename_calls_main(self, monkeypatch):
        calls = []
        monkeypatch.setattr(moviedatabase, 'main', lambda *args, **kwargs: calls.append((args, kwargs)))
        monkeypatch.setattr(moviedatabase, 'command_line_args', ArgParser())
        moviedatabase.command()
        assert len(calls) == 1
    
    def test_import_movies_called(self, monkeypatch):
        monkeypatch.setattr(moviedatabase, 'command_line_args', ArgParser(import_csv=TEST_FN))
        monkeypatch.setattr(moviedatabase.database, 'connect_to_database', lambda: None)
        calls = []
        monkeypatch.setattr(moviedatabase.impexp, 'import_movies', lambda db_fn: calls.append(db_fn))
        moviedatabase.command()
        assert calls == [TEST_FN]
    
    def test_default_database_called(self, monkeypatch):
        monkeypatch.setattr(moviedatabase, 'command_line_args', ArgParser(import_csv=TEST_FN))
        calls = []
        monkeypatch.setattr(moviedatabase.database, 'connect_to_database',
                            lambda *args, **kwargs: calls.append((args, kwargs)))
        monkeypatch.setattr(moviedatabase.impexp, 'import_movies', lambda *args: None)
        moviedatabase.command()
        assert calls == [((), {})]
    
    def test_user_defined_database_called(self, monkeypatch):
        test_db = 'user_defined_filename'
        monkeypatch.setattr(moviedatabase, 'command_line_args', ArgParser(import_csv=TEST_FN,
                                                                          database=test_db))
        calls = []
        monkeypatch.setattr(moviedatabase.database, 'connect_to_database',
                            lambda *args, **kwargs: calls.append((args, kwargs)))
        monkeypatch.setattr(moviedatabase.impexp, 'import_movies', lambda *args: None)
        moviedatabase.command()
        assert calls == [((test_db,), {})]
    
    def test_verbosity_called_with_default_database(self, monkeypatch):
        expected_1 = "movies/moviedatabase.py"
        expected_2 = f"Loading movies from {TEST_FN}"
        expected_3 = "Adding movies to the default database."
        
        print_file = io.StringIO()
        with redirect_stdout(print_file):
            monkeypatch.setattr(moviedatabase, 'command_line_args', ArgParser(import_csv=TEST_FN,
                                                                              verbosity=42))
            monkeypatch.setattr(moviedatabase.database, 'connect_to_database', lambda: None)
            monkeypatch.setattr(moviedatabase.impexp, 'import_movies', lambda *args: None)
            moviedatabase.command()
        
        lines = [line for line in print_file.getvalue().split('\n')]
        assert lines[0][-23:] == expected_1
        assert lines[1] == expected_2
        assert lines[2] == expected_3
    
    def test_verbosity_called_with_user_supplied_database(self, monkeypatch):
        test_database = 'user_defined_database'
        expected_1 = "movies/moviedatabase.py"
        expected_2 = f"Loading movies from {TEST_FN}"
        expected_3 = f"Adding movies to database '{test_database}'."
        
        print_file = io.StringIO()
        with redirect_stdout(print_file):
            monkeypatch.setattr(moviedatabase, 'command_line_args',
                                ArgParser(import_csv=TEST_FN, verbosity=42, database=test_database))
            monkeypatch.setattr(moviedatabase.database, 'connect_to_database', lambda *args: None)
            monkeypatch.setattr(moviedatabase.impexp, 'import_movies', lambda *args: None)
            moviedatabase.command()
        
        lines = [line for line in print_file.getvalue().split('\n')]
        assert lines[0][-23:] == expected_1
        assert lines[1] == expected_2
        assert lines[2] == expected_3
