from dataclasses import dataclass


@dataclass
class Todo:
    id: int
    title: str
    done: bool = False

    def __post_init__(self) -> None:
        if self.id < 0:
            raise ValueError("id must be non-negative")
        if not self.title or not self.title.strip():
            raise ValueError("title must not be blank")
