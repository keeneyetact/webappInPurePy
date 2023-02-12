import os.path
from typing import List, Tuple, Type

import pytest

from pynecone.app import App, DefaultState
from pynecone.components import Box
from pynecone.event import Event
from pynecone.middleware import HydrateMiddleware
from pynecone.state import State
from pynecone.style import Style


@pytest.fixture
def app() -> App:
    """A base app.

    Returns:
        The app.
    """
    return App()


@pytest.fixture
def index_page():
    """An index page.

    Returns:
        The index page.
    """

    def index():
        return Box.create("Index")

    return index


@pytest.fixture
def about_page():
    """An about page.

    Returns:
        The about page.
    """

    def about():
        return Box.create("About")

    return about


@pytest.fixture()
def TestState() -> Type[State]:
    """A default state.

    Returns:
        A default state.
    """

    class TestState(State):
        var: int

    return TestState


def test_default_app(app: App):
    """Test creating an app with no args.

    Args:
        app: The app to test.
    """
    assert app.state() == DefaultState()
    assert app.middleware == [HydrateMiddleware()]
    assert app.style == Style()


def test_add_page_default_route(app: App, index_page, about_page):
    """Test adding a page to an app.

    Args:
        app: The app to test.
        index_page: The index page.
        about_page: The about page.
    """
    assert app.pages == {}
    app.add_page(index_page)
    assert set(app.pages.keys()) == {"index"}
    app.add_page(about_page)
    assert set(app.pages.keys()) == {"index", "about"}


def test_add_page_set_route(app: App, index_page, windows_platform: bool):
    """Test adding a page to an app.

    Args:
        app: The app to test.
        index_page: The index page.
        windows_platform: Whether the system is windows.
    """
    route = "test" if windows_platform else "/test"
    assert app.pages == {}
    app.add_page(index_page, route=route)
    assert set(app.pages.keys()) == {"test"}


def test_add_page_set_route_nested(app: App, index_page, windows_platform: bool):
    """Test adding a page to an app.

    Args:
        app: The app to test.
        index_page: The index page.
        windows_platform: Whether the system is windows.
    """
    route = "test\\nested" if windows_platform else "/test/nested"
    assert app.pages == {}
    app.add_page(index_page, route=route)
    assert set(app.pages.keys()) == {route.strip(os.path.sep)}


def test_initialize_with_state(TestState: Type[State]):
    """Test setting the state of an app.

    Args:
        TestState: The default state.
    """
    app = App(state=TestState)
    assert app.state == TestState

    # Get a state for a given token.
    token = "token"
    state = app.state_manager.get_state(token)
    assert isinstance(state, TestState)
    assert state.var == 0  # type: ignore


