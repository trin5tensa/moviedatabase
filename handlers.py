"""Menu handlers.

This module is the glue between the user's selection of a menu item and the gui."""

#  Copyright© 2020. Stephen Rigden.
#  Last modified 1/1/20, 8:24 AM by stephen.
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

from typing import Sequence

import config
import database
import exception
import guiwidgets
import impexp


def about_dialog():
    """Display the about dialog."""
    guiwidgets.gui_messagebox(config.app.tk_root, config.app.name, config.app.version)


def add_movie():
    """ Get new movie data from the user and add it to the database. """
    tags = database.all_tags()
    guiwidgets.MovieGUI(config.app.tk_root, tags, add_movie_callback)


def add_movie_callback(movie: config.MovieDict, tags: Sequence[str]):
    """ Add user supplied data to the database.
    
    Args:
        movie:
        tags:
    """
    database.add_movie(movie)
    # TODO Remove note and 'noinspection' when fixed
    #   Pycharm reported bug:  https://youtrack.jetbrains.com/issue/PY-39404
    # noinspection PyTypedDict
    movies = (config.MovieKeyDict(title=movie['title'], year=movie['year']),)
    for tag in tags:
        database.add_tag_and_links(tag, movies)


def edit_movie():
    """ Get search movie data from the user and search for compliant records"""
    tags = database.all_tags()
    guiwidgets.SearchGUI(config.app.tk_root, tags, edit_movie_callback)


def edit_movie_callback(movie: config.MovieDict, tags: Sequence[str]):
    # moviedb-#109 Prototype function
    # moviedb-#109 Test this function
    print()
    gui_dict: config.FindMovieDict = {**movie}
    gui_dict['tags'] = tags
    
    # Remove empty items otherwise SQL will treat them as meaningful.
    criteria = {k: v for k, v in gui_dict.items() if v != '' and v != [] and v != ['', '']}
    print(f"{criteria=}")
    
    find_gen = database.find_movies(criteria)
    
    if not next(find_gen):
        raise exception.MovieSearchFoundNothing
    
    # moviedb-#109 Call new gui select and edit screen with argument 'movie'.
    for movie in find_gen:
        print(f"{movie}")


def import_movies():
    """Open a csv file and load the contents into the database."""
    csv_fn = guiwidgets.gui_askopenfilename(parent=config.app.tk_root,
                                            filetypes=(('Movie import files', '*.csv'),))
    try:
        impexp.import_movies(csv_fn)
    except impexp.MoviedbInvalidImportData as exc:
        guiwidgets.gui_messagebox(config.app.tk_root, message='Errors were found in the input file.',
                                  detail=exc.args[0], icon='warning')
