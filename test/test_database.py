"""Functional pytests for database module. """

#  Copyright© 2019. Stephen Rigden.
#  Last modified 12/17/19, 9:11 AM by stephen.
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
from dataclasses import dataclass
from typing import Dict

import pytest
import sqlalchemy.orm.exc

import database
import exception


class DatabaseTestException(Exception):
    """Base class for exceptions in this module."""
    pass


@pytest.fixture()
def connection():
    """Database access ."""
    database.connect_to_database(filename=':memory:')


@pytest.fixture()
def session():
    """Provide a session scope."""
    # noinspection PyProtectedMember
    with database._session_scope() as session:
        yield session


@pytest.fixture(scope='module')
def hamlet() -> Dict:
    """Provide test data for 'Hamlet'."""
    return dict(title='Hamlet', director='Branagh', minutes=242, year=1996)


@pytest.fixture(scope='module')
def revanche() -> Dict:
    """Provide test data for 'Hamlet'."""
    return dict(title='Revanche', director='Speilmann', minutes=122, year=2008, notes='Oscar nominated')


@pytest.fixture(scope='module')
def solaris() -> Dict:
    """Provide test data for 'Solaris'."""
    return dict(title='Solaris', director='Tarkovsky', minutes=169, year=1972)


@pytest.fixture(scope='module')
def dreams() -> Dict:
    """Provide test data for "Akira Kurosawa's Dreams"."""
    return dict(title="Akira Kurosawa's Dreams", director='Kurosawa', minutes=119, year=1972)


@pytest.fixture(scope='class')
def loaded_database(hamlet, solaris, dreams, revanche):
    """Provide a loaded database."""
    database.connect_to_database(filename=':memory:')
    # noinspection PyProtectedMember
    movies = [database.Movie(**movie) for movie in (hamlet, solaris, dreams, revanche)]
    # noinspection PyProtectedMember
    with database._session_scope() as session:
        session.add_all(movies)
    database.add_tag_and_links('blue', [database.MovieKeyDict(title='Hamlet', year=1996)])
    database.add_tag_and_links('yellow', [database.MovieKeyDict(title='Revanche', year=2008)])
    database.add_tag_and_links('green', [database.MovieKeyDict(title='Revanche', year=2008)])
    database.add_tag_and_links('green', [database.MovieKeyDict(title='Solaris', year=1972)])


def test_init_database_access_with_new_database(connection):
    """Create a new database and test that date_created is today."""
    with database._session_scope() as session:
        today = (session.query(database.MoviesMetaData.value)
                 .filter(database.MoviesMetaData.name == 'date_created')
                 .one())
    assert today.value[0:10] == str(database.datetime.datetime.today())[0:10]


def test_init_database_access_with_existing_database(tmpdir):
    """Attach to an existing database and check tha date_last_accessed is today."""
    path = tmpdir.mkdir('tmpdir').join(database.database_fn)
    database.connect_to_database(filename=path)

    # Reattach to the same database
    database.connect_to_database(filename=path)

    with database._session_scope() as session:
        current = (session.query(database.MoviesMetaData.value)
                   .filter(database.MoviesMetaData.name == 'date_last_accessed')
                   .one())
        previous = (session.query(database.MoviesMetaData.value)
                    .filter(database.MoviesMetaData.name == 'date_created')
                    .one())
    assert current != previous


def test_add_movie(connection, session, hamlet):
    expected = tuple(hamlet.values())
    database.add_movie(hamlet)
    result = (session.query(database.Movie.title,
                            database.Movie.director,
                            database.Movie.minutes,
                            database.Movie.year, )
              .one())
    assert result == expected


def test_add_movie_with_empty_title_string(connection, session, monkeypatch):
    expected = 'Null values (empty strings) in row.'
    calls = []
    monkeypatch.setattr(database.logging, 'error', lambda msg: calls.append(msg))

    bad_row = dict(title='Hamlet', director='Branagh', minutes=242, year='')
    with pytest.raises(ValueError) as exc:
        database.add_movie(bad_row)
    assert str(exc.value) == expected
    assert calls[0] == expected


