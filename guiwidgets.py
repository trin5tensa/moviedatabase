"""GUI Windows.

This module includes windows for presenting data supplied to it and returning entered data to its
callers.
"""

#  Copyright© 2019. Stephen Rigden.
#  Last modified 12/12/19, 12:34 PM by stephen.
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

import tkinter as tk
import tkinter.ttk as ttk
from dataclasses import dataclass, field
from tkinter import messagebox
from typing import Callable, Dict, List, Sequence

import config
import exception
import observerpattern
from config import MovieDict


INTERNAL_NAMES = ('title', 'year', 'director', 'minutes', 'notes')
FIELD_TEXTS = ('Title *', 'Year *', 'Director', 'Length (minutes)', 'Notes')
COMMIT_TEXT = 'Commit'
CANCEL_TEXT = 'Cancel'
SELECT_TAGS_TEXT = 'Select tags'


@dataclass
class MovieGUI:
    """ Create a form for entering or editing a movie."""
    parent: tk.Tk
    # List of all tags in the database.
    tags: Sequence[str]
    # On exit this callback will be called with a dictionary of fields and user entered values.
    callback: Callable[[MovieDict], None]
    
    caller_fields: MovieDict = field(default_factory=dict)
    outer_frame: ttk.Frame = field(default=None, init=False, repr=False)
    entry_fields: Dict[str, 'MovieField'] = field(default_factory=dict, init=False, repr=False)
    commit_neuron: observerpattern.Neuron = field(default_factory=observerpattern.Neuron,
                                                  init=False, repr=False)
    selected_tags: List[str] = field(default_factory=list, init=False, repr=False)
    
    def __post_init__(self):
        self.entry_fields = {internal_name: MovieField(field_text,
                                                       self.caller_fields.get(internal_name, ''))
                             for internal_name, field_text
                             in zip(INTERNAL_NAMES, FIELD_TEXTS)}
        
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)
        
        self.outer_frame = ttk.Frame(self.parent)
        self.outer_frame.grid(column=0, row=0, sticky='nsew')
        self.outer_frame.columnconfigure(0, weight=1)
        self.outer_frame.rowconfigure(0, weight=1)
        self.outer_frame.rowconfigure(1, minsize=35)
        
        self.create_body(self.outer_frame)
        self.create_buttonbox(self.outer_frame)
    
    def create_body(self, outerframe: ttk.Frame):
        """Create the body of the form with a column for labels and another for user input fields."""
        body_frame = ttk.Frame(outerframe, padding=(10, 25, 10, 0))
        body_frame.grid(column=0, row=0, sticky='n')
        body_frame.columnconfigure(0, weight=1, minsize=30)
        body_frame.columnconfigure(1, weight=1)
    
        # Create entry fields and their labels.
        for row_ix, internal_name in enumerate(INTERNAL_NAMES):
            label = ttk.Label(body_frame, text=self.entry_fields[internal_name].label_text)
            label.grid(column=0, row=row_ix, sticky='e', padx=5)
            entry = ttk.Entry(body_frame, textvariable=self.entry_fields[internal_name].textvariable,
                              width=36)
            entry.grid(column=1, row=row_ix)
            # moviedb-#94 Test following line
            self.entry_fields[internal_name].widget = entry
    
        # Set default field values
        # moviedb-#94 Restructure field customization by field instead of type of customization?
        # moviedb-#94 Test following suite
        # moviedb-#94 If user enters a title then the commit button ought to be enabled in case user
        #   wants the default year; i.e. there will be no events for the 'year' field which will
        #   trigger a state alteration of the observing neuron. As written the user is forced to click
        #   in the 'year; field to enable the 'commit' button.
        self.entry_fields['year'].textvariable.set('2020')
        self.entry_fields['minutes'].textvariable.set('0')
    
        # Customize validation of entry fields.
        # moviedb-#94 Prototype code
        # moviedb-#94 Test following suite
    
        minutes = self.entry_fields['minutes'].widget
        registered_callback = minutes.register(self.validate_int)
        minutes.config(validate='key', validatecommand=(registered_callback, '%S'))
    
        year = self.entry_fields['year'].widget
        registered_callback = year.register(self.validate_int)
        year.config(validate='key', validatecommand=(registered_callback, '%S'))
    
        # Customize  neuron links to entry fields.
        self.neuron_linker('title', self.commit_neuron, self.neuron_callback)
        self.neuron_linker('year', self.commit_neuron, self.neuron_callback)
    
        # Create treeview for tag selection.
        # moviedb-#95 The tags of an existing record should be shown as selected.
        label = ttk.Label(body_frame, text=SELECT_TAGS_TEXT)
        label.grid(column=0, row=6, sticky='e', padx=5)
        tags_frame = ttk.Frame(body_frame, padding=5)
        tags_frame.grid(column=1, row=6, sticky='w')
        tree = ttk.Treeview(tags_frame, columns=('tags',), height=5, selectmode='extended',
                            show='tree', padding=5)
        tree.grid(column=0, row=0, sticky='w')
        tree.column('tags', width=100)
        for tag in self.tags:
            tree.insert('', 'end', tag, text=tag, tags='tags')
        tree.tag_bind('tags', '<<TreeviewSelect>>', callback=self.treeview_callback(tree))
        scrollbar = ttk.Scrollbar(tags_frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar.grid(column=1, row=0)
        tree.configure(yscrollcommand=scrollbar.set)
    
    def create_buttonbox(self, outerframe: ttk.Frame):
        """Create the buttons."""
        buttonbox = ttk.Frame(outerframe, padding=(5, 5, 10, 10))
        buttonbox.grid(column=0, row=1, sticky='e')
        
        # Commit button
        commit = ttk.Button(buttonbox, text=COMMIT_TEXT, command=self.commit)
        commit.grid(column=0, row=0)
        commit.bind('<Return>', lambda event, b=commit: b.invoke())
        commit.state(['disabled'])
        self.commit_neuron.register(self.button_state_callback(commit))
        
        # Cancel button
        cancel = ttk.Button(buttonbox, text=CANCEL_TEXT, command=self.destroy)
        cancel.grid(column=1, row=0)
        cancel.bind('<Return>', lambda event, b=cancel: b.invoke())
        cancel.focus_set()
    
    def neuron_linker(self, internal_name: str, neuron: observerpattern.Neuron,
                      neuron_callback: Callable):
        """Link a field to a neuron."""
        self.entry_fields[internal_name].textvariable.trace_add('write',
                                                                neuron_callback(internal_name, neuron))
        neuron.register_event(internal_name)
    
    def neuron_callback(self, internal_name: str, neuron: observerpattern.Neuron) -> Callable:
        """Create the callback for an observed field.
        
        This will be registered as the 'trace_add' callback for an entry field.
        """
        
        # noinspection PyUnusedLocal
        def change_neuron_state(*args):
            """Call the neuron when the field changes.
            
            Args:
                *args: Not used. Required to match unused arguments from caller..
            """
            state = (self.entry_fields[internal_name].textvariable.get()
                     != self.entry_fields[internal_name].original_value)
            neuron(internal_name, state)
    
        return change_neuron_state
    
    @staticmethod
    def button_state_callback(button: ttk.Button) -> Callable:
        """Create the callback for a button.
        
        This will be registered with a neuron as s notifee."""

        def change_button_state(state: bool):
            """Enable or disable the commit button when the title or year field change."""
            if state:
                button.state(['!disabled'])
            else:
                button.state(['disabled'])

        return change_button_state
    
    def treeview_callback(self, tree: ttk.Treeview):
        """Create a callback which will be called whenever the user selection is changed.
        
        Args:
            tree:

        Returns: The callback.
        """

        # noinspection PyUnusedLocal
        def update_tag_selection(*args):
            """Save the newly changed user selection.
            
            Args:
                *args: Not used. Needed for compatibility with Tk:Tcl caller.
            """
            self.selected_tags = tree.selection()

        return update_tag_selection
    
    @staticmethod
    def validate_int(user_input: str) -> bool:
        """Validate integer input by user.
        
        Use Case: Supports field validation by Tk
        """
        # moviedb-#94 Test this method
        try:
            int(user_input)
        except ValueError:
            config.app.tk_root.bell()
        else:
            return True
        return False
    
    @staticmethod
    def validate_int_range(user_input: int, lowest: int = None, highest: int = None) -> bool:
        """Validate that user input is an integer within a valid range.

        Use Case: Supports field validation by Tk
        """
        # moviedb-#94 Delete this method if validation can be carried out by database integrity checks.
        # moviedb-#94 Test this method
        lowest = user_input > lowest if lowest else True
        highest = user_input < highest if highest else True
        return lowest and highest
    
    def commit(self):
        """The user clicked the commit button."""
        # moviedb-#94 Test new lines
        return_fields = {internal_name: movie_field.textvariable.get()
                         for internal_name, movie_field in self.entry_fields.items()}
        
        # Validate the year range
        # TODO Get the range limits from the SQL schema
        if not self.validate_int_range(int(return_fields['year']), 1877, 10000):
            msg = 'Invalid year.'
            detail = 'The year must be between 1877 and 10000.'
            messagebox.showinfo(parent=self.parent, message=msg, detail=detail)
            return
        
        # Commit and exit
        try:
            self.callback(return_fields, self.selected_tags)
        except exception.MovieDBConstraintFailure:
            msg = 'Database constraint failure.'
            detail = 'This title and year are already present in the database.'
            messagebox.showinfo(parent=self.parent, message=msg, detail=detail)
        else:
            self.destroy()
    
    def destroy(self):
        """Destroy all widgets of this class."""
        self.outer_frame.destroy()


@dataclass
class MovieField:
    """A support class for attributes of a gui entry field."""
    label_text: str
    original_value: str
    widget: ttk.Entry = None
    textvariable: tk.StringVar = None
    observer: observerpattern.Observer = None
    
    def __post_init__(self):
        self.textvariable = tk.StringVar()
        self.observer = observerpattern.Observer()
