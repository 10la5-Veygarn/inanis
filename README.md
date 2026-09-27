# Inanis

A small Flask-based WYSIWYG document editor.

While brainstorming ideas for the CS50P final project, I thought of many different projects, but I ultimately decided to build this simple editor both to convince myself to write something (code and otherwise) and as a simple project which I can build upon. I have some experience with Flask, so I decided to make it web-based first. I might update it to use a more modern front-end framework in the future, but that depends on how lazy I feel.

## Structure

- `app.py` - Flask application
- `document.py` - document model and filesystem operations
- `templates/` - HTML templates
- `static/` - CSS and JavaScript

The editor has a pretty simple framework, which revolves around a few core functions. The `document.py` file contains the 'Document' class, which is the basic document model and contains the filesystem operations. The main functions are:

- `from_file()` - opens a document from the default directory, reads its properties, and initializes a document object based on the file name and content.
- `save_document()` - saves the document to the default directory. It checks for file existence, name availability and OS permissions. It also validates the name and content before saving. The default encoding is UTF-8 (not changeable for now).
- `delete_document()` - deletes the document from the default directory. It first gets the file path from the name, checks for errors, and then deletes the file.
- `rename()` - renames the document to a new name. It first gets the file path from the old name, validates the new name, checks for errors, and then renames the file. It also adjusts the document object's properties to reflect the new name and file path.
- `from_file()` - creates a document object from a file on the filesystem. It reads the file, validates the name and content, and initializes a document object with the file path and content.
- `list_documents()` - lists all documents in the default directory.
- A bunch of other functions like `word_counter()`, `overwrite()`, `reading_time()`, `exists()` etc.

`document.py` works with no dependencies required other than the standard-library modules which come bundled with python by default - datetime, pathlib, typing and re. It does however, require OS level permissions to access the filesystem, create directories, and read/write files. In terms of error handling, it raises exceptions for any errors that occur during file operations and passes them on to Flask, where they are shown to the user before being handled with fallbacks.

---

The `app.py` file is the main Flask application file, which contains the routes and logic for the web interface. It works with the `document.py` file to handle document operations and serves the HTML templates and static files. It contains both path-based and method-based routing. The main functions are:

- `new_document()` - creates a new document object in memory and redirects to /edit/<filename>?is_new=1. (Note: This is a bit of a fragile system since the file is not saved to the filesystem till you click save. You might lose data if you close the port or the browser page before saving.)
- `edit()` - serves the edit page for a document. If the document is new (like above), it will initialize the document object and redirect to /edit/<filename>. If not, it will read the document properties and pass them to the document object. This also initializes reading_time().
- `save_document()` - saves the document to the filesystem. This is a POST request. It first gets the args from the request, then either saves the new document or overwrites the existing one with new content.
- `delete_document()` - deletes a document from the filesystem. This is also a POST request. It gets the various details from the document object, tracks down the file, and deletes it.
- `rename_document()` - renames a document on the filesystem. This is also a POST request. It gets the new name from the request and renames the file.

Most of the error handling happens in `app.py` because it inherits a lot of errors from `document.py` and also raises a few of its own. In all cases, the error message is either passed to the user in a comprehensible format (for weird errors) or as a string of the error directly. There are redirects after every function, which either lead to the base URL, which is sort of the home screen, or the edit page of the document. All of these functions, except for the home page, work on the basis of similarly named functions in `document.py` for simplicity. There is also a secret key for the app for Flask, which is not very secure but should be fine for local use (on private devices, obviously), but not really on a public device, or for production. That said, I don't plan on exposing any ports with this, so it should be fine. Probably. Maybe.

The `templates/` and `static/` directories contain the HTML templates and CSS/JavaScript files, respectively. I won't elaborate much on them, as they're pretty simple and also because this is a final project for a Python course. Suffice to say that the HTML files are the base, the CSS files provide styling, and JavaScript files provide interactivity.

## Current features and supported file types

The application stores documents in:

`~/Documents/Inanis`

The `Document` class currently supports `.txt` files.

## Prerequisites

- Python 3+
- Flask
- Git
- A terminal or command prompt

## To run this

### Linux

```bash
git clone https://github.com/10la5-Veygarn/inanis.git
cd inanis
```

```bash
python3 -m pip install -r requirements.txt
python3 app.py
```

### macOS

```bash
git clone https://github.com/10la5-Veygarn/inanis.git
cd inanis
```

```bash
python3 -m pip install -r requirements.txt
python3 app.py
```

### Windows

```powershell
git clone https://github.com/10la5-Veygarn/inanis.git
cd inanis
```

```powershell
python -m pip install -r requirements.txt
python app.py
```