def test_add_movie_with_non_numeric_values(connection, session, monkeypatch):
    bad_int = 'forty two'
    expected = f"invalid literal for int() with base 10: '{bad_int}'"
    logging_msg = (f'{expected}\nA non-integer value has been supplied for either the year '
                   f'or the minute column.')
    calls = []
    monkeypatch.setattr(database.logging, 'error', lambda msg: calls.append(msg))

    bad_row = dict(title='Hamlet', director='Branagh', minutes=bad_int, year='1942')
    with pytest.raises(ValueError) as exc:
        database.add_movie(bad_row)
    assert str(exc.value) == expected
    assert calls[0] == logging_msg


def test_add_movie_with_integrity_error(connection, session, hamlet, monkeypatch):
    calls = []
    monkeypatch.setattr(database.logging, 'error', lambda msg: calls.append(msg))
    
    with pytest.raises(exception.MovieDBConstraintFailure):
        database.add_movie(hamlet)
        database.add_movie(hamlet)
    assert calls == ['UNIQUE constraint failed: movies.title, movies.year']


def test_add_movie_with_notes(connection, session, revanche):
    expected = tuple(revanche.values())
    database.add_movie(revanche)
    result = (session.query(database.Movie.title,
                            database.Movie.director,
                            database.Movie.minutes,
                            database.Movie.year,
                            database.Movie.notes, )
              .one())
    assert result == expected


@pytest.mark.usefixtures('loaded_database', 'monkeypatch')
class TestFindMovie:
    def test_search_movie_year(self):
        test_year = 1996
        for movie in database.find_movies(dict(year=test_year)):
            assert movie['year'] == test_year

    def test_search_movie_id(self):
        test_title = 'Hamlet'
        test_id = 1
        for movie in database.find_movies(database.FindMovieDict(id=test_id)):
            assert movie['title'] == test_title

    def test_search_movie_title(self):
        expected = 'Hamlet'
        for movie in database.find_movies(dict(title='Ham')):
            assert movie['title'] == expected

    def test_search_movie_director(self):
        expected = 'Tarkovsky'
        for movie in database.find_movies(dict(director='Tark')):
            assert movie['director'] == expected

    def test_search_movie_notes(self):
        expected = 'Revanche'
        for movie in database.find_movies(dict(notes='Oscar')):
            assert movie['title'] == expected

    def test_search_movie_with_range_of_minutes(self):
        expected = {122}
        minutes = {movie['minutes'] for movie in database.find_movies(dict(minutes=[130, 120]))}
        assert minutes == expected

    def test_search_movie_with_range_of_minutes_2(self):
        expected = {119, 122, 169}
        minutes = {movie['minutes'] for movie in database.find_movies(dict(minutes=[170, 100]))}
        assert minutes == expected

    def test_search_movie_with_minute(self):
        expected = {169}
        minutes = {movie['minutes'] for movie in database.find_movies(dict(minutes=169))}
        assert minutes == expected

    def test_search_movie_tag(self):
        expected = {'Revanche', 'Solaris'}
        titles = {movie['title'] for movie in database.find_movies(dict(tags='green'))}
        assert titles == expected

    def test_search_movie_all_tags(self):
        expected = {'Hamlet', 'Revanche'}
        titles = {movie['title'] for movie in database.find_movies(dict(tags=['blue', 'yellow']))}
        assert titles == expected

    def test_value_error_is_raised(self, monkeypatch):
        invalid_keys = {'months', }
        expected = f"Invalid attribute '{invalid_keys}'."
        calls = []
        monkeypatch.setattr(database.logging, 'error', lambda msg: calls.append(msg))
    
        with pytest.raises(ValueError) as exc:
            for _ in database.find_movies(dict(months=[169])):
                pass
        assert exc.type is ValueError
        assert exc.value.args == (expected,)
        assert calls[0] == expected


@pytest.mark.usefixtures('loaded_database')
class TestEditMovie:
    def test_edit_movie(self):
        new_note = 'Science Fiction'
        database.edit_movie(database.MovieKeyDict(title='Solaris', year=1972), dict(notes=new_note))
        notes = {movie['notes'] for movie in database.find_movies(dict(title='Solaris'))}
        assert notes == {new_note, }


@pytest.mark.usefixtures('loaded_database')
class TestDeleteMovie:
    
    def test_delete_movie(self):
        expected = set()
        database.del_movie(database.MovieKeyDict(title='Solaris', year=1972))
        titles = {movie['title'] for movie in database.find_movies(dict(title='Solaris'))}
        assert titles == expected


@pytest.mark.usefixtures('loaded_database')
class TestAllTags:
    
    def test_all_tags(self):
        expected = {'blue', 'yellow', 'green'}
        tags = database.all_tags()
        assert set(tags) == expected


