"""Menu handlers test module."""

#  Copyright© 2024. Stephen Rigden.
#  Last modified 10/19/24, 10:33 AM by stephen.
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

from unittest.mock import MagicMock

from pytest_check import check

import config
from globalconstants import MovieTD, MovieInteger
from gui_handlers import (
    guidatabase,
    moviebagfacade,
)


# noinspection DuplicatedCode
def test_add_movie(monkeypatch):
    monkeypatch.setattr(guidatabase.config, "current", MagicMock(name="current"))
    test_tags = {"tag 1", "tag 2", "tag 3"}
    mock_select_tags = MagicMock(name="mock_select_tags", return_value=test_tags)
    monkeypatch.setattr(guidatabase.tables, "select_all_tags", mock_select_tags)
    mock_add_movie_gui = MagicMock(name="mock_add_movie_gui")
    monkeypatch.setattr(guidatabase.guiwidgets_2, "AddMovieGUI", mock_add_movie_gui)
    movie_bag = guidatabase.MovieBag()

    guidatabase.add_movie(movie_bag)

    mock_add_movie_gui.assert_called_once_with(
        guidatabase.config.current.tk_root,
        guidatabase._tmdb_io_handler,
        list(test_tags),
        movie_bag=movie_bag,
        add_movie_callback=guidatabase.add_movie_callback,
    )


def test_add_movie_callback(monkeypatch):
    add_movie = MagicMock(name="add_movie")
    monkeypatch.setattr(guidatabase.tables, "add_movie", add_movie)
    gui_movie = MovieTD(title="Add movie test", year="4242")
    # noinspection PyUnresolvedReferences
    movie_bag = moviebagfacade.convert_from_movie_td(gui_movie)

    guidatabase.add_movie_callback(gui_movie)

    add_movie.assert_called_once_with(movie_bag=movie_bag)


# noinspection PyPep8Naming
def test_add_movie_callback_with_MovieExists_exception(monkeypatch):
    # noinspection PyTypeChecker
    table_add_movie = MagicMock(
        name="table_add_movie",
        side_effect=guidatabase.tables.MovieExists("", "", Exception),
    )
    monkeypatch.setattr(guidatabase.tables, "add_movie", table_add_movie)
    guid_add_movie = MagicMock(name="guid_add_movie")
    monkeypatch.setattr(guidatabase, "add_movie", guid_add_movie)
    gui_movie = MovieTD(title="Add movie test", year="4242")
    messagebox = MagicMock(name="messagebox")
    monkeypatch.setattr(guidatabase.guiwidgets_2, "gui_messagebox", messagebox)
    monkeypatch.setattr(guidatabase, "config", MagicMock(name="config"))
    # noinspection PyUnresolvedReferences
    movie_bag = moviebagfacade.convert_from_movie_td(gui_movie)

    guidatabase.add_movie_callback(gui_movie)

    with check:
        messagebox.assert_called_once_with(
            guidatabase.config.current.tk_root,
            message=guidatabase.TITLE_AND_YEAR_EXISTS_MSG,
        )
    with check:
        guid_add_movie.assert_called_once_with(movie_bag)


# noinspection DuplicatedCode, PyPep8Naming
def test_add_movie_callback_with_InvalidReleaseYear_exception(monkeypatch):
    # noinspection PyTypeChecker
    table_add_movie = MagicMock(
        name="table_add_movie",
        side_effect=guidatabase.tables.InvalidReleaseYear("", "", Exception),
    )
    monkeypatch.setattr(guidatabase.tables, "add_movie", table_add_movie)
    guid_add_movie = MagicMock(name="guid_add_movie")
    monkeypatch.setattr(guidatabase, "add_movie", guid_add_movie)
    messagebox = MagicMock(name="messagebox")
    monkeypatch.setattr(guidatabase.guiwidgets_2, "gui_messagebox", messagebox)
    monkeypatch.setattr(guidatabase, "config", MagicMock(name="config"))
    gui_movie = MovieTD(title="Add movie test", year="4242")
    # noinspection PyUnresolvedReferences
    movie_bag = moviebagfacade.convert_from_movie_td(gui_movie)

    guidatabase.add_movie_callback(gui_movie)

    with check:
        messagebox.assert_called_once_with(
            guidatabase.config.current.tk_root,
            message=guidatabase.IMPOSSIBLE_RELEASE_YEAR_MSG,
        )
    with check:
        guid_add_movie.assert_called_once_with(movie_bag)


