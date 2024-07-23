"""Test module."""

#  Copyright© 2024. Stephen Rigden.
#  Last modified 7/23/24, 3:51 AM by stephen.
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

import pytest
from pytest_check import check
from sqlalchemy import create_engine, Engine

from database_src import schema, tables
from database_src.tables import (
    sessionmaker,
    Session,
    NoResultFound,
)
from globalconstants import *

TAG_PREFIX = "test tag "
TAG_MATCH = "two"
SOUGHT_TAG = TAG_PREFIX + TAG_MATCH
TAG_TEXTS = {
    TAG_PREFIX + "one",
    SOUGHT_TAG,
    TAG_PREFIX + "three",
}
PEOPLE_PREFIX = "Test "
PERSON_MATCH = "B Bullock"
PERSON_SOUGHT = PEOPLE_PREFIX + PERSON_MATCH
PEOPLE_NAMES = {
    PEOPLE_PREFIX + "A Arnold",
    PERSON_SOUGHT,
    PEOPLE_PREFIX + "C Candlewick",
}
DIRECTORS = {"Donald Director"}
STARS = {"Edgar Ethelred", "Fanny Fullworthy"}
MOVIEBAG_1 = MovieBag(
    title="First Movie",
    year=MovieInteger("4241"),
    notes="I am MOVIEBAG_1",
)
MOVIEBAG_2 = MovieBag(
    title="Transformer",
    year=MovieInteger("4242"),
    duration=MovieInteger(142),
    directors=DIRECTORS,
    stars=STARS,
    synopsis="Synopsis for test",
    notes="I am MOVIEBAG_2",
    movie_tags=TAG_TEXTS,
)
MOVIEBAG_3 = MovieBag(
    title="Third Movie",
    duration=MovieInteger(242),
    notes="I am MOVIEBAG_3",
    year=MovieInteger("4243"),
)
MOVIEBAG_4 = MovieBag(
    title="Fourth Movie",
    notes="I am MOVIEBAG_4",
    year=MovieInteger("4244"),
)


@pytest.mark.skip("Suspended until #391 and #392 have been completed.")
def test__translate_to_moviebag(load_tags, db_session: Session):
    mb = MOVIEBAG_2
    # todo Call mb.get(<key>) not mb[<'key'>]
    movie = schema.Movie(
        title=mb["title"],
        year=int(mb["year"]),
        duration=int(mb["duration"]),
        directors={schema.Person(name=name) for name in mb["directors"]},
        stars={schema.Person(name=name) for name in mb["stars"]},
        synopsis=mb["synopsis"],
        notes=mb["notes"],
        # todo: Can't do this - These already entered names have unique constraint
        tags={schema.Tag(text=text) for text in mb["movie_tags"]},
    )
    # todo Add the movie to get the id and datestamps

    movie_bag = tables._translate_to_moviebag(db_session, movie=movie)

    assert movie_bag == MOVIEBAG_2
    # todo Test id and datestamps
    assert False


# def test__select_movie(load_movies, db_session: Session):
#     title = MOVIEBAG_2["title"]
#     year = int(MOVIEBAG_2["year"])
#
#     movie = tables._select_movie(db_session, title=title, year=year)
#
#     check.equal(movie.title, title)
#     check.equal(movie.year, year)


def test__select_person(load_people, db_session: Session):
    person = tables._select_person(db_session, match=PERSON_SOUGHT)

    assert person.name == PERSON_SOUGHT


def test__match_people(load_people, db_session: Session):
    people = tables._match_people(db_session, match=PEOPLE_PREFIX)

    names = {person.name for person in people}
    assert names == PEOPLE_NAMES


def test__add_person(load_people, db_session: Session):
    new_person_name = "Test D Dougal"
    tables._add_person(db_session, name=new_person_name)

    person = tables._select_person(db_session, match=new_person_name)
    assert person.name == new_person_name


def test__delete_person(load_people, db_session: Session):
    person = tables._select_person(db_session, match=PERSON_MATCH)

    tables._delete_person(db_session, person=person)

    with pytest.raises(NoResultFound):
        tables._select_person(db_session, match=PERSON_MATCH)


@pytest.mark.skip("Suspended until #391 and #392 have been completed.")
def test__delete_orphans(load_people, db_session: Session):
    # todo Write test
    #   Setup needs a data structure where some people are attached to a Movie
    #   so _add_movie must be written first.
    pass


def test__select_tag(load_tags, db_session: Session):
    tag = tables._match_tag(db_session, match=TAG_MATCH)

    assert tag.text == SOUGHT_TAG


def test__select_all_tags(load_tags, db_session: Session):
    tags = tables._select_all_tags(db_session)
    texts = {tag.text for tag in tags}

    assert texts == TAG_TEXTS


def test__add_tag(load_tags, db_session: Session):
    new_tag = "test add tag garbage garbage"
    tables._add_tag(db_session, tag_text=new_tag)

    # 'load_tags' loads three 'test tag […]'s. This is 'test add tag'.
    tag = tables._match_tag(db_session, match=new_tag[:12])
    assert tag.text == new_tag


def test__add_tags(load_tags, db_session: Session):
    new_tag = "test add tag garbage garbage"
    tables._add_tags(db_session, tag_texts=[new_tag])

    # 'load_tags' loads three 'test tag […]'s. This is 'test add tag'.
    tag = tables._match_tag(db_session, match=new_tag[:12])
    assert tag.text == new_tag


def test__edit_tag(load_tags, db_session: Session):
    replacement_text = "test edited tag"
    tag = tables._match_tag(db_session, match=SOUGHT_TAG)

    tables._edit_tag(tag=tag, replacement_text=replacement_text)

    tag = tables._match_tag(db_session, match=replacement_text)
    assert tag.text == replacement_text


def test__delete_tag(load_tags, db_session: Session):
    tag = tables._match_tag(db_session, match=SOUGHT_TAG)

    tables._delete_tag(db_session, tag=tag)

    with check.raises(NoResultFound):
        tables._match_tag(db_session, match=SOUGHT_TAG)


@pytest.fixture(scope="session")
def session_engine():
    """Yields an engine."""
    engine: Engine = create_engine("sqlite+pysqlite:///:memory:")
    schema.Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def session_factory(session_engine: Engine) -> sessionmaker[Session]:
    """Returns a session factory.

    Args:
        session_engine:

    Returns:
        A session factory
    """
    return sessionmaker(session_engine)


@pytest.fixture(scope="function")
def db_session(session_factory: sessionmaker[Session]):
    """Yields a database connection.

    Args:
        session_factory:
    """
    session: Session = session_factory()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def load_tags(db_session: Session):
    """Add test tags to the database.

    Args:
        db_session:
    """
    db_session.add_all([schema.Tag(text=text) for text in TAG_TEXTS])


@pytest.fixture(scope="function")
def load_people(db_session: Session):
    """Add test people to the database.

    Args:
        db_session:
    """
    db_session.add_all([schema.Person(name=name) for name in PEOPLE_NAMES])
