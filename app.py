from flask import Flask, render_template, request, session, url_for, redirect
from datetime import datetime
import base64
import hashlib
import secrets
import sqlite3
import os
import psycopg2
import psycopg2.extras

UPLOAD_FOLDER = os.path.join('static', 'uploads')

# フォルダがなければ作成する
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

HASH_ALGORITHM = "pbkdf2_sha256"

# appという名前で flaskアプリケーションを作成
app = Flask(__name__)
app.secret_key = b'opensesame'
def get_db():
    # PostgreSQLデータベースに接続
    conn = psycopg2.connect(
        host="localhost",
        database="todo.db",
        user="reiji",
        password="",  # 実際のパスワードに置き換えてください
        port=5432
    )
    return conn

def hash_password(password, salt=None, iterations=310000):
    if salt is None:
        salt = secrets.token_hex(16)
    assert salt and isinstance(salt, str) and "$" not in salt
    assert isinstance(password, str)
    pw_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations
    )
    b64_hash = base64.b64encode(pw_hash).decode("ascii").strip()
    return "{}${}${}${}".format(HASH_ALGORITHM, iterations, salt, b64_hash)


def verify_password(password, password_hash):
    if (password_hash or "").count("$") != 3:
        return False
    algorithm, iterations, salt, _ = password_hash.split("$", 3)
    iterations = int(iterations)
    assert algorithm == HASH_ALGORITHM
    compare_hash = hash_password(password, salt, iterations)
    return secrets.compare_digest(password_hash, compare_hash)

# データベースに接続
def get_db():
	db = sqlite3.connect('todo.db')
	db.row_factory = sqlite3.Row
	return db

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("index"))


@app.route("/login", methods=["GET"])
def login_form():
    return render_template("login.html")

@app.route("/login2", methods=["GET"])
def login2():
    return render_template("login2.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    if not username:
        return render_template("login.html", error_user=True, form=request.form)

    password = request.form.get("password")
    if not password:
        return render_template("login.html", error_password=True, form=request.form)

    db = get_db()
    try:
        with db:
            row = db.execute(
                "SELECT * FROM users where username = ?", (username,)
            ).fetchone()

            verified = row is not None and verify_password(
                password, row["password_hash"]
            )

            if verified:
                session["user_id"] = row["id"]
                return redirect(url_for("home2_html"))
            else:
                return render_template("login.html", error_login=True)
    finally:
        db.close()

@app.route("/register", methods=["GET"])
def register_form():
    return render_template("register.html")


@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username")
    if not username or len(username) < 3:
        return render_template("register.html", error_user=True, form=request.form)

    password = request.form.get("password")
    if not password:
        return render_template("register.html", error_password=True, form=request.form)

    password_confirmation = request.form.get("password_confirmation")
    if password != password_confirmation:
        return render_template("register.html", error_confirm=True, form=request.form)

    db = get_db()
    try:
        with db:
            res = db.execute(
                "SELECT * FROM users WHERE username = ?", (username,)
            ).fetchall()
            if len(res) != 0:
                return render_template(
                    "register.html", error_unique=True, form=request.form
                )

            password_hash = hash_password(password)
            db.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash),
            )

        return redirect(url_for("home2_html"))

    finally:
        db.close()

@app.route('/', methods=['GET'])
def index():
	query_books = """
	SELECT id,title,episord_title,main_text, create_name
	FROM books
	"""
	query_users = """
	SELECT id,username,password_hash
	FROM users
	"""
	# user_idをしゅとく
	user_id = request.args.get('user_id')
	print(user_id)

	if user_id:
		query_books += f" WHERE user_id = {user_id}"

	# データベースに接続
	db = get_db()
	with db:
		cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
		# SQL文を実行
		cursor.execute(query_books)
		# 取得したデータをtasksに格納
		books = cursor.fetchall()

		cursor.execute(query_users)
		users = cursor.fetchall()
		# データベースを閉じる
	db.close()
	# HTMLにデータを渡して表示
	return render_template('index.html', books = books, users = users)

# htmlテンプレートの定義
@app.route('/home', endpoint='home_html', methods=['GET'])
def home():
	query_books = """
	SELECT id,title,episord_title,main_text, create_name, img
	FROM books
	"""
	query_users = """
	SELECT id,username,password_hash
	FROM users
	"""
	# user_idをしゅとく
	user_id = request.args.get('user_id')
	print(user_id)

	if user_id:
		query_books += f" WHERE user_id = {user_id}"

	# データベースに接続
	db = get_db()
	with db:
		cursor = db.cursor()
		# SQL文を実行
		cursor.execute(query_books)
		# 取得したデータをtasksに格納
		books = cursor.fetchall()

		cursor.execute(query_users)
		users = cursor.fetchall()
		# データベースを閉じる
	db.close()
	# HTMLにデータを渡して表示
	return render_template('home.html', books = books, users = users)

@app.route('/home2', endpoint='home2_html', methods=['GET'])
def home2():
	query_books = """
	SELECT id,title,episord_title,main_text, create_name, img
	FROM books
	"""
	query_users = """
	SELECT id,username,password_hash
	FROM users
	"""
	# user_idをしゅとく
	user_id = request.args.get('user_id')
	print(user_id)

	if user_id:
		query_books += f" WHERE user_id = {user_id}"

	# データベースに接続
	db = get_db()
	with db:
		cursor = db.cursor()
		# SQL文を実行
		cursor.execute(query_books)
		# 取得したデータをtasksに格納
		books = cursor.fetchall()

		cursor.execute(query_users)
		users = cursor.fetchall()
		# データベースを閉じる
	db.close()
	# HTMLにデータを渡して表示
	return render_template('home2.html', books = books, users = users)

@app.route('/create', methods=['GET','POST'])
def create():
    print(request.method == 'POST')
    if request.method == 'POST':
        create_name = request.form.get('create_name')
        title = request.form.get('title')
        episord_title = request.form.get('episord_title')
        main_text = request.form.get('main_text')
        # img = request.form.get('img')
        print(request.form["create_name"])
        print(request.form["title"])
        print(request.form["episord_title"])
        print(request.form["main_text"])
        # print(request.form["img"])

        if 'img' not in request.files:
            return 'ファイルがありません（enctype指定やnameミスの可能性）', 400
        
        file = request.files['img']
        if file.filename == '':
            return 'ファイルが選択されていません', 400

        # ファイル保存
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        if title: # title == ''
            db = get_db()
            with db:
                query = """
                    INSERT INTO books (create_name, title, episord_title, main_text, create_at, img)
                    VALUES (?, ?, ?, ?, ?, ?)
                """
                db.execute(query, (create_name, title, episord_title, main_text, datetime.now(), file.filename)) # palceholderにタプルで与える
            db.commit()
            db.close()

            return redirect(url_for('home2_html'))
    
    return render_template('create.html')
	
@app.route('/book/<post_id>', methods=['GET'])
def book(post_id):
    print(post_id)
    query = """
        SELECT id, title, episord_title, main_text, create_name, img
        FROM books
        WHERE id = """ + post_id


    db = get_db()

    cursor = db.cursor()

    cursor.execute(query)

    books = []
    for row in cursor:
        book = dict(row)
        books.append(book)


    return render_template('book.html', books=books)