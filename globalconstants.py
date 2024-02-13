"""Global constants and type definitions."""

#  Copyright (c) 2024-2024. Stephen Rigden.
#  Last modified 2/12/24, 6:20 AM by stephen.
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
from collections.abc import Sequence
from typing import TypedDict, NotRequired

TITLE = "title"
YEAR = "year"
DIRECTOR = "director"
DURATION = "minutes"
NOTES = "notes"
MOVIE_TAGS = "tags"


class MovieTD(TypedDict):
    """Type definition for movie."""

    TITLE: str
    YEAR: str
    DIRECTOR: NotRequired[Sequence[str]]
    DURATION: NotRequired[str]
    NOTES: NotRequired[str]
    MOVIE_TAGS: NotRequired[Sequence[str]]