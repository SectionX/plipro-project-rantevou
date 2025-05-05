from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, validates


class Base(DeclarativeBase): ...


class Item(Base):
    __tablename__ = "item"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    mama: Mapped[str]

    @validates("id")
    def id_validator(self, key, value):
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError as e:
                raise e

        if isinstance(value, int):
            return value

        if value is None:
            return None

    @validates("name")
    def name_validator(self, key, value):
        self.mama = "Hello"

        if isinstance(value, str):
            if value == "":
                return None
            else:
                return value

        if value is None:
            return None

    def __str__(self):
        return str(self.__dict__)


item = Item()

item.id = "1"
item.name = ""
print(item)
