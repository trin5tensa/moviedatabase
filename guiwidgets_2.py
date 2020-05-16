"""GUI Windows.

This module includes windows for presenting data supplied to it and returning entered data to its
callers.
"""

#  Copyright© 2020. Stephen Rigden.
#  Last modified 5/14/20, 2:55 PM by stephen.
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

import itertools
import tkinter as tk
import tkinter.ttk as ttk
from dataclasses import dataclass, field
from tkinter import filedialog, messagebox
from typing import Callable, Dict, Mapping, Sequence, Tuple, TypeVar

import neurons


TAG_FIELD_NAMES = ('tag',)
TAG_FIELD_TEXTS = ('Tag',)
COMMIT_TEXT = 'Commit'
CANCEL_TEXT = 'Cancel'

ParentType = TypeVar('ParentType', tk.Tk, ttk.Frame)


@dataclass
class AddTagGUI:
    """ A form for adding a tag."""
    parent: tk.Tk
    add_tag_callback: Callable
    
    # The main outer frame of this class.
    outer_frame: ttk.Frame = field(default=None, init=False, repr=False)
    
    # An internal dictionary to simplify field data management.
    entry_fields: Dict[str, 'EntryField'] = field(default_factory=dict, init=False, repr=False)
    
    def __post_init__(self):
        # Initialize an internal dictionary to simplify field data management.
        self.entry_fields = create_entry_fields(TAG_FIELD_NAMES, TAG_FIELD_TEXTS)
        
        # Create outer frames to hold fields and buttons.
        self.outer_frame, body_frame, buttonbox = create_input_form_framing(self.parent)
        
        # Create label and field
        create_input_form_fields(body_frame, TAG_FIELD_NAMES, self.entry_fields)
        
        # Populate buttonbox with commit and cancel buttons
        column_num = itertools.count()
        commit_button = create_button(buttonbox, COMMIT_TEXT, column=next(column_num),
                                      command=self.commit, enabled=False)
        create_button(buttonbox, CANCEL_TEXT, column=next(column_num),
                      command=self.destroy).focus_set()
        
        # Link commit button to tag field
        neuron = link_or_neuron_to_button(enable_button_wrapper(commit_button))
        link_field_to_neuron(self.entry_fields, TAG_FIELD_NAMES[0], neuron,
                             notify_neuron_wrapper(self.entry_fields,
                                                   TAG_FIELD_NAMES[0], neuron))
    
    def commit(self):
        """The user clicked the 'Commit' button."""
        self.add_tag_callback(self.entry_fields[TAG_FIELD_NAMES[0]].textvariable.get())
        self.destroy()
    
    def destroy(self):
        """Destroy all widgets of this class."""
        self.outer_frame.destroy()


# noinspection PyMissingOrEmptyDocstring
@dataclass
class EditTagGUI:
    # moviedb-#164
    #   Code
    #   Test
    #   Document
    pass


def gui_messagebox(parent: ParentType, message: str, detail: str = '', icon: str = 'info'):
    """Present a Tk messagebox."""
    messagebox.showinfo(parent, message, detail=detail, icon=icon)


def gui_askopenfilename(parent: ParentType, filetypes: Sequence[Sequence[str]]):
    """Present a Tk askopenfilename."""
    return filedialog.askopenfilename(parent=parent, filetypes=filetypes)


@dataclass
class EntryField:
    """A support class for attributes of a gui entry field."""
    label_text: str
    original_value: str
    widget: ttk.Entry = None
    textvariable: tk.StringVar = None
    observer: neurons.Observer = field(default_factory=neurons.Observer, init=False, repr=False)
    
    def __post_init__(self):
        self.textvariable = tk.StringVar()


def create_entry_fields(names: Sequence[str], texts: Sequence[str]) -> dict:
    """Create an internal dictionary to simplify field data management.
    
    Args:
        names: A sequence of names of the fields
        texts: A sequence of text to be seen by the user.

    Returns:
        key: The internal name of the field.
        value: An EntryField instance.
    """
    return {internal_name: EntryField(field_text, '')
            for internal_name, field_text in zip(names, texts)}