# noinspection DuplicatedCode, PyPep8Naming
def test_add_movie_callback_with_TagNotFound_exception(monkeypatch):
    table_add_movie = MagicMock(
        name="table_add_movie",
        side_effect=guidatabase.tables.TagNotFound,
    )
    monkeypatch.setattr(guidatabase.tables, "add_movie", table_add_movie)
    guid_add_movie = MagicMock(name="guid_add_movie")
    monkeypatch.setattr(guidatabase, "add_movie", guid_add_movie)
    messagebox = MagicMock(name="messagebox")
    monkeypatch.setattr(guidatabase.guiwidgets_2, "gui_messagebox", messagebox)
    monkeypatch.setattr(guidatabase, "config", MagicMock(name="config"))
    gui_movie = MovieTD(title="Add movie test", year="4242")
    # noinspection PyUnresolvedReferences
    movie_bag = moviebagfacade.convert_from_movie_td(gui_movie)

    guidatabase.add_movie_callback(gui_movie)

    with check:
        messagebox.assert_called_once_with(
            guidatabase.config.current.tk_root, message=guidatabase.TAG_NOT_FOUND_MSG
        )
    with check:
        guid_add_movie.assert_called_once_with(movie_bag)


# noinspection DuplicatedCode
def test_search_for_movie(monkeypatch):
    monkeypatch.setattr(guidatabase.config, "current", MagicMock(name="current"))
    test_tags = {"tag 1", "tag 2", "tag 3"}
    mock_select_tags = MagicMock(name="mock_select_tags", return_value=test_tags)
    monkeypatch.setattr(guidatabase.tables, "select_all_tags", mock_select_tags)
    mock_search_movie_gui = MagicMock(name="mock_search_movie_gui")
    monkeypatch.setattr(guidatabase.guiwidgets, "SearchMovieGUI", mock_search_movie_gui)

    guidatabase.search_for_movie()

    mock_search_movie_gui.assert_called_once_with(
        guidatabase.config.current.tk_root,
        guidatabase.search_for_movie_callback,
        list(test_tags),
    )


# noinspection DuplicatedCode
def test_search_for_movie_callback(monkeypatch):
    # Arrange
    match_movies = MagicMock(name="match_movies", return_value=[])
    monkeypatch.setattr(guidatabase.tables, "match_movies", match_movies)

    title = "title search"
    year = "4242"
    director_1 = "Michael Madison"
    director_2 = "Nancy Nichols"
    minutes = "142"
    notes = "A test note"
    criteria = config.FindMovieTypedDict(
        title=title,
        year=[year],
        director=director_1 + ", " + director_2,
        minutes=[minutes],
        notes=notes,
    )
    tags = ["test tag 1", "test tag 2"]

    match = guidatabase.MovieBag(
        title=title,
        year=MovieInteger(year),
        directors={director_1, director_2},
        duration=MovieInteger(minutes),
        notes=notes,
        movie_tags=set(tags),
    )

    monkeypatch.setattr(
        guidatabase.guiwidgets_2, "gui_messagebox", lambda *args, **kwargs: None
    )
    monkeypatch.setattr(guidatabase.config, "current", MagicMock(name="current"))
    monkeypatch.setattr(guidatabase, "search_for_movie", lambda: None)

    # Act
    guidatabase.search_for_movie_callback(criteria, tags)
    # Assert
    match_movies.assert_called_once_with(match=match)


# noinspection DuplicatedCode
def test_search_for_movie_callback_with_year_range(monkeypatch):
    # Arrange
    match_movies = MagicMock(name="match_movies", return_value=[])
    monkeypatch.setattr(guidatabase.tables, "match_movies", match_movies)

    title = "title search"
    year_1 = "4242"
    year_2 = "4247"
    criteria = config.FindMovieTypedDict(title=title, year=[year_1, year_2])
    tags = ["test tag 1", "test tag 2"]

    match = guidatabase.MovieBag(
        title=title,
        year=(MovieInteger(f"{year_1}-{year_2}")),
        movie_tags=set(tags),
    )

    monkeypatch.setattr(
        guidatabase.guiwidgets_2, "gui_messagebox", lambda *args, **kwargs: None
    )
    monkeypatch.setattr(guidatabase.config, "current", MagicMock(name="current"))
    monkeypatch.setattr(guidatabase, "search_for_movie", lambda: None)

    # Act
    guidatabase.search_for_movie_callback(criteria, tags)
    # Assert
    match_movies.assert_called_once_with(match=match)


