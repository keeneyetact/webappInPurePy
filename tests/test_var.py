import typing
from typing import Dict, List

import cloudpickle
import pytest

from pynecone.base import Base
from pynecone.state import State
from pynecone.var import BaseVar, ComputedVar, ImportVar, PCDict, PCList, Var

test_vars = [
    BaseVar(name="prop1", type_=int),
    BaseVar(name="key", type_=str),
    BaseVar(name="value", type_=str, state="state"),
    BaseVar(name="local", type_=str, state="state", is_local=True),
    BaseVar(name="local2", type_=str, is_local=True),
]

test_import_vars = [ImportVar(tag="DataGrid"), ImportVar(tag="DataGrid", alias="Grid")]


@pytest.fixture
def TestObj():
    class TestObj(Base):
        foo: int
        bar: str

    return TestObj


@pytest.fixture
def ParentState(TestObj):
    class ParentState(State):
        foo: int
        bar: int

        @ComputedVar
        def var_without_annotation(self):
            return TestObj

    return ParentState


@pytest.fixture
def ChildState(ParentState, TestObj):
    class ChildState(ParentState):
        @ComputedVar
        def var_without_annotation(self):
            return TestObj

    return ChildState


@pytest.fixture
def GrandChildState(ChildState, TestObj):
    class GrandChildState(ChildState):
        @ComputedVar
        def var_without_annotation(self):
            return TestObj

    return GrandChildState


@pytest.fixture
def StateWithAnyVar(TestObj):
    class StateWithAnyVar(State):
        @ComputedVar
        def var_without_annotation(self) -> typing.Any:
            return TestObj

    return StateWithAnyVar


@pytest.fixture
def StateWithCorrectVarAnnotation():
    class StateWithCorrectVarAnnotation(State):
        @ComputedVar
        def var_with_annotation(self) -> str:
            return "Correct annotation"

    return StateWithCorrectVarAnnotation


@pytest.fixture
def StateWithWrongVarAnnotation(TestObj):
    class StateWithWrongVarAnnotation(State):
        @ComputedVar
        def var_with_annotation(self) -> str:
            return TestObj

    return StateWithWrongVarAnnotation


@pytest.mark.parametrize(
    "prop,expected",
    zip(
        test_vars,
        [
            "prop1",
            "key",
            "state.value",
            "state.local",
            "local2",
        ],
    ),
)
def test_full_name(prop, expected):
    """Test that the full name of a var is correct.

    Args:
        prop: The var to test.
        expected: The expected full name.
    """
    assert prop.full_name == expected


@pytest.mark.parametrize(
    "prop,expected",
    zip(
        test_vars,
        ["{prop1}", "{key}", "{state.value}", "state.local", "local2"],
    ),
)
def test_str(prop, expected):
    """Test that the string representation of a var is correct.

    Args:
        prop: The var to test.
        expected: The expected string representation.
    """
    assert str(prop) == expected


@pytest.mark.parametrize(
    "prop,expected",
    [
        (BaseVar(name="p", type_=int), 0),
        (BaseVar(name="p", type_=float), 0.0),
        (BaseVar(name="p", type_=str), ""),
        (BaseVar(name="p", type_=bool), False),
        (BaseVar(name="p", type_=list), []),
        (BaseVar(name="p", type_=dict), {}),
        (BaseVar(name="p", type_=tuple), ()),
        (BaseVar(name="p", type_=set), set()),
    ],
)
def test_default_value(prop, expected):
    """Test that the default value of a var is correct.

    Args:
        prop: The var to test.
        expected: The expected default value.
    """
    assert prop.get_default_value() == expected


@pytest.mark.parametrize(
    "prop,expected",
    zip(
        test_vars,
        [
            "set_prop1",
            "set_key",
            "state.set_value",
            "state.set_local",
            "set_local2",
        ],
    ),
)
def test_get_setter(prop, expected):
    """Test that the name of the setter function of a var is correct.

    Args:
        prop: The var to test.
        expected: The expected name of the setter function.
    """
    assert prop.get_setter_name() == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        (None, None),
        (1, BaseVar(name="1", type_=int, is_local=True)),
        ("key", BaseVar(name="key", type_=str, is_local=True)),
        (3.14, BaseVar(name="3.14", type_=float, is_local=True)),
        ([1, 2, 3], BaseVar(name="[1, 2, 3]", type_=list, is_local=True)),
        (
            {"a": 1, "b": 2},
            BaseVar(name='{"a": 1, "b": 2}', type_=dict, is_local=True),
        ),
    ],
)
def test_create(value, expected):
    """Test the var create function.

    Args:
        value: The value to create a var from.
        expected: The expected name of the setter function.
    """
    prop = Var.create(value)
    if value is None:
        assert prop == expected
    else:
        assert prop.equals(expected)  # type: ignore


def test_create_type_error():
    """Test the var create function when inputs type error."""

    class ErrorType:
        pass

    value = ErrorType()

    with pytest.raises(TypeError) as exception:
        Var.create(value)

    assert (
        exception.value.args[0]
        == f"To create a Var must be Var or JSON-serializable. Got {value} of type {type(value)}."
    )


def v(value) -> Var:
    val = Var.create(value)
    assert val is not None
    return val


