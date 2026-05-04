def singleton(cls):
    instances = {}
    def getinstance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return getinstance

@singleton
class Memory:

    def __init__(self) -> None:
        self.scopes: list[dict] = [{}]  # index 0 is global scope

    @property
    def _current(self) -> dict:
        return self.scopes[-1]

    def push_scope(self) -> None:
        self.scopes.append({})

    def pop_scope(self) -> None:
        assert len(self.scopes) > 1, "Cannot pop global scope"
        self.scopes.pop()

    def get(self, variable_name: str) -> object:
        for scope in reversed(self.scopes):
            if variable_name in scope:
                return scope[variable_name]
        raise NameError(f"Variable '{variable_name}' is not defined")

    def set(self, variable_name: str, value: object, data_type: str) -> None:
        # No shadowing: assignment updates the variable in whichever scope already
        # owns it, so inner scopes cannot hide outer ones. If the variable is new,
        # it is created in the current (innermost) scope.
        for scope in reversed(self.scopes):
            if variable_name in scope:
                scope[variable_name] = {"value": value, "data_type": data_type}
                return
        self._current[variable_name] = {"value": value, "data_type": data_type}

    def __repr__(self) -> str:
        string = "Name\tValue\tData Type\n"
        string += "-" * 30 + "\n"
        for i, scope in enumerate(self.scopes):
            label = "global" if i == 0 else f"scope {i}"
            string += f"[{label}]\n"
            for var, data in scope.items():
                string += f"{var}\t{data['value']}\t{data['data_type']}\n"
        string += "-" * 30 + "\n"
        return string


if __name__ == "__main__":
    memory = Memory()
    memory.set(variable_name='a', value=10, data_type='int')
    memory.set(variable_name='b', value="20", data_type='string')
    print(memory)
    print(memory.get(variable_name='b'))

    memory.set(variable_name='a', value=99, data_type='int')
    print(memory.get(variable_name='a'))

    # scoped lookup
    memory.push_scope()
    memory.set(variable_name='x', value=1, data_type='int')
    print(memory.get(variable_name='a'))  # found in global scope
    memory.pop_scope()