def test_search_for_movie_callback_returning_0_movies(monkeypatch):
    title = "title search"
    year = "4242"
    criteria = config.FindMovieTypedDict(title=title, year=[year])
    tags = ["test tag 1"]

    match_movies = MagicMock(name="match_movies", return_value=[])
    monkeypatch.setattr(guidatabase.tables, "match_movies", match_movies)
    messagebox = MagicMock(name="messagebox")
    monkeypatch.setattr(guidatabase.guiwidgets_2, "gui_messagebox", messagebox)
    monkeypatch.setattr(guidatabase, "config", MagicMock(name="config"))
    search_for_movie = MagicMock(name="search_for_movie")
    monkeypatch.setattr(guidatabase, "search_for_movie", search_for_movie)

    guidatabase.search_for_movie_callback(criteria, tags)

    with check:
        messagebox.assert_called_once_with(
            guidatabase.config.current.tk_root,
            message=guidatabase.NO_COMPLIANT_MOVIES_FOUND_MSG,
        )
    with check:
        search_for_movie.assert_called_once_with()


def test_search_for_movie_callback_returning_1_movie(monkeypatch):
    year = "4242"
    movie_1 = guidatabase.MovieBag(title="Old Movie", year=MovieInteger(year))
    match_movies = MagicMock(name="match_movies", return_value=[movie_1])
    monkeypatch.setattr(guidatabase.tables, "match_movies", match_movies)

    title = "title search"
    criteria = config.FindMovieTypedDict(title=title, year=[year])

    edit_movie_gui = MagicMock(name="edit_movie_gui")
    monkeypatch.setattr(guidatabase.guiwidgets_2, "EditMovieGUI", edit_movie_gui)
    edit_movie_callback = MagicMock(name="edit_movie_callback")
    monkeypatch.setattr(guidatabase, "edit_movie_callback", edit_movie_callback)
    old_movie = guidatabase.convert_to_movie_update_def(movie_1)
    test_tags = ["tag 1", "tag 2", "tag 3"]
    select_all_tags = MagicMock(name="select_all_tags", return_value=test_tags)
    monkeypatch.setattr(guidatabase.tables, "select_all_tags", select_all_tags)
    monkeypatch.setattr(guidatabase.config, "current", MagicMock(name="current"))

    guidatabase.search_for_movie_callback(criteria, test_tags)

    with check:
        edit_movie_gui.assert_called_once_with(
            guidatabase.config.current.tk_root,
            guidatabase._tmdb_io_handler,
            test_tags,
            old_movie=old_movie,
            edit_movie_callback=guidatabase.edit_movie_callback(old_movie),
            delete_movie_callback=guidatabase.delete_movie_callback,
        )
    with check:
        edit_movie_callback.assert_called_with(old_movie)


def test_search_for_movie_callback_returning_2_movies(monkeypatch):
    movie_1 = guidatabase.MovieBag(title="Old Movie", year=MovieInteger(4242))
    movie_2 = guidatabase.MovieBag(title="Son of Old Movie", year=MovieInteger(4243))
    movies_found = [
        guidatabase.moviebagfacade.convert_to_movie_update_def(movie_1),
        guidatabase.moviebagfacade.convert_to_movie_update_def(movie_2),
    ]
    monkeypatch.setattr(
        guidatabase.tables,
        "match_movies",
        MagicMock(name="match_movies", return_value=movies_found),
    )
    criteria = config.FindMovieTypedDict()
    tags = []

    select_movie_gui = MagicMock(name="select_movie_gui")
    monkeypatch.setattr(guidatabase.guiwidgets, "SelectMovieGUI", select_movie_gui)
    monkeypatch.setattr(guidatabase.config, "current", MagicMock(name="current"))
    monkeypatch.setattr(
        guidatabase, "_select_movie_callback", MagicMock(name="select_movie_callback")
    )

    guidatabase.search_for_movie_callback(criteria, tags)

    select_movie_gui.assert_called_once_with(
        guidatabase.config.current.tk_root,
        movies_found,
        guidatabase._select_movie_callback,
    )
