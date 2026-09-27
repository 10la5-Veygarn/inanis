# Inanis

A small Flask-based WYSIWYG document editor.

## Structure

- `app.py` - Flask application
- `document.py` - document model and filesystem operations
- `templates/` - HTML templates
- `static/` - CSS and JavaScript

## To run this:

```bash
git clone https://github.com/10la5-Veygarn/inanis.git
cd inanis
```

```bash
python -m pip install -r requirements.txt
python app.py
```

The application stores documents in:

`~/Documents/Inanis`

The `Document` class currently supports `.txt` files.