def create_input_form_framing(parent: tk.Tk) -> Tuple[ttk.Frame, ttk.Frame, ttk.Frame]:
    """Create the outer frames for an input form.

    This consists of an upper body and a lower buttonbox frame. THe body frame has two columns,
    one for the field labels and one for the entry fields.

    Args:
        parent: The Tk parent frame.

    Returns:
        Outer frame which contains the body and buttonbox frames.
        Body frame
        Buttonbox frame
    """
    outer_frame = ttk.Frame(parent)
    outer_frame.grid(column=0, row=0, sticky='nsew')
    outer_frame.columnconfigure(0, weight=1)
    outer_frame.rowconfigure(0, weight=1)
    outer_frame.rowconfigure(1, minsize=35)
    
    body_frame = ttk.Frame(outer_frame, padding=(10, 25, 10, 0))
    body_frame.grid(column=0, row=0, sticky='n')
    
    buttonbox = ttk.Frame(outer_frame, padding=(5, 5, 10, 10))
    buttonbox.grid(column=0, row=1, sticky='e')
    
    return outer_frame, body_frame, buttonbox


def create_input_form_fields(body_frame: ttk.Frame, names: Sequence[str],
                             entry_fields: Mapping[str, EntryField]):
    """Create the labels and fields for an entry form.
    
    Args:
        body_frame: The outer frame for the labels and fields.
        names: A sequence of names of the fields.
        entry_fields: A mapping of the field names to an instance of EntryField.
    """
    
    # Create a column for the labels.
    body_frame.columnconfigure(0, weight=1, minsize=30)
    # Create a column for the fields.
    body_frame.columnconfigure(1, weight=1)
    
    for row_ix, internal_name in enumerate(names):
        label = ttk.Label(body_frame, text=entry_fields[internal_name].label_text)
        label.grid(column=0, row=row_ix, sticky='e', padx=5)
        entry = ttk.Entry(body_frame, textvariable=entry_fields[internal_name].textvariable, width=36)
        entry.grid(column=1, row=row_ix)
        entry_fields[internal_name].widget = entry


def create_button(buttonbox: ttk.Frame, text: str, column: int, command: Callable,
                  enabled: bool = True) -> ttk.Button:
    """Create a button
    
    Args:
        buttonbox: The enclosing buttonbox.
        text: The enclosing buttonbox.
        column: The index of the button in the buttonbox. '0' is leftmost position.
        command: The command to be executed when the button is clicked.
        enabled: Sets the initial enabled or disables state of the button.

    Returns:
        The button
    """
    button = ttk.Button(buttonbox, text=text, command=command)
    button.grid(column=column, row=0)
    button.bind('<Return>', lambda event, b=button: b.invoke())
    if not enabled:
        button.state(['disabled'])
    return button


def enable_button_wrapper(button: ttk.Button) -> Callable:
    """Create the callback for a button.

    This will be registered with a neuron as a notifee.
    
    Args:
        button:

    Returns:
        A callable which will set the enabled state of the button.
    """
    
    def enable_button(state: bool):
        """Enable or disable the button.
        
        Args:
            state:
        """
        if state:
            button.state(['!disabled'])
        else:
            button.state(['disabled'])
    
    return enable_button


def link_or_neuron_to_button(change_button_state: Callable) -> neurons.OrNeuron:
    """Create an "Or' neuron and link it to a button.
    
    Args:
        change_button_state:

    Returns:

    """
    neuron = neurons.OrNeuron()
    neuron.register(change_button_state)
    return neuron


def link_field_to_neuron(entry_fields: dict, name: str, neuron: neurons.Neuron, notify_neuron: Callable):
    """Link the fields associated with a button to its neuron.
    
    Args:
        entry_fields: A mapping of field names to instances of EntryField.
        name: …of the field being mapped to the neuron.
        neuron:
        notify_neuron:
    """
    entry_fields[name].textvariable.trace_add('write', notify_neuron)
    neuron.register_event(name)


def notify_neuron_wrapper(entry_fields: dict, name: str, neuron: neurons.Neuron) -> Callable:
    """Create the callback for an observed field.

        This will be registered as the 'trace_add' callback for an entry field.
    
    Args:
        entry_fields: A mapping of the field names to instances of EntryField.
        name: Field name.
        neuron: The neuron which will be notified of the field's state.

    Returns:
        The callback which will be called when the field is changed.
    """
    
    # noinspection PyUnusedLocal
    def notify_neuron(*args):
        """Call the neuron when the field changes.

        Args:
            *args: Not used. Required to match unused arguments from caller.
        """
        state = (entry_fields[name].textvariable.get()
                 != str(entry_fields[name].original_value))
        neuron(name, state)
    
    return notify_neuron