""" Test._guiwidgets_<..>.

This module contains new tests written after Brian Okken's course and book on pytest in Fall 2022 together with
mocks from Python's unittest.mok module.

Test strategies are noted for each class but, in general, they test the interface with other code and not the
internal implementation of widgets.
"""

#  Copyright (c) 2023-2023. Stephen Rigden.
#  Last modified 10/21/23, 11:55 AM by stephen.
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

from contextlib import contextmanager
from unittest.mock import MagicMock, call

import pytest
from pytest_check import check

import config
import guiwidgets_2

TEST_TITLE = 'test moviedb'
TEST_VERSION = 'Test version'


# noinspection PyMissingOrEmptyDocstring
class TestMovieGUI:
    """
    Detect any changes to calls to other functions and methods and changes to the arguments to those calls.
    Changes in the API of called functions and methods are not part of this test suite.
    """

    def test_post_init(self, monkeypatch):
        # todo Do all of these need mocks? Without an assignment they cannot be interrogated.
        monkeypatch.setattr('guiwidgets_2._create_entry_fields', mock_create_entry_fields := MagicMock())
        monkeypatch.setattr('guiwidgets_2.MovieGUI.original_values', mock_original_values := MagicMock())
        monkeypatch.setattr('guiwidgets_2.MovieGUI.framing', mock_framing := MagicMock())
        mock_framing.return_value = [MagicMock(), mock_body_frame := MagicMock(),
                                     mock_buttonbox := MagicMock(),
                                     mock_internet_frame := MagicMock()]
        monkeypatch.setattr('guiwidgets_2.MovieGUI.set_initial_tag_selection',
                            mock_set_initial_tag_selection := MagicMock())
        monkeypatch.setattr('guiwidgets_2.MovieGUI._create_buttons', mock_create_buttons := MagicMock())

        monkeypatch.setattr('guiwidgets_2._InputZone', mock_inputzone := MagicMock())
        monkeypatch.setattr('guiwidgets_2._focus_set', mock_focus_set := MagicMock())
        monkeypatch.setattr('guiwidgets_2.ttk.Treeview', mock_treeview := MagicMock())
        monkeypatch.setattr('guiwidgets_2.itertools.count', MagicMock())
        monkeypatch.setattr('guiwidgets_2._create_button', mock_create_button := MagicMock())
        monkeypatch.setattr('guiwidgets_2.MovieGUI.tmdb_consumer', mock_tmdb_consumer := MagicMock())

        with self.moviegui(monkeypatch) as cut:
            # Test initialize an internal dictionary.
            with check:
                mock_create_entry_fields.assert_called_once_with(guiwidgets_2.MOVIE_FIELD_NAMES,
                                                                 guiwidgets_2.MOVIE_FIELD_TEXTS)
            check.equal(cut.title, guiwidgets_2.MOVIE_FIELD_NAMES[0])
            with check:
                mock_original_values.assert_called_once_with()
            cut.entry_fields.fromkeys(guiwidgets_2.MOVIE_FIELD_NAMES)

            # Test create frames.
            with check:
                mock_framing.assert_called_once_with(cut.parent)
            with check:
                mock_inputzone.assert_called_once_with(mock_body_frame)

            # Test create labels and entry widgets.
            check.equal(mock_inputzone().add_entry_row.call_count, 4)
            arg = cut.entry_fields['dummy']
            with check:
                mock_inputzone().add_entry_row.assert_has_calls([call(arg), call(arg), call(arg), call(arg)])
            with check:
                mock_focus_set.assert_called_once_with(cut.entry_fields[cut.title].widget)

            # Test create label and text widget.
            with check:
                mock_inputzone().add_text_row.assert_called_once_with(cut.entry_fields['dummy'])

            # Test create a label and treeview for movie tags.
            with check:
                mock_inputzone().add_treeview_row.assert_called_once_with(
                    'Tags', items=['test tag 1', 'test tag 2', 'test tag 3'],
                    callers_callback=cut.tags_treeview_callback)
            with check:
                mock_set_initial_tag_selection.assert_called_once_with()

            # Test create a treeview for movies retrieved from tmdb.
            with check:
                mock_treeview.assert_called_once_with(
                    mock_internet_frame, columns=('title', 'year', 'director'),
                    show=['headings'], height=20, selectmode='browse')
            check.equal(cut.tmdb_treeview.column.call_count, 3)
            with check:
                cut.tmdb_treeview.column.assert_has_calls([
                    call('title', width=300, stretch=True),
                    call('year', width=40, stretch=True),
                    call('director', width=200, stretch=True),
                    ])
            check.equal(cut.tmdb_treeview.heading.call_count, 3)
            with check:
                cut.tmdb_treeview.heading.assert_has_calls([
                    call('title', text='Title', anchor='w'),
                    call('year', text='Year', anchor='w'),
                    call('director', text='Director', anchor='w')
                    ])
            with check:
                cut.tmdb_treeview.grid.assert_called_once_with(column=0, row=0, sticky='nsew')
            with check:
                cut.tmdb_treeview.bind.assert_called_once_with('<<TreeviewSelect>>',
                                                               func=cut.tmdb_treeview_callback)

            # Test populate buttonbox with buttons.
            column_num = guiwidgets_2.itertools.count()
            with check:
                mock_create_buttons.assert_called_once_with(mock_buttonbox, column_num)
            with check:
                mock_create_button.assert_called_once_with(
                    mock_buttonbox, guiwidgets_2.CANCEL_TEXT, column=next(column_num),
                    command=cut.destroy, default='active')

            # Test start the tmdb_work_queue polling
            with check:
                mock_tmdb_consumer.assert_called_once_with()

    def test_original_values(self, monkeypatch):
        # todo Do all of these need mocks? Without an assignment they cannot be interrogated.
        monkeypatch.setattr('guiwidgets_2._create_entry_fields', MagicMock())
        monkeypatch.setattr('guiwidgets_2.MovieGUI.framing', mock_framing := MagicMock())
        mock_framing.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        monkeypatch.setattr('guiwidgets_2.MovieGUI.set_initial_tag_selection', MagicMock())
        monkeypatch.setattr('guiwidgets_2.MovieGUI._create_buttons', MagicMock())

        with pytest.raises(NotImplementedError):
            with self.moviegui(monkeypatch):
                pass

    def test_initial_tag_selection(self, monkeypatch):
        # todo Do all of these need mocks? Without an assignment they cannot be interrogated.
        monkeypatch.setattr('guiwidgets_2._create_entry_fields', MagicMock())
        monkeypatch.setattr('guiwidgets_2.MovieGUI.original_values', mock_original_values := MagicMock())
        monkeypatch.setattr('guiwidgets_2.MovieGUI.framing', mock_framing := MagicMock())
        mock_framing.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        monkeypatch.setattr('guiwidgets_2.MovieGUI._create_buttons', MagicMock())

        with pytest.raises(NotImplementedError):
            with self.moviegui(monkeypatch):
                pass

    def test_create_buttons(self, monkeypatch):
        # todo Do all of these need mocks? Without an assignment they cannot be interrogated.
        monkeypatch.setattr('guiwidgets_2._create_entry_fields', MagicMock())
        monkeypatch.setattr('guiwidgets_2.MovieGUI.original_values', mock_original_values := MagicMock())
        monkeypatch.setattr('guiwidgets_2.MovieGUI.framing', mock_framing := MagicMock())
        mock_framing.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        monkeypatch.setattr('guiwidgets_2.MovieGUI.set_initial_tag_selection', MagicMock())

        with pytest.raises(NotImplementedError):
            with self.moviegui(monkeypatch):
                pass

    def test_call_title_notifees(self, monkeypatch, movie_gui_patch):
        with self.moviegui(monkeypatch) as cut:
            func = cut.call_title_notifees(mock_commit_neuron := MagicMock())
            monkeypatch.setattr('guiwidgets_2.MovieGUI.tmdb_search', mock_tmdb_search := MagicMock())
            cut.entry_fields[cut.title].textvariable.get.return_value = mock_text = 'mock text'
            cut.entry_fields[cut.title].original_value = mock_original_text = 'mock original text'
            func(mock_commit_neuron)

            with check:
                mock_tmdb_search.assert_called_once_with(mock_text)
            with check:
                mock_commit_neuron.assert_called_once_with(cut.title, mock_text != mock_original_text)

    def test_tmdb_search(self, monkeypatch, movie_gui_patch):
        with self.moviegui(monkeypatch) as cut:
            substring = 'mock substring'
            cut.tmdb_search(substring)
            with check:
                assert cut.parent.after.mock_calls[1] == call(cut.last_text_queue_timer, cut.tmdb_search_callback,
                                                              substring, cut.tmdb_work_queue)

            # First call only
            with check:
                cut.parent.after_cancel.assert_not_called()

            # Second and subsequent calls
            cut.tmdb_search(substring)
            with check:
                cut.parent.after_cancel.assert_called_once_with(cut.last_text_event_id)

    def test_tmdb_consumer(self, monkeypatch, movie_gui_patch):
        items = ['child 1', 'child 2']
        title = 'test title'
        year = 2042
        director = 'test director'
        minutes = 142
        notes = 'test notes'

        with self.moviegui(monkeypatch) as cut:
            movie = [config.MovieTypedDict(title=title, year=year, director=[director],
                                           minutes=minutes, notes=notes), ]
            cut.tmdb_work_queue.put(movie)
            monkeypatch.setattr(cut, 'tmdb_treeview', mock_tmdb_treeview := MagicMock())
            mock_tmdb_treeview.get_children.return_value = items
            # This tmdb_movies item should be cleared by the function under test.
            cut.tmdb_movies['dummy'] = 'garbage'

            # test with item in queue ('else' branch executed)
            cut.tmdb_consumer()
            with check:
                cut.tmdb_treeview.get_children.assert_called_once_with()
            with check:
                cut.tmdb_treeview.delete.assert_called_once_with(*items)
            with check:
                cut.tmdb_treeview.insert.assert_called_once_with('', 'end', values=(title, year, director))
            check.equal(list(cut.tmdb_movies.values()), [dict(title=title, year=year, director=director,
                                                              minutes=minutes, notes=notes), ])

            # test with no items in queue ('else' branch not executed)
            cut.tmdb_movies['dummy'] = 'garbage'
            cut.tmdb_consumer()
            check.is_true('dummy' in cut.tmdb_movies)

            # test finally branch
            with check:
                cut.parent.after.assert_has_calls([call(cut.work_queue_poll, cut.tmdb_consumer),
                                                   call(cut.work_queue_poll, cut.tmdb_consumer),
                                                   call(cut.work_queue_poll, cut.tmdb_consumer)])

    def test_tags_treeview_callback(self, monkeypatch, movie_gui_patch):
        reselection = ('a', 'b', 'c')
        with self.moviegui(monkeypatch) as cut:
            cut.tags_treeview_callback(reselection)
        check.equal(cut.selected_tags, reselection)

    def test_tmdb_treeview_callback(self, monkeypatch, movie_gui_patch):
        dummy_item_id = 'dummy_item_id'
        dummy_entry_fields = {
            guiwidgets_2.MOVIE_FIELD_NAMES[-1]: (mock_notes := MagicMock()),
            guiwidgets_2.MOVIE_FIELD_NAMES[0]: (mock_title := MagicMock()),
            }

        with self.moviegui(monkeypatch) as cut:
            monkeypatch.setattr(cut, 'tmdb_treeview', mock_tmdb_treeview := MagicMock())
            mock_tmdb_treeview.selection.return_value = [dummy_item_id]
            monkeypatch.setattr(cut, 'notes_widget', mock_notes_widget := MagicMock())
            cut.entry_fields = dummy_entry_fields
            cut.tmdb_movies = {dummy_item_id: dummy_entry_fields}

            cut.tmdb_treeview_callback()
            with check:
                mock_notes_widget.delete.assert_called_once_with('1.0', 'end')
            with check:
                mock_notes_widget.insert.assert_called_once_with('1.0', mock_notes, ('font_tag',))
            textvariable_set = cut.entry_fields[guiwidgets_2.MOVIE_FIELD_NAMES[0]].textvariable.set
            with check:
                textvariable_set.assert_called_once_with(mock_title)

    def test_destroy(self, monkeypatch, movie_gui_patch):
        with self.moviegui(monkeypatch) as cut:
            cut.destroy()
            with check:
                cut.parent.after_cancel.assert_called_once_with(cut.recall_id)
            with check:
                cut.outer_frame.destroy.assert_called_once_with()

    def test_framing(self, monkeypatch):
        # todo
        #  Do all of these need mocks? Without an assignment they cannot be interrogated.
        #  Should they be separate fixtures?
        monkeypatch.setattr('guiwidgets_2._create_entry_fields', MagicMock())
        monkeypatch.setattr('guiwidgets_2.MovieGUI.original_values', lambda *args: None)
        monkeypatch.setattr('guiwidgets_2.MovieGUI.set_initial_tag_selection', lambda *args: None)
        monkeypatch.setattr('guiwidgets_2.MovieGUI._create_buttons', lambda *args: None)

        monkeypatch.setattr('guiwidgets_2.ttk.Frame', MagicMock())

        with self.moviegui(monkeypatch) as cut:
            with check:
                cut.outer_frame.assert_has_calls(
                    [call.grid(column=0, row=0, sticky='nsew'),
                     call.columnconfigure(0, weight=1),
                     call.columnconfigure(1, weight=1000),
                     call.rowconfigure(0),

                     call.grid(column=0, row=0, sticky='nw'),
                     call.columnconfigure(0, weight=1, minsize=25),

                     call.grid(column=1, row=0, sticky='nw'),
                     call.columnconfigure(0, weight=1, minsize=25),

                     call.grid(column=0, row=0, sticky='new'),

                     call.grid(column=0, row=1, sticky='ne')])

            check.equal(guiwidgets_2.config.current.escape_key_dict[type(cut).__name__.lower()], cut.destroy)

    @contextmanager
    def moviegui(self, monkeypatch):
        dummy_current_config = guiwidgets_2.config.CurrentConfig()
        dummy_current_config.tk_root = MagicMock(name='test tk_root')
        dummy_current_config.escape_key_dict = {}
        dummy_persistent_config = guiwidgets_2.config.PersistentConfig(TEST_TITLE, TEST_VERSION)

        monkeypatch.setattr('guiwidgets_2.config', mock_config := MagicMock(name='config'))
        mock_config.current = dummy_current_config
        mock_config.persistent = dummy_persistent_config

        # noinspection PyTypeChecker
        yield guiwidgets_2.MovieGUI(dummy_current_config.tk_root,
                                    tmdb_search_callback=MagicMock(),
                                    all_tags=['test tag 1', 'test tag 2', 'test tag 3', ])

    @pytest.fixture
    def movie_gui_patch(self, monkeypatch):
        # todo
        #  Should they be five separate fixtures?
        monkeypatch.setattr('guiwidgets_2._create_entry_fields', MagicMock())
        monkeypatch.setattr('guiwidgets_2.MovieGUI.original_values', lambda *args: None)
        monkeypatch.setattr('guiwidgets_2.MovieGUI.framing', mock_framing := MagicMock())
        mock_framing.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        monkeypatch.setattr('guiwidgets_2.MovieGUI.set_initial_tag_selection', lambda *args: None)
        monkeypatch.setattr('guiwidgets_2.MovieGUI._create_buttons', lambda *args: None)


