import datetime
import re
from pathlib import Path
from typing import ClassVar

path = Path.home() / "Documents" / "Inanis"

try:
    path.mkdir(parents=True, exist_ok=True)
except (PermissionError, OSError) as e:
    raise RuntimeError(f"Could not create document directory: {e}") from e


class Document:
    _default_location = path
    _known_extensions: ClassVar[set[str]] = {"txt"}

    def __init__(self, name=None, ext="txt"):
        if name is None:
            largest_n = self._next_doc_number()
            self.name = f"NewDoc{largest_n + 1}"
        else:
            self._validate_name(name)
            self.name = name

        if not isinstance(ext, str):
            raise TypeError("Extension must be a string.")

        ext = ext.lstrip(".").lower()
        if ext not in self._known_extensions:
            raise ValueError(f"Unsupported extension: {ext}")

        self.content = ""
        self.word_count = 0
        self._init_time = datetime.datetime.now().astimezone()
        self.ext = ext
        self._file_path = None

    @classmethod
    def _next_doc_number(cls):
        largest_n = 0
        try:
            files = cls._default_location.iterdir()
        except (PermissionError, FileNotFoundError, OSError) as e:
            raise RuntimeError(f"Could not access document directory: {e}") from e

        for file in files:
            if not file.is_file() or file.suffix.lower() != ".txt":
                continue
            match = re.fullmatch(r"NewDoc(\d+)", file.stem)
            if match:
                largest_n = max(largest_n, int(match.group(1)))
        return largest_n

    @staticmethod
    def _validate_name(name):
        if not isinstance(name, str):
            raise TypeError("Document name must be a string.")
        name = name.strip()
        if not name:
            raise ValueError("Document name cannot be empty.")
        if name in {".", ".."}:
            raise ValueError("Invalid document name.")
        if any(char in name for char in '<>:"/\\|?*'):
            raise ValueError("Document name contains invalid characters.")
        if Path(name).name != name:
            raise ValueError("Document name cannot contain a path.")

    def word_counter(self):
        if not isinstance(self.content, str):
            raise TypeError("Document content must be a string.")
        words = re.findall(r"\b\w+(?:['\-.]\w+)*\b", self.content)
        self.word_count = len(words)
        return self.word_count

    def _get_available_path(self):
        base_path = self._default_location / f"{self.name}.{self.ext}"
        if not base_path.exists():
            return base_path

        counter = 1
        while True:
            candidate = self._default_location / f"{self.name}({counter}).{self.ext}"
            if not candidate.exists():
                return candidate
            counter += 1

    def save_document(self):
        self._validate_name(self.name)
        if self.ext not in self._known_extensions:
            raise ValueError(f"Unsupported extension: {self.ext}")
        if not isinstance(self.content, str):
            raise TypeError("Document content must be a string.")

        save_path = self._get_available_path()
        try:
            with open(save_path, "wb") as file:
                file.write(self.content.encode("utf-8"))
        except (PermissionError, OSError) as e:
            raise OSError(f"Could not save document: {e}") from e

        self._file_path = save_path
        return save_path

    def overwrite(self):
        self._validate_name(self.name)
        if self.ext not in self._known_extensions:
            raise ValueError(f"Unsupported extension: {self.ext}")
        if not isinstance(self.content, str):
            raise TypeError("Document content must be a string.")

        file_path = self._file_path
        if file_path is None:
            file_path = self._default_location / f"{self.name}.{self.ext}"
        if not file_path.exists():
            raise FileNotFoundError(f"Document does not exist: {file_path.name}")

        try:
            with open(file_path, "wb") as file:
                file.write(self.content.encode("utf-8"))
        except (PermissionError, OSError) as e:
            raise OSError(f"Could not overwrite document: {e}") from e

        self._file_path = file_path
        return file_path

    def rename(self, new_name):
        self._validate_name(new_name)

        old_path = self._file_path
        if old_path is None:
            old_path = self._default_location / f"{self.name}.{self.ext}"
        if not old_path.exists():
            raise FileNotFoundError(f"Document does not exist: {old_path.name}")

        new_path = self._default_location / f"{new_name}.{self.ext}"
        if new_path.exists() and new_path != old_path:
            raise FileExistsError(
                f"A document named {new_name}.{self.ext} already exists."
            )

        try:
            old_path.rename(new_path)
        except (PermissionError, OSError) as e:
            raise OSError(f"Could not rename document: {e}") from e

        self.name = new_name
        self._file_path = new_path
        return new_path

    def delete_document(self):
        file_path = self._file_path
        if file_path is None:
            file_path = self._default_location / f"{self.name}.{self.ext}"
        if not file_path.exists():
            raise FileNotFoundError(f"Document does not exist: {file_path.name}")

        try:
            file_path.unlink()
        except (PermissionError, OSError) as e:
            raise OSError(f"Could not delete document: {e}") from e

        self._file_path = None
        return True

    def exists(self):
        file_path = self._file_path
        if file_path is None:
            file_path = self._default_location / f"{self.name}.{self.ext}"
        return file_path.exists()

    def reading_time(self):
        self.word_counter()
        return self.word_count / 200

    def to_dict(self):
        return {
            "name": self.name,
            "content": self.content,
            "word_count": self.word_count,
            "init_time": self._init_time.isoformat(),
            "ext": self.ext,
        }

    @classmethod
    def from_file(cls, filename):
        if not isinstance(filename, str):
            raise TypeError("Filename must be a string.")

        filename_path = Path(filename)
        if filename_path.name != filename or filename in {".", ".."}:
            raise ValueError("Invalid filename.")
        if filename_path.suffix.lower() != ".txt":
            raise ValueError("Unsupported file extension.")

        file_path = cls._default_location / filename
        if not file_path.is_file():
            raise FileNotFoundError(f"No such document: {filename}")

        doc = cls(name=file_path.stem, ext=file_path.suffix.lstrip("."))
        try:
            doc.content = file_path.read_text(encoding="utf-8")
        except (PermissionError, OSError, UnicodeDecodeError) as e:
            raise OSError(f"Could not read document: {e}") from e

        doc.word_counter()
        doc._file_path = file_path
        return doc

    @classmethod
    def list_documents(cls):
        try:
            files = cls._default_location.iterdir()
        except (PermissionError, FileNotFoundError, OSError) as e:
            raise RuntimeError(f"Could not access document directory: {e}") from e

        return sorted(
            [
                file.name
                for file in files
                if file.is_file() and file.suffix.lower() == ".txt"
            ],
            key=str.casefold,
        )

    def __repr__(self):
        return (
            f"Document(name={self.name!r}, ext={self.ext!r}, "
            f"word_count={self.word_count}, file_path={self._file_path!r})"
        )
