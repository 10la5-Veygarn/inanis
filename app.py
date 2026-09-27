from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from document import Document

app = Flask(__name__)
app.secret_key = "dev"  # fine for local single-user use; not for production


@app.route("/")
def index():
    try:
        documents = Document.list_documents()
    except (PermissionError, FileNotFoundError, OSError) as e:
        flash(str(e))
        documents = []

    return render_template("index.html", documents=documents)


@app.route("/new")
def new_document():
    doc = Document()
    return redirect(url_for("edit", filename=f"{doc.name}.{doc.ext}", is_new="1"))


@app.route("/edit/<filename>")
def edit(filename):
    is_new = request.args.get("is_new") == "1"

    if is_new:
        name, _, ext = filename.rpartition(".")
        doc = Document()
        doc.name = name
        doc.ext = ext
        return render_template("editor.html", doc=doc, is_new=True,
                                reading_time=0.0)

    try:
        doc = Document.from_file(filename)
    except FileNotFoundError:
        flash(f"No such document: {filename}")
        return redirect(url_for("index"))
    except (PermissionError, UnicodeDecodeError, OSError, ValueError, TypeError) as e:
        flash(str(e))
        return redirect(url_for("index"))

    return render_template("editor.html", doc=doc, is_new=False,
                            reading_time=doc.reading_time())


@app.route("/save/<filename>", methods=["POST"])
def save(filename):
    content = request.form.get("content", "")
    is_new = request.form.get("is_new") == "1"

    name, _, ext = filename.rpartition(".")
    doc = Document()
    doc.name = name
    doc.ext = ext
    doc.content = content
    doc.word_counter()

    try:
        if is_new:
            saved_path = doc.save_document()
        else:
            doc._file_path = Document._default_location / filename
            saved_path = doc.overwrite()
    except (PermissionError, OSError, FileNotFoundError, ValueError,
            TypeError, NotADirectoryError) as e:
        flash(f"Could not save: {e}")
        return redirect(url_for("edit", filename=filename,
                                 is_new="1" if is_new else None))

    flash("Saved.")
    return redirect(url_for("edit", filename=saved_path.name))


@app.route("/delete/<filename>", methods=["POST"])
def delete(filename):
    name, _, ext = filename.rpartition(".")
    doc = Document()
    doc.name = name
    doc.ext = ext
    doc._file_path = Document._default_location / filename

    try:
        doc.delete_document()
        flash(f"Deleted {filename}.")
    except FileNotFoundError:
        flash(f"No such document: {filename}")
    except (PermissionError, OSError) as e:
        flash(str(e))

    return redirect(url_for("index"))


@app.route("/rename/<filename>", methods=["POST"])
def rename(filename):
    new_name = request.form.get("new_name", "")

    name, _, ext = filename.rpartition(".")
    doc = Document()
    doc.name = name
    doc.ext = ext
    doc._file_path = Document._default_location / filename

    try:
        doc.rename(new_name)
        flash("Renamed.")
    except (ValueError, TypeError):
        flash("That name isn't valid.")
        return redirect(url_for("edit", filename=filename))
    except FileExistsError as e:
        flash(str(e))
        return redirect(url_for("edit", filename=filename))
    except (PermissionError, OSError) as e:
        flash(str(e))
        return redirect(url_for("edit", filename=filename))

    return redirect(url_for("edit", filename=f"{doc.name}.{doc.ext}"))


if __name__ == "__main__":
    app.run(debug=True)
