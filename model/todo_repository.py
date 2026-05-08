from abc import ABC, abstractmethod

from model.todo import Todo


class TodoRepository(ABC):

    @abstractmethod
    def find_all(self) -> list[Todo]: ...

    @abstractmethod
    def find_by_id(self, id: int) -> Todo | None: ...

    @abstractmethod
    def save(self, todo: Todo) -> Todo: ...

    @abstractmethod
    def update(self, todo: Todo) -> Todo: ...

    @abstractmethod
    def delete(self, id: int) -> bool: ...


class InMemoryTodoRepository(TodoRepository):

    def __init__(self) -> None:
        self._store: dict[int, Todo] = {}
        self._next_id: int = 1

    def find_all(self) -> list[Todo]:
        return list(self._store.values())

    def find_by_id(self, id: int) -> Todo | None:
        return self._store.get(id)

    def save(self, todo: Todo) -> Todo:
        todo.id = self._next_id
        self._next_id += 1
        self._store[todo.id] = todo
        return todo

    def update(self, todo: Todo) -> Todo:
        if todo.id not in self._store:
            raise KeyError(f"Todo id={todo.id} not found")
        self._store[todo.id] = todo
        return todo

    def delete(self, id: int) -> bool:
        if id not in self._store:
            return False
        del self._store[id]
        return True
