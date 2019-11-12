"""Application configuration data """

#  Copyright© 2019. Stephen Rigden.
#  Last modified 11/12/19, 4:00 PM by stephen.
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
from typing import Optional


tk: 'tk'
mainwindow: 'mainwindow'


@dataclass
class Config:
    """The applications configuration data.
    
    A single object of this class is created in the application's start_up() function.
    """
    # Program
    name: str
    version: str
    # tk.Tk screen geometry
    geometry: str = None

    # Save the root window for easy access for testing.
    tk_root: 'tk.Tk' = None
    root_pane: 'mainwindow.MainWindow' = None


app: Optional[Config] = None