def test_set_and_get_state(TestState: Type[State]):
    """Test setting and getting the state of an app with different tokens.

    Args:
        TestState: The default state.
    """
    app = App(state=TestState)

    # Create two tokens.
    token1 = "token1"
    token2 = "token2"

    # Get the default state for each token.
    state1 = app.state_manager.get_state(token1)
    state2 = app.state_manager.get_state(token2)
    assert state1.var == 0  # type: ignore
    assert state2.var == 0  # type: ignore

    # Set the vars to different values.
    state1.var = 1
    state2.var = 2
    app.state_manager.set_state(token1, state1)
    app.state_manager.set_state(token2, state2)

    # Get the states again and check the values.
    state1 = app.state_manager.get_state(token1)
    state2 = app.state_manager.get_state(token2)
    assert state1.var == 1  # type: ignore
    assert state2.var == 2  # type: ignore


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "event_tuples",
    [
        pytest.param(
            [
                (
                    "test_state.make_friend",
                    {"test_state": {"plain_friends": ["Tommy", "another-fd"]}},
                ),
                (
                    "test_state.change_first_friend",
                    {"test_state": {"plain_friends": ["Jenny", "another-fd"]}},
                ),
            ],
            id="append then __setitem__",
        ),
        pytest.param(
            [
                (
                    "test_state.unfriend_first_friend",
                    {"test_state": {"plain_friends": []}},
                ),
                (
                    "test_state.make_friend",
                    {"test_state": {"plain_friends": ["another-fd"]}},
                ),
            ],
            id="delitem then append",
        ),
        pytest.param(
            [
                (
                    "test_state.make_friends_with_colleagues",
                    {"test_state": {"plain_friends": ["Tommy", "Peter", "Jimmy"]}},
                ),
                (
                    "test_state.remove_tommy",
                    {"test_state": {"plain_friends": ["Peter", "Jimmy"]}},
                ),
                (
                    "test_state.remove_last_friend",
                    {"test_state": {"plain_friends": ["Peter"]}},
                ),
                (
                    "test_state.unfriend_all_friends",
                    {"test_state": {"plain_friends": []}},
                ),
            ],
            id="extend, remove, pop, clear",
        ),
        pytest.param(
            [
                (
                    "test_state.add_jimmy_to_second_group",
                    {
                        "test_state": {
                            "friends_in_nested_list": [["Tommy"], ["Jenny", "Jimmy"]]
                        }
                    },
                ),
                (
                    "test_state.remove_first_person_from_first_group",
                    {
                        "test_state": {
                            "friends_in_nested_list": [[], ["Jenny", "Jimmy"]]
                        }
                    },
                ),
                (
                    "test_state.remove_first_group",
                    {"test_state": {"friends_in_nested_list": [["Jenny", "Jimmy"]]}},
                ),
            ],
            id="nested list",
        ),
        pytest.param(
            [
                (
                    "test_state.add_jimmy_to_tommy_friends",
                    {"test_state": {"friends_in_dict": {"Tommy": ["Jenny", "Jimmy"]}}},
                ),
                (
                    "test_state.remove_jenny_from_tommy",
                    {"test_state": {"friends_in_dict": {"Tommy": ["Jimmy"]}}},
                ),
                (
                    "test_state.tommy_has_no_fds",
                    {"test_state": {"friends_in_dict": {"Tommy": []}}},
                ),
            ],
            id="list in dict",
        ),
    ],
)
async def test_list_mutation_detection__plain_list(
    event_tuples: List[Tuple[str, List[str]]], list_mutation_state: State
):
    """Test list mutation detection
    when reassignment is not explicitly included in the logic.

    Args:
        event_tuples: From parametrization.
        list_mutation_state: A state with list mutation features.
    """
    for event_name, expected_delta in event_tuples:
        result = await list_mutation_state.process(
            Event(
                token="fake-token",
                name=event_name,
                router_data={"pathname": "/", "query": {}},
                payload={},
            )
        )

        assert result.delta == expected_delta


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "event_tuples",
    [
        pytest.param(
            [
                (
                    "test_state.add_age",
                    {"test_state": {"details": {"name": "Tommy", "age": 20}}},
                ),
                (
                    "test_state.change_name",
                    {"test_state": {"details": {"name": "Jenny", "age": 20}}},
                ),
                (
                    "test_state.remove_last_detail",
                    {"test_state": {"details": {"name": "Jenny"}}},
                ),
            ],
            id="update then __setitem__",
        ),
        pytest.param(
            [
                (
                    "test_state.clear_details",
                    {"test_state": {"details": {}}},
                ),
                (
                    "test_state.add_age",
                    {"test_state": {"details": {"age": 20}}},
                ),
            ],
            id="delitem then update",
        ),
        pytest.param(
            [
                (
                    "test_state.add_age",
                    {"test_state": {"details": {"name": "Tommy", "age": 20}}},
                ),
                (
                    "test_state.remove_name",
                    {"test_state": {"details": {"age": 20}}},
                ),
                (
                    "test_state.pop_out_age",
                    {"test_state": {"details": {}}},
                ),
            ],
            id="add, remove, pop",
        ),
        pytest.param(
            [
                (
                    "test_state.remove_home_address",
                    {"test_state": {"address": [{}, {"work": "work address"}]}},
                ),
                (
                    "test_state.add_street_to_home_address",
                    {
                        "test_state": {
                            "address": [
                                {"street": "street address"},
                                {"work": "work address"},
                            ]
                        }
                    },
                ),
            ],
            id="dict in list",
        ),
        pytest.param(
            [
                (
                    "test_state.change_friend_name",
                    {
                        "test_state": {
                            "friend_in_nested_dict": {
                                "name": "Nikhil",
                                "friend": {"name": "Tommy"},
                            }
                        }
                    },
                ),
                (
                    "test_state.add_friend_age",
                    {
                        "test_state": {
                            "friend_in_nested_dict": {
                                "name": "Nikhil",
                                "friend": {"name": "Tommy", "age": 30},
                            }
                        }
                    },
                ),
                (
                    "test_state.remove_friend",
                    {"test_state": {"friend_in_nested_dict": {"name": "Nikhil"}}},
                ),
            ],
            id="nested dict",
        ),
    ],
)
async def test_dict_mutation_detection__plain_list(
    event_tuples: List[Tuple[str, List[str]]], dict_mutation_state: State
):
    """Test dict mutation detection
    when reassignment is not explicitly included in the logic.

    Args:
        event_tuples: From parametrization.
        dict_mutation_state: A state with dict mutation features.
    """
    for event_name, expected_delta in event_tuples:
        result = await dict_mutation_state.process(
            Event(
                token="fake-token",
                name=event_name,
                router_data={"pathname": "/", "query": {}},
                payload={},
            )
        )

        assert result.delta == expected_delta
