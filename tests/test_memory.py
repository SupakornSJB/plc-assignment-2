import pytest
from src.memory import Memory


@pytest.fixture(autouse=True)
def reset_memory():
    memory = Memory()
    memory.scopes = [{}]
    yield


# ── Basic get / set ───────────────────────────────────────────────────────────

def test_set_and_get():
    m = Memory()
    m.set("x", 10, "int")
    assert m.get("x") == {"value": 10, "data_type": "int"}


def test_get_undefined_raises():
    m = Memory()
    with pytest.raises(NameError):
        m.get("undefined")


def test_reassignment():
    m = Memory()
    m.set("x", 1, "int")
    m.set("x", 99, "int")
    assert m.get("x")["value"] == 99


def test_reassignment_different_type():
    m = Memory()
    m.set("x", 1, "int")
    m.set("x", "hello", "string")
    assert m.get("x") == {"value": "hello", "data_type": "string"}


def test_multiple_variables():
    m = Memory()
    m.set("a", 1, "int")
    m.set("b", 2.0, "float")
    m.set("c", "hi", "string")
    assert m.get("a")["value"] == 1
    assert m.get("b")["value"] == 2.0
    assert m.get("c")["value"] == "hi"


# ── Scoping ───────────────────────────────────────────────────────────────────

def test_push_scope_creates_new_scope():
    m = Memory()
    m.push_scope()
    assert len(m.scopes) == 2


def test_pop_scope_removes_scope():
    m = Memory()
    m.push_scope()
    m.pop_scope()
    assert len(m.scopes) == 1


def test_cannot_pop_global_scope():
    m = Memory()
    with pytest.raises(AssertionError):
        m.pop_scope()


def test_local_variable_not_visible_after_pop():
    m = Memory()
    m.push_scope()
    m.set("local", 42, "int")
    m.pop_scope()
    with pytest.raises(NameError):
        m.get("local")


def test_inner_scope_can_read_outer_variable():
    m = Memory()
    m.set("x", 10, "int")
    m.push_scope()
    assert m.get("x")["value"] == 10
    m.pop_scope()


def test_inner_scope_assignment_propagates_to_outer():
    # set() walks up to find the existing variable and updates it in place.
    # There is no shadowing — assignment always targets the owning scope.
    m = Memory()
    m.set("x", 10, "int")
    m.push_scope()
    m.set("x", 99, "int")   # x exists in global → updates global
    assert m.get("x")["value"] == 99
    m.pop_scope()
    assert m.get("x")["value"] == 99  # global was updated, not shadowed


def test_reassignment_updates_outer_scope():
    # Assigning to an existing variable from an inner scope updates it in place.
    m = Memory()
    m.set("x", 1, "int")
    m.push_scope()
    m.set("x", 2, "int")   # x exists in global → updates global
    m.pop_scope()
    assert m.get("x")["value"] == 2


def test_nested_scopes():
    m = Memory()
    m.set("g", 0, "int")
    m.push_scope()
    m.set("a", 1, "int")
    m.push_scope()
    m.set("b", 2, "int")
    assert m.get("g")["value"] == 0
    assert m.get("a")["value"] == 1
    assert m.get("b")["value"] == 2
    m.pop_scope()
    with pytest.raises(NameError):
        m.get("b")
    m.pop_scope()


# ── Singleton behaviour ───────────────────────────────────────────────────────

def test_singleton_same_instance():
    m1 = Memory()
    m2 = Memory()
    assert m1 is m2


def test_singleton_shared_state():
    m1 = Memory()
    m1.set("shared", True, "bool")
    m2 = Memory()
    assert m2.get("shared")["value"] is True