class TestAddMovieGUI:
    """
    Test Strategy:
    """
    # todo


class TestEditMovieGUI:
    """
    Test Strategy:
    """
    # todo


class TestAddTagGUI:
    """
    Test Strategy:
    """
    # todo


class TestEditTagGUI:
    """
    Test Strategy:
    """
    # todo


class TestSearchTagGUI:
    """
    Test Strategy:
    """
    # todo


class TestSelectTagGUI:
    """
    Test Strategy:
    """
    # todo


class TestPreferencesGUI:
    """
    Test Strategy:
    """
    # todo


class TestCreateBodyAndButtonFrames:
    """
    Test Strategy:
    """
    # todo


@pytest.mark.skip('Rewrite')
class TestGUIAskYesNo:
    def test_askyesno_called(self, monkeypatch):
        # askyesno = MagicMock(name='mock_gui_askyesno')
        # monkeypatch.setattr(guiwidgets_2.messagebox, 'askyesno', askyesno)
        # parent = DummyTk()
        # message = 'dummy message'
        #
        # # noinspection PyTypeChecker
        # guiwidgets_2.gui_askyesno(parent, message)
        #
        # askyesno.assert_called_once_with(parent, message, detail='', icon='question')
        ...


class TestInputZone:
    """
    Test Strategy:
    """
    # todo
