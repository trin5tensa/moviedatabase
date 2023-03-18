"""test_handlers_pbo

This module contains new tests written after Brian Okken's course and book on pytest in Fall 2022.

Test strategies are noted for each class.
"""
#  Copyright (c) 2023. Stephen Rigden.
#  Last modified 3/15/23, 8:13 AM by stephen.
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import handlers
from unittest.mock import MagicMock

import pytest


# noinspection PyMissingOrEmptyDocstring
class TestSelectMovieCallback:
    """ Strategy
    Calls to database and GUI modules are mocked.
    """
    TITLE = 'Mock Title'
    YEAR = 2042
    MOVIE = handlers.config.MovieUpdateDef(title=TITLE, year=YEAR)
    MOVIES = [MOVIE]
    TAGS = ['tag 1', 'tag 2']

    @pytest.fixture()
    def find_movies(self, monkeypatch):
        find_movies = MagicMock(return_value=self.MOVIES)
        monkeypatch.setattr('handlers.database.find_movies', find_movies)
        return find_movies

    @pytest.fixture()
    def movie_gui(self, monkeypatch):
        movie_gui = MagicMock()
        monkeypatch.setattr('handlers.guiwidgets_2.MovieGUI', movie_gui)
        return movie_gui

    @pytest.fixture()
    def all_tags(self, monkeypatch):
        all_tags = MagicMock(return_value=self.TAGS)
        monkeypatch.setattr('handlers.database.all_tags', all_tags)
        return all_tags

    @pytest.fixture()
    def config_current(self, monkeypatch):
        config_current = MagicMock()
        monkeypatch.setattr('handlers.config.current', config_current)
        return config_current

    def test_database_find_movies_called(self, find_movies, movie_gui, all_tags, config_current):
        handlers._select_movie_callback(self.MOVIE)
        find_movies.assert_called_once_with(dict(title=self.TITLE, year=[str(self.YEAR)]))

    def test_movie_gui_called(self, find_movies, movie_gui, all_tags, config_current, check):
        handlers._select_movie_callback(self.MOVIE)
        call_args = movie_gui.call_args
        tk_root, tmdb, all_tags = call_args.args
        movie, edit_movie, delete_movie = call_args.kwargs.items()

        msg = 'Incorrect argument for guiwidgets_2.MovieGUI.'
        check.equal(tk_root, config_current.tk_root, msg)
        check.equal(tmdb, handlers._tmdb_io_handler, msg)
        check.equal(all_tags, self.TAGS, msg)
        check.equal(movie, ('old_movie', self.MOVIE), msg)
        k, v = edit_movie
        check.equal(k, 'edit_movie_callback', msg)
        check.equal(str(v)[10:30], '_edit_movie_callback', msg)
        check.equal(delete_movie, ('delete_movie_callback', handlers._delete_movie_callback), msg)
