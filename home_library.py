import os

from flask import *
from flask_bootstrap import Bootstrap

from book import Library, Book
from forms import EditBook

app = Flask(__name__)
app.config["SECRET_KEY"] = "blablabla"
bootstrap = Bootstrap(app)

Library.FILEPATH = os.path.join(
    os.path.dirname(__file__),
    "databases",
    "books.json"
)


def load_library():
    return Library.from_json(Library.FILEPATH)


def valid_get(obj):
    val_key = obj.get("sort_key", "id") in list(Book.DEFAULTS.keys()) + ["id"]
    val_order = obj.get("sort_order", "asc") in ["asc", "desc"]
    return val_key and val_order


def valid_post_put(obj, post=True):
    if post:
        keys = all(x in obj for x in ["title", "author"])
        default = None
    else:
        keys = True
        default = 0
    val_int = all(
        type(x) is int for x in [
            obj.get("year", default),
            obj.get("pages", default)
        ]
    )
    val_list = "genres" not in obj or len(obj.get("genres", [])) == 3
    return keys and val_int and val_list


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({
        'error': 'Not found',
        'status_code': 404
    }), 404)


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({
        'error': 'Bad request',
        'status_code': 400
    }), 400)


@app.route("/")
def index():
    return render_template("index.html")
 

@app.route("/books")
@app.route("/books/<int:id>")
def books(id=None):
    library = load_library()
    if id is not None:
        book = library.get_book(id)
        if not book:
            abort(404)
        return render_template("book.html", book=book)
    else:
        sort = request.args
        if not sort:
            return redirect("/books?sort_key=id&sort_order=asc")
        books = library.get_books(**sort)
        return render_template("books.html", books=books, args=sort)


@app.route("/edit_book/", methods=["GET", "POST"])
@app.route("/edit_book/<id>", methods=["GET", "POST"])
def edit_book(id=None):
    library = load_library()
    form = EditBook()
    if request.method == "GET":
        if id is None:
            book = Book.as_blank()
        else:
            book = library.get_book(int(id))
            if not book:
                abort(404)
        form.load_data(book)
        return render_template(
            "editbook.html", book=book,
            form=form, error=None)
    else:
        if form.validate_on_submit():
            if id == 'None':
                id = len(library.books)
            book = Book.from_dict(
                int(id), dict(request.form),
                from_request=True)
            library.update_book(int(id), book)
            library.save()
            return redirect("/books/%s" % id)
        else:
            book = Book.as_blank()
            book.id = id
            error = form.errors
            return render_template(
                "editbook.html", book=book,
                form=form, error=error)


@app.route("/delete_book/<int:id>")
def delete_book(id):
    library = load_library()
    library.remove_book(id)
    library.reorder()
    library.save()
    return redirect("/books")


@app.route("/api/v1/books", methods=["GET"])
def api_list_books():
    library = load_library()
    args = request.args
    if not args:
        args = {"sort_key": "id", "sort_order": "asc"}
    if not valid_get(args):
        abort(400)
    books = library.get_books(
        **dict(
            (k, args.get(k)) for k in args if k in ["sort_order", "sort_key"]
        )
    )
    return jsonify({
        "books": library.to_json(books),
        "sort_key": args.get("sort_key", "id"),
        "sort_order": args.get("sort_order", "asc"),
    })


@app.route("/api/v1/books/<int:id>", methods=["GET"])
def api_get_book(id):
    library = load_library()
    book = library.get_book(id)
    if not book:
        abort(404)
    return jsonify({"book": book.to_dict()})


@app.route("/api/v1/books", methods=["POST"])
def api_new_book():
    data = Library.str_to_json(request.json)
    if not data or not valid_post_put(data):
        abort(400)
    library = load_library()
    book = Book(
        len(library.books),
        **dict(
            (k, data.get(k, Book.DEFAULTS[k])) for k in Book.DEFAULTS.keys()
        )
    )
    library.add_book(book)
    library.save()
    return jsonify({'book': book.to_dict()}), 201


@app.route("/api/v1/books/<int:id>", methods=["DELETE"])
def api_delete_book(id):
    library = load_library()
    removed = library.remove_book(id)
    if not removed:
        abort(404)
    library.save()
    return jsonify({'result': removed})


@app.route("/api/v1/books/<int:id>", methods=["PUT"])
def api_update_book(id):
    data = Library.str_to_json(request.json)
    library = load_library()
    book = library.get_book(id)
    if not book:
        abort(404)
    if not data or not valid_post_put(data, post=False):
        abort(400)
    old_book_data = book.to_dict()
    updated_book = Book(
        id,
        **dict(
            (k, data.get(k, old_book_data[k])) for k in Book.DEFAULTS.keys()
        )
    )
    library.update_book(id, updated_book)
    library.save()
    return jsonify({'book': updated_book.to_dict()})

if __name__ == "__main__":
    app.run()