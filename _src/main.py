from datetime import date
from pathlib import Path, PurePosixPath
from typing import Annotated

from jinja2 import Environment, FileSystemLoader
from py_markdown_table.markdown_table import markdown_table
from pydantic import BaseModel, Field, HttpUrl
from sortedcontainers_pydantic import SortedList
from yaml import safe_load

src_dir = Path(__file__).parent
data_file = src_dir / "data.yml"
env = Environment(loader=FileSystemLoader(src_dir / "templates"), autoescape=True)
template = env.get_template("README.md.jinja")


class Instance(BaseModel):
    venue: str
    date: date
    type_: Annotated[str, Field(alias="type")]
    path: HttpUrl | PurePosixPath | None = None

    def format(self):
        if self.path is None:
            return f"{self.venue} ({self.type_}, {self.date})"
        else:
            return to_hyperlink(self.venue, str(self.path)) + f" ({self.type_}, {self.date})"

    def __lt__(self, other):
        if isinstance(other, Instance):
            # Sort descending
            return self.date > other.date
        return NotImplemented


def to_hyperlink(text: str, url: str) -> str:
    return f"[{text}]({url})"


class Entry(BaseModel):
    title: str
    path: HttpUrl | PurePosixPath | None = None
    instances: SortedList[Instance]

    def to_row(self):
        if self.path is None:
            title = self.title
        else:
            title = to_hyperlink(self.title, str(self.path))
        return {
            "Title": title,
            "Instances": "<br>".join(inst.format() for inst in self.instances),
        }

    def __lt__(self, other):
        if isinstance(other, Entry):
            # Sort descending
            return self.instances[0].date > other.instances[0].date
        return NotImplemented


def main():
    with data_file.open("r") as f:
        data = [Entry.model_validate(entry) for entry in safe_load(f)]

    rows = [entry.to_row() for entry in sorted(data)]
    table = markdown_table(rows)

    rendered = template.render(table=table)

    with (src_dir.parent / "README.md").open("w") as f:
        f.write(rendered)


if __name__ == "__main__":
    main()