def test_basic_operations(TestObj):
    """Test the var operations.

    Args:
        TestObj: The test object.
    """
    assert str(v(1) == v(2)) == "{(1 === 2)}"
    assert str(v(1) != v(2)) == "{(1 !== 2)}"
    assert str(v(1) < v(2)) == "{(1 < 2)}"
    assert str(v(1) <= v(2)) == "{(1 <= 2)}"
    assert str(v(1) > v(2)) == "{(1 > 2)}"
    assert str(v(1) >= v(2)) == "{(1 >= 2)}"
    assert str(v(1) + v(2)) == "{(1 + 2)}"
    assert str(v(1) - v(2)) == "{(1 - 2)}"
    assert str(v(1) * v(2)) == "{(1 * 2)}"
    assert str(v(1) / v(2)) == "{(1 / 2)}"
    assert str(v(1) // v(2)) == "{Math.floor(1 / 2)}"
    assert str(v(1) % v(2)) == "{(1 % 2)}"
    assert str(v(1) ** v(2)) == "{Math.pow(1 , 2)}"
    assert str(v(1) & v(2)) == "{(1 && 2)}"
    assert str(v(1) | v(2)) == "{(1 || 2)}"
    assert str(v([1, 2, 3])[v(0)]) == "{[1, 2, 3].at(0)}"
    assert str(v({"a": 1, "b": 2})["a"]) == '{{"a": 1, "b": 2}["a"]}'
    assert (
        str(BaseVar(name="foo", state="state", type_=TestObj).bar) == "{state.foo.bar}"
    )
    assert str(abs(v(1))) == "{Math.abs(1)}"
    assert str(v([1, 2, 3]).length()) == "{[1, 2, 3].length}"


def test_var_indexing_lists():
    """Test that we can index into list vars."""
    lst = BaseVar(name="lst", type_=List[int])

    # Test basic indexing.
    assert str(lst[0]) == "{lst.at(0)}"
    assert str(lst[1]) == "{lst.at(1)}"

    # Test negative indexing.
    assert str(lst[-1]) == "{lst.at(-1)}"

    # Test non-integer indexing raises an error.
    with pytest.raises(TypeError):
        lst["a"]
    with pytest.raises(TypeError):
        lst[1.5]


def test_var_list_slicing():
    """Test that we can slice into list vars."""
    lst = BaseVar(name="lst", type_=List[int])

    assert str(lst[:1]) == "{lst.slice(0, 1)}"
    assert str(lst[:1]) == "{lst.slice(0, 1)}"
    assert str(lst[:]) == "{lst.slice(0, undefined)}"


def test_dict_indexing():
    """Test that we can index into dict vars."""
    dct = BaseVar(name="dct", type_=Dict[str, int])

    # Check correct indexing.
    assert str(dct["a"]) == '{dct["a"]}'
    assert str(dct["asdf"]) == '{dct["asdf"]}'


@pytest.mark.parametrize(
    "fixture,full_name",
    [
        ("ParentState", "parent_state.var_without_annotation"),
        ("ChildState", "parent_state.child_state.var_without_annotation"),
        (
            "GrandChildState",
            "parent_state.child_state.grand_child_state.var_without_annotation",
        ),
        ("StateWithAnyVar", "state_with_any_var.var_without_annotation"),
    ],
)
def test_computed_var_without_annotation_error(request, fixture, full_name):
    """Test that a type error is thrown when an attribute of a computed var is
    accessed without annotating the computed var.

    Args:
        request: Fixture Request.
        fixture: The state fixture.
        full_name: The full name of the state var.
    """
    with pytest.raises(TypeError) as err:
        state = request.getfixturevalue(fixture)
        state.var_without_annotation.foo
    assert (
        err.value.args[0]
        == f"You must provide an annotation for the state var `{full_name}`. Annotation cannot be `typing.Any`"
    )


@pytest.mark.parametrize(
    "fixture,full_name",
    [
        (
            "StateWithCorrectVarAnnotation",
            "state_with_correct_var_annotation.var_with_annotation",
        ),
        (
            "StateWithWrongVarAnnotation",
            "state_with_wrong_var_annotation.var_with_annotation",
        ),
    ],
)
def test_computed_var_with_annotation_error(request, fixture, full_name):
    """Test that an Attribute error is thrown when a non-existent attribute of an annotated computed var is
    accessed or when the wrong annotation is provided to a computed var.

    Args:
        request: Fixture Request.
        fixture: The state fixture.
        full_name: The full name of the state var.
    """
    with pytest.raises(AttributeError) as err:
        state = request.getfixturevalue(fixture)
        state.var_with_annotation.foo
    assert (
        err.value.args[0]
        == f"The State var `{full_name}` has no attribute 'foo' or may have been annotated wrongly.\n"
        f"original message: 'ComputedVar' object has no attribute 'foo'"
    )


def test_pickleable_pc_list():
    """Test that PCList is pickleable."""
    pc_list = PCList(
        original_list=[1, 2, 3], reassign_field=lambda x: x, field_name="random"
    )

    pickled_list = cloudpickle.dumps(pc_list)
    assert cloudpickle.loads(pickled_list) == pc_list


def test_pickleable_pc_dict():
    """Test that PCDict is pickleable."""
    pc_dict = PCDict(
        original_dict={1: 2, 3: 4}, reassign_field=lambda x: x, field_name="random"
    )

    pickled_dict = cloudpickle.dumps(pc_dict)
    assert cloudpickle.loads(pickled_dict) == pc_dict


@pytest.mark.parametrize(
    "import_var,expected",
    zip(
        test_import_vars,
        [
            "DataGrid",
            "DataGrid as Grid",
        ],
    ),
)
def test_import_var(import_var, expected):
    """Test that the import var name is computed correctly.

    Args:
        import_var: The import var.
        expected: expected name
    """
    assert import_var.name == expected
