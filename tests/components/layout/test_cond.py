import json
from typing import Any

import pytest

import pynecone as pc
from pynecone.components.layout.cond import Cond, cond
from pynecone.components.layout.fragment import Fragment
from pynecone.components.typography.text import Text
from pynecone.var import Var


@pytest.fixture
def cond_state(request):
    class CondState(pc.State):
        value: request.param["value_type"] = request.param["value"]  # noqa

    return CondState


@pytest.mark.parametrize(
    "cond_state",
    [
        pytest.param({"value_type": bool, "value": True}),
        pytest.param({"value_type": int, "value": 0}),
        pytest.param({"value_type": str, "value": "true"}),
    ],
    indirect=True,
)
def test_validate_cond(cond_state: pc.Var):
    """Test if cond can be a pc.Var with any values.

    Args:
        cond_state: A fixture.
    """
    cond_component = cond(
        cond_state.value,
        Text.create("cond is True"),
        Text.create("cond is False"),
    )

    assert str(cond_component) == (
        "<Fragment>{cond_state.value ? "
        "<Fragment><Text>{`cond is True`}</Text></Fragment> : "
        "<Fragment><Text>{`cond is False`}</Text></Fragment>}</Fragment>"
    )


@pytest.mark.parametrize(
    "c1, c2",
    [
        (True, False),
        (32, 0),
        ("hello", ""),
        (2.3, 0.0),
    ],
)
def test_prop_cond(c1: Any, c2: Any):
    """Test if cond can be a prop.

    Args:
        c1: truth condition value
        c2: false condition value
    """
    prop_cond = cond(
        True,
        c1,
        c2,
    )

    assert isinstance(prop_cond, Var)
    c1 = json.dumps(c1).replace('"', "`")
    c2 = json.dumps(c2).replace('"', "`")
    assert str(prop_cond) == f"{{true ? {c1} : {c2}}}"


def test_cond_no_else():
    """Test if cond can be used without else."""
    # Components should support the use of cond without else
    comp = cond(True, Text.create("hello"))
    assert isinstance(comp, Fragment)
    comp = comp.children[0]
    assert isinstance(comp, Cond)
    assert comp.cond == True  # noqa
    assert comp.comp1 == Fragment.create(Text.create("hello"))
    assert comp.comp2 == Fragment.create()

    # Props do not support the use of cond without else
    with pytest.raises(ValueError):
        cond(True, "hello")