@pytest.mark.usefixtures('loaded_database')
class TestTagOperations:
    
    def test_add_new_tag(self, session):
        tag = 'Movie night candidate'
        database.add_tag_and_links(tag)
        
        count = (session.query(database.Tag)
                 .filter(database.Tag.tag == 'Movie night candidate')
                 .count())
        assert count == 1

    def test_add_existing_tag_ignored(self, session):
        tag = 'Movie night candidate'
        database.add_tag_and_links(tag)
        database.add_tag_and_links(tag)

        count = (session.query(database.Tag)
                 .filter(database.Tag.tag == 'Movie night candidate')
                 .count())
        assert count == 1

    def test_add_links_to_movies(self, session):
        expected = {'Solaris', "Akira Kurosawa's Dreams"}
        test_tag = 'Foreign'
        movies = [database.MovieKeyDict(title='Solaris', year=1972),
                  database.MovieKeyDict(title="Akira Kurosawa's Dreams", year=1972)]
        database.add_tag_and_links(test_tag, movies)
    
        movies = (session.query(database.Movie.title)
                  .filter(database.Movie.tags.any(tag=test_tag)))
        result = {movie.title for movie in movies}
        assert result == expected

    def test_edit_tag(self, session):
        old_tag = 'old test tag'
        movies = [database.MovieKeyDict(title='Solaris', year=1972)]
        database.add_tag_and_links(old_tag, movies)
        old_tag_id, tag = (session.query(database.Tag.id, database.Tag.tag)
                           .filter(database.Tag.tag == 'old test tag')
                           .one())

        new_tag = 'new test tag'
        database.edit_tag(old_tag, new_tag)
        new_tag_id, tag = (session.query(database.Tag.id, database.Tag.tag)
                           .filter(database.Tag.tag == 'new test tag')
                           .one())

        assert old_tag_id == new_tag_id

    def test_del_tag(self, session):
        # Add a tag and links
        test_tag = 'Going soon'
        movies = [database.MovieKeyDict(title='Solaris', year=1972),
                  database.MovieKeyDict(title='Hamlet', year=1996)]
        database.add_tag_and_links(test_tag, movies)
    
        # Delete the tag
        database.del_tag(test_tag)
    
        # Is the tag still there?
        with pytest.raises(sqlalchemy.orm.exc.NoResultFound):
            session.query(database.Tag).filter(database.Tag.tag == test_tag).one()
    
        # Do any movies still have the tag?
        assert (session.query(database.Movie)
                .filter(database.Movie.tags.any(tag=test_tag))
                .all()) == []


@dataclass
class InstrumentedSession:
    """A Session dummy with test instrumentation."""
    commit_called = False
    rollback_called = False
    close_called = False
    
    def correct_function(self):
        """A working test function"""
        pass
    
    def incorrect_function(self):
        """A broken test function"""
        raise DatabaseTestException
    
    def commit(self):
        """Register the calling of this function."""
        self.commit_called = True
    
    def rollback(self):
        """Register the calling of this function."""
        self.rollback_called = True
    
    def close(self):
        """Register the calling of this function."""
        self.close_called = True


@dataclass
class InstrumentedLogging:
    """A Logging dummy with test instrumentation."""
    def __init__(self) -> None:
        self.info_calls = []
    
    def info(self, msg):
        """Register the arguments with which this function was called."""
        self.info_calls.append(msg)


def test_commit_called(monkeypatch):
    monkeypatch.setattr(database, 'Session', InstrumentedSession)
    with database._session_scope() as session:
        session.correct_function()
    assert session.commit_called
    assert session.close_called


def test_rollback_called(monkeypatch):
    monkeypatch.setattr(database, 'Session', InstrumentedSession)
    monkeypatch.setattr(database, 'logging', InstrumentedLogging())
    with pytest.raises(DatabaseTestException):
        with database._session_scope() as session:
            session.incorrect_function()
    assert session.rollback_called
    assert session.close_called


def test_logging_called(monkeypatch):
    monkeypatch.setattr(database, 'Session', InstrumentedSession)
    log = InstrumentedLogging()
    monkeypatch.setattr(database, 'logging', log)
    with pytest.raises(DatabaseTestException):
        with database._session_scope() as session:
            session.incorrect_function()
    assert log.info_calls[0] == ("An incomplete database session has been rolled back "
                                 "because of exception:\nDatabaseTestException")
