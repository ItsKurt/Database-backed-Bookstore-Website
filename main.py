from flask import Flask, redirect, url_for, render_template, session, request, logging, flash
from connectToDB import Database
from passlib.hash import sha256_crypt
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, IntegerField, DecimalField, DateField
import operator

db = Database.getConnected()
app = Flask(__name__)
app.secret_key = "431"


@app.route("/")
def home():
    cur = db.cursor(dictionary=True, buffered=True)
    cur.execute("SELECT *, (usefulness/numRatings) as usefulnessScore FROM users WHERE awarded = True")
    awarded_users = cur.fetchall()
    cur.close()
    return render_template("home.html", users=awarded_users)

@app.route("/login", methods=["POST", "GET"])
def login():
    if 'loginName' in session:
        flash("You are already signed in. Logout first to sign in with a different account", "danger")
        return redirect(url_for('home'))
    if request.method == 'POST':
        loginName = request.form["loginName"]
        password = request.form["password"]
        cur = db.cursor(dictionary=True) #buffering=True
        cur.execute("SELECT * FROM users WHERE loginName = %s", (loginName,))
        user = cur.fetchone()
        db_password = cur.fetchone()
        if user is None:
            flash("User does not exist", "danger")
            return redirect(url_for("login"))
        if not sha256_crypt.verify(password, user['password']):
            flash("Incorrect password", "danger")
            return redirect(url_for("login"))
        session["loginName"] = request.form["loginName"]
        session["isManager"] = user['isManager']
        flash("Successfully Logged in", "success")
        return redirect(url_for("home"))
    return render_template("signIn.html")


@app.route("/logout")
def logout():
    if "loginName" not in session:
        flash("You cannot logout since you are not signed in", "danger")
        return redirect(url_for("login"))
    session.clear()
    return redirect(url_for("login"))


class RegistrationForm(Form):
    firstName = StringField('First Name', [validators.Length(min=1, max=40), validators.DataRequired()])
    lastName = StringField('Last Name', [validators.Length(min=1, max=40), validators.DataRequired()])
    address = StringField('Address', [validators.DataRequired()])
    phoneNumber = StringField('Phone Number', [validators.DataRequired()])
    loginName = StringField('Login Name', [validators.Length(min=1, max=40), validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired(), validators.EqualTo('confirm', message='Password mismatch')])
    confirm = PasswordField('Re-type Password')


@app.route("/register", methods=["POST", "GET"])
def registration():
    if 'loginName' in session:
        flash("You are already signed in. Logout first to create a new account", "danger")
        return redirect(url_for('home'))
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        firstName = form.firstName.data
        lastName = form.lastName.data
        address = form.address.data
        phoneNumber = form.phoneNumber.data
        loginName = form.loginName.data
        password = sha256_crypt.encrypt(str(form.password.data))

        cur = db.cursor()
        cur.execute("SELECT * FROM users WHERE loginName=%s", (loginName,))
        if cur.fetchone() is not None:
            flash("Login Name has already been taken. Please try another one.", "danger")
            cur.close()
            return redirect(url_for("registration"))

        cur.execute("INSERT INTO users(firstName, lastName, address, phoneNumber, loginName, password) VALUES(%s, %s, %s, %s, %s, %s)", (firstName, lastName, address, phoneNumber, loginName, password))
        db.commit()
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()
        if len(users) == 1:
            session['isManager'] = 1
        else:
            session['isManager'] = 0
        cur.close()
        session["loginName"] = request.form["loginName"]
        flash("Account successfully created. Happy Searching", "success")
        return redirect(url_for('home'))
    return render_template("register.html", form=form)


class ChangePasswordForm(Form):
    curr_password = PasswordField('Current Password:', [validators.DataRequired()])
    new_password = PasswordField('Password:', [validators.DataRequired(), validators.EqualTo('confirm', message='Password mismatch')])
    confirm = PasswordField('Re-type Password:')


@app.route('/changePassword/<string:loginName>/', methods=['GET', 'POST'])
def change_password(loginName):
    if session['loginName'] != loginName:
        flash("You cannot change another user's password", "danger")
        return redirect(request.referrer)
    form = ChangePasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        old_password = form.curr_password.data
        new_password = sha256_crypt.encrypt(str(form.new_password.data))
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE loginName = %s", (session['loginName'],))
        cPass = cur.fetchone()
        if not sha256_crypt.verify(old_password, cPass['password']):
            flash("Current password was incorrect", "danger")
            cur.close()
            return redirect(request.url)
        cur.execute('UPDATE users SET password = %s WHERE loginName = %s', (new_password, loginName))
        db.commit()
        cur.close()
        flash("Password has successfully been changed", "success")
        return redirect(url_for('profile', loginName=loginName))
    return render_template('change_password.html', form=form)




@app.route('/books', methods=["POST", "GET"])
def books():
    if "loginName" not in session:
        flash("You must be signed in to see our book selection", "danger")
        return redirect(url_for("home"))
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM books ORDER BY publicationDate DESC LIMIT 100")
    books = cur.fetchall()
    for book in books:
        cur.execute("SELECT bookRating FROM comments WHERE book = %s", (book['isbn'],))
        book_rating = 0
        ratings = cur.fetchall()
        if not ratings:
            book['rating'] = 0
        else:
            for rating in ratings:
                book_rating += rating['bookRating']
            book_rating = book_rating / len(ratings)
            book['rating'] = book_rating
    if request.method == 'POST':
        if 'search' in request.form:
            search = request.form['search'].lower()
            if request.form['search_type'] == 'publisher':
                cur.execute("SELECT * FROM books WHERE publisher LIKE %s ORDER BY publicationDate DESC", ('%' + search + '%',))
                books = cur.fetchall()
            elif request.form['search_type'] == 'title':
                cur.execute("SELECT * FROM books WHERE title LIKE %s ORDER BY publicationDate DESC", ('%'+search+'%', ))
                books = cur.fetchall()
            elif request.form['search_type'] == 'language':
                cur.execute("SELECT * FROM books WHERE language LIKE %s ORDER BY publicationDate DESC", ('%' + search + '%',))
                books = cur.fetchall()
            else:
                cur.execute("SELECT * FROM books, authors WHERE name LIKE %s AND book = isbn ORDER BY publicationDate DESC", ('%'+search+'%', ))
                books = cur.fetchall()

            for book in books:
                cur.execute("SELECT bookRating FROM comments WHERE book = %s", (book['isbn'],))
                book_rating = 0
                ratings = cur.fetchall()
                if not ratings:
                    book['rating'] = 0
                else:
                    for rating in ratings:
                        book_rating += rating['bookRating']
                    book_rating = book_rating / len(ratings)
                    book['rating'] = book_rating

            if request.form['sort'] == 'rating':
                books = sorted(books, key=lambda i: int(i['rating']), reverse=True)
                flash("Sorting by Book Rating", "success")

            elif request.form['sort'] == 'trating':
                cur.execute("SELECT * FROM comments,books, (SELECT trustee FROM trust WHERE truster = 'kmueller321') AS t WHERE creator = trustee AND book = isbn")
                t_books = cur.fetchall()
                good_books = []
                for book in books:
                    for t_book in t_books:
                        if book['isbn'] == t_book['isbn']:
                            books.remove(book)
                            good_books.append(t_book)
                            t_book['rating'] = book['rating']
                            continue
                books = sorted(good_books, key=lambda i: int(i['bookRating']), reverse=True) + books
                flash("Sorting by Trusted User Book Ratings", "success")

            else:
                flash("Sorting by Publication Date", "success")

    books = books[:100]
    cur.close()
    return render_template('books.html', books=books)


@app.route('/books/<string:isbn>/', methods=["POST", "GET"])
def book(isbn):
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM books WHERE isbn = %s", (isbn,))
    book_info = cur.fetchone()
    cur.execute("SELECT * FROM comments WHERE book = %s", (isbn,))
    comments_info = cur.fetchall()
    cur.execute("SELECT * FROM comments WHERE book = %s", (isbn,))
    book_ratings = cur.fetchall()
    book_rating = 0
    if len(book_ratings) == 0:
        book_rating = "No Ratings Yet"
    else:
        for ratings in book_ratings:
            book_rating += ratings['bookRating']
        book_rating = round((book_rating / len(book_ratings)), 2)
    cur.execute("SELECT * FROM authors WHERE book = %s", (isbn,))
    authors = cur.fetchall()
    book_authors = ', '.join([author['name'] for author in authors])
    if request.method == 'POST':
        if 'stock' in request.form:
            added_stock = request.form['stock']
            if int(added_stock) <= 0:
                flash("You cannot add zero or less books", "danger")
                cur.close()
                return redirect(url_for('book', isbn=isbn))
            cur.execute('UPDATE books SET stockLevel=stockLevel+%s WHERE isbn = %s', (added_stock, isbn))
            db.commit()
            cur.execute('DELETE FROM bookRequests WHERE book = %s', (isbn,))
            cur.close()
            flash(added_stock+' copies of this book added to the stock', 'success')
            return redirect(request.url)
        elif 'copies' in request.form:
            cur.execute('SELECT * FROM cart WHERE cart_owner = %s AND book = %s', (session['loginName'], isbn))
            duplicate = cur.fetchall()
            copies = request.form["copies"]
            if int(copies) <= 0:
                flash("You cannot order zero or less books", "danger")
                cur.close()
                return redirect(url_for('book', isbn=isbn))
            if int(copies) > book_info['stockLevel']:
                flash("Cannot order "+str(copies)+" copies of this book. Only "+str(book_info['stockLevel'])+" are in stock", "danger")
                cur.close()
                return redirect(url_for('book', isbn=isbn))
            if duplicate:
                cur.execute('UPDATE cart SET copies = copies + %s WHERE cart_owner = %s AND book = %s', (copies, session['loginName'], isbn))
            else:
                cur.execute("INSERT INTO cart(cart_owner, book, copies) VALUES(%s, %s, %s)", (session['loginName'], book_info['isbn'], copies))
            db.commit()
            cur.execute('UPDATE books SET stockLevel=stockLevel-%s WHERE isbn = %s', (copies, book_info['isbn']))
            db.commit()
            cur.close()
            flash("Book has been added to your cart.", "success")
            return redirect(url_for('book', isbn=isbn))
        else:
            for comment in comments_info:
                comment['usefulness'] = comment['useful'] + (2 * comment['v_useful'])
            comments_info = sorted(comments_info, key=lambda i: int(i['usefulness']), reverse=True)
            if not request.form['count']:
                flash("Showing all comments sorted by usefulness", "success")
            else:
                top_n = int(request.form['count'])
                if top_n <= 0:
                    flash("You must enter a positive number of top comments to see", "danger")
                    cur.close()
                    return redirect(url_for('book', isbn=isbn))
                comments_info = comments_info[:top_n]
                flash("Now showing the top "+str(top_n)+" useful comments", "success")
    cur.close()
    return render_template('book.html', book=book_info, comments=comments_info, book_rating=book_rating, book_authors=book_authors)


@app.route('/recommended_books/')
def recommended_booksn():
    flash("You must be signed in to access this feature", "danger")
    return redirect(url_for("login"))


@app.route('/recommended_books/<string:user>/')
def recommended_books(user):
    if "loginName" not in session:
        flash("You must be signed in to access this feature", "danger")
        return redirect(url_for("login"))
    if session['loginName'] != user:
        flash("You do not have access to the user's recommened books", "danger")
        return redirect(url_for('home'))
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM books INNER JOIN (SELECT DISTINCT title AS t, isbn AS book FROM books, ordercontent, (SELECT DISTINCT o2.customer FROM books, ordercontent o1, ordercontent o2 WHERE o1.book = o2.book AND o1.customer = %s AND o1.customer != o2.customer AND isbn=o1.book) AS simUsers WHERE isbn = book AND ordercontent.customer = simUsers.customer EXCEPT SELECT title, book FROM books, ordercontent WHERE customer = 'kmueller321' AND book = isbn) AS rec ON books.isbn = rec.book", (user,))
    rec_books = cur.fetchall()
    cur.close()
    return render_template('recommended_books.html', books=rec_books)


class CommentsForm(Form):
    bookRating = IntegerField('Rating (1 - 10):', [validators.NumberRange(min=0, max=10), validators.InputRequired()])
    text = TextAreaField('Text (optional):', [validators.optional()])


@app.route('/add_comment/<string:isbn>/', methods=['GET', 'POST'])
def add_comment(isbn):
    if "loginName" not in session:
        flash("You must be signed in to write a comment", "danger")
        return redirect(url_for("login"))
    cur = db.cursor()
    cur.execute('SELECT * FROM comments WHERE creator = %s AND book = %s', (session['loginName'], isbn))
    already_commented = cur.fetchone()
    if already_commented:
        flash("You already wrote a comment for this book.", "danger")
        cur.close()
        return redirect(request.referrer)
    form = CommentsForm(request.form)
    if request.method == 'POST' and form.validate():
        creator = session['loginName']
        book = isbn
        bookRating = form.bookRating.data
        c_text = form.text.data
        cur = db.cursor()
        cur.execute("INSERT INTO comments(creator, book, bookRating, c_text) VALUES(%s, %s, %s, %s)", (creator, book, bookRating, c_text))
        db.commit()
        cur.close()
        flash("Comment Successfully Created", "success")
        return redirect(url_for('book', isbn=isbn))
    return render_template('add_comment.html', form=form)


@app.route('/edit_comment/<int:commentID>/', methods=['GET', 'POST'])
def edit_comment(commentID):
    if "loginName" not in session:
        flash("You must be signed in to edit a comment", "danger")
        return redirect(url_for("login"))
    cur = db.cursor(dictionary=True)
    cur.execute('SELECT * FROM comments WHERE commentID = %s', (commentID,))
    comment = cur.fetchone()
    if session['loginName'] != comment['creator']:
        flash("You can only edit your own comments", "danger")
        return redirect(url_for('book', isbn=comment['book']))
    form = CommentsForm(request.form)
    form.bookRating.data = comment['bookRating']
    form.text.data = comment['c_text']
    print(request.method)
    if request.method == 'POST' and form.validate():
        print(request.form['bookRating'])
        bookRating = request.form['bookRating']
        c_text = request.form['text']
        cur.execute("UPDATE comments SET bookRating = %s, c_text = %s WHERE commentID = %s", (bookRating, c_text, commentID))
        db.commit()
        cur.close()
        flash("Comment Successfully Updated", "success")
        return redirect(url_for('book', isbn=comment['book']))
    return render_template('edit_comment.html', form=form)


@app.route('/delete_comment/<int:commentID>/', methods=['GET', 'POST'])
def delete_comment(commentID):
    cur = db.cursor()
    cur.execute("DELETE FROM comments WHERE commentID = %s", (commentID,))
    db.commit()
    cur.close()
    flash("Comment Successfully Deleted", "success")
    return redirect(request.referrer)


class NewBookForm(Form):
    title = StringField('Title:', [validators.DataRequired()])
    authors = StringField('Author(s) (separated by commas):', [validators.Length(min=1, max=300), validators.DataRequired()])
    subject = StringField('Subject:', [validators.Length(min=1, max=40), validators.DataRequired()])
    isbn = StringField('ISBN (#############):', [validators.Length(min=13, max=13), validators.DataRequired()])
    language = StringField('Language', [validators.Length(min=1, max=40), validators.DataRequired()])
    publisher = StringField('Publisher:', [validators.DataRequired()])
    publicationDate = DateField('Publication Date (YYYY-MM-DD):', [validators.DataRequired()])
    numPages = IntegerField('Number of Pages:', [validators.DataRequired()])
    price = DecimalField('Price:', [validators.DataRequired(), validators.NumberRange(min=0, max=1000)])


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if not session['isManager']:
        flash("You must be a manager to add a book", "danger")
        return redirect(url_for("home"))
    form = NewBookForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        authors = form.authors.data
        authors = authors.split(',')
        isbn = form.isbn.data
        subject = form.subject.data
        language = form.language.data
        publisher = form.publisher.data
        publicationDate = form.publicationDate.data
        numPages = form.numPages.data
        price = form.price.data

        cur = db.cursor()
        cur.execute("INSERT INTO books(title, isbn, subject, language, publisher, publicationDate, numPages, price) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)", (title, isbn, subject, language, publisher, publicationDate, numPages, price))
        db.commit()
        for author in authors:
            cur.execute("INSERT INTO authors(name, book) VALUES(%s, %s)", (author, isbn))
            db.commit()
        cur.close()
        flash("Book Successfully Created", "success")
        return redirect(url_for('profile', loginName=session['loginName']))
    return render_template('add_book.html', form=form)


@app.route('/c_usefulness/<int:commentID>.<string:usefulness>/')
def comment_usefulness(commentID, usefulness):
    cur = db.cursor(buffered=True)
    cur.execute('SELECT creator FROM comments WHERE commentID = %s', (commentID,))
    comment_author = cur.fetchone()[0]
    if session['loginName'] == comment_author:
        flash("You cannot rate your own comment", "danger")
        cur.close()
        return redirect(request.referrer)
    cur.execute('SELECT * FROM commentRatings WHERE user = %s AND comment = %s', (session['loginName'], commentID))
    already_rated = cur.fetchall()
    if already_rated:
        flash("You have already rated this comment", 'danger')
        cur.close()
        return redirect(request.referrer)
    if usefulness == 'useless':
        score = 0
        cur.execute('UPDATE comments SET useless = useless + 1 WHERE commentID = %s', (commentID,))
    elif usefulness == 'useful':
        score = 1
        cur.execute('UPDATE users SET usefulness = usefulness + %s', (score,))
        cur.execute('UPDATE comments SET useful = useful + 1 WHERE commentID = %s', (commentID,))
    else:
        score = 2
        cur.execute('UPDATE users SET usefulness = usefulness + %s', (score,))
        cur.execute('UPDATE comments SET v_useful = v_useful + 1 WHERE commentID = %s', (commentID,))

    cur.execute('UPDATE users SET numRatings = numRatings + 1 WHERE loginName = %s', (comment_author,))
    cur.execute('INSERT INTO commentRatings(score, comment, user) VALUES(%s, %s, %s)', (score, commentID, session['loginName']))
    db.commit()
    cur.close()
    flash("Comment has been rated", "success")
    return redirect(request.referrer)


@app.route('/requests/<string:isbn>/')
def add_book_requests(isbn):
    cur = db.cursor()
    cur.execute('SELECT * FROM bookRequests WHERE user = %s AND book = %s', (session['loginName'], isbn))
    already_requested = cur.fetchall()
    if already_requested:
        flash("You have already requested more copies of this book", "danger")
        cur.close()
        return redirect(request.referrer)
    cur.execute('INSERT INTO bookRequests (user, book) VALUES (%s, %s)', (session['loginName'], isbn))
    db.commit()
    cur.close()
    flash("Successfully submitted request. Managers will be informed", 'success')
    return redirect(request.referrer)

@app.route('/cart/')
def cart():
    flash("You must be signed in to see your shopping cart", "danger")
    return redirect(url_for('login'))


@app.route('/cart/remove_<string:isbn>/')
def cart_remove(isbn):
    cur = db.cursor(dictionary=True)
    cur.execute('SELECT * FROM cart WHERE cart_owner = %s AND book = %s', (session['loginName'], isbn))
    item = cur.fetchone()
    cur.execute('DELETE FROM cart WHERE cart_owner = %s AND book = %s', (session['loginName'], isbn))
    cur.execute('UPDATE books SET stockLevel=stockLevel+%s WHERE isbn = %s', (item['copies'], isbn))
    db.commit()
    cur.close()
    flash("Item has successfully been removed from your cart", "success")
    return redirect(url_for('shopping_cart', loginName=session['loginName']))



@app.route('/cart/<string:loginName>/')
def shopping_cart(loginName):
    if loginName != session['loginName']:
        flash("You cannot see this user's shopping cart", "danger")
        return redirect(url_for('home'))
    if "loginName" not in session:
        flash("You must be signed in to see our book selection", "danger")
        return redirect(url_for("home"))
    cur = db.cursor(dictionary=True, buffered=True)
    cur.execute("SELECT * FROM books, cart WHERE isbn = book AND cart_owner = %s", (loginName,))
    cart = cur.fetchall()
    cur.close()
    total_price = 0
    for item in cart:
        total_price += (item['price'] * item['copies'])
    return render_template('cart.html', cart=cart, total_price=total_price)


@app.route('/book_stats', methods=['GET', 'POST'])
def book_stats():
    if "loginName" not in session:
        flash("You must be signed in to see our book selection", "danger")
        return redirect(url_for("home"))
    if not session["isManager"]:
        flash("You must be a manager to access this page", "danger")
        return redirect(url_for('manager'))
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM books ORDER BY copiesSold DESC LIMIT 50")
    stats = cur.fetchall()
    category = 'books'
    if request.method == 'POST':
        category = request.form['category']
        limit = False
        if 'count' in request.form and request.form['count']:
            limit = int(request.form['count'])
        if category == 'authors':
            cur.execute("SELECT * FROM authors, books WHERE copiesSold != 0 AND book = isbn")
            sales = cur.fetchall()
            authors = {}
            for sale in sales:
                if sale['name'] not in authors:
                    authors[sale['name']] = sale['copiesSold']
                else:
                    authors[sale['name']] += sale['copiesSold']
            sorted_authors = sorted(authors.items(), key=operator.itemgetter(1), reverse=True)
            if limit:
                stats = sorted_authors[:limit]
            else:
                stats = sorted_authors
        elif category == 'publishers':
            cur.execute("SELECT * FROM books WHERE copiesSold != 0")
            sales = cur.fetchall()
            publishers = {}
            for sale in sales:
                if sale['publisher'] not in publishers:
                    publishers[sale['publisher']] = sale['copiesSold']
                else:
                    publishers[sale['publisher']] += sale['copiesSold']
            sorted_publishers = sorted(publishers.items(), key=operator.itemgetter(1), reverse=True)
            if limit:
                stats = sorted_publishers[:limit]
            else:
                stats = sorted_publishers
        else:
            if limit:
                cur.execute("SELECT * FROM books ORDER BY copiesSold DESC LIMIT %s", (limit,))
                stats = cur.fetchall()
    cur.close()
    return render_template('book_stats.html', stats=stats, category=category)


@app.route('/users', methods=['GET', 'POST'])
def users():
    if "loginName" not in session:
        flash("You must be signed in to see our book selection", "danger")
        return redirect(url_for("home"))
    if not session["isManager"]:
        flash("You must be a manager to access this page", "danger")
        return redirect(url_for('home'))
    cur = db.cursor(dictionary=True, buffered=True)
    cur.execute("SELECT * FROM users ORDER BY trustScore DESC",)
    users = cur.fetchall()

    if request.method == 'POST':
        category = request.form['category']
        limit = False
        if 'count' in request.form and request.form['count']:
            limit = int(request.form['count'])
        if category == 'trust':
            if limit:
                cur.execute("SELECT * FROM users ORDER BY trustScore DESC LIMIT %s", (limit,))
                users = cur.fetchall()
        else:
            if limit:
                cur.execute("SELECT *, (usefulness/numRatings) as usefulnessScore FROM users WHERE numRatings != 0 ORDER BY usefulnessScore DESC LIMIT %s", (limit,))
                users = cur.fetchall()
                limit -= len(users)
                cur.execute("SELECT * FROM users WHERE numRatings = 0 LIMIT %s", (limit,))
                users += cur.fetchall()
            else:
                cur.execute(
                    "SELECT *, (usefulness/numRatings) as usefulnessScore FROM users WHERE numRatings != 0 ORDER BY usefulnessScore DESC")
                users = cur.fetchall()
                cur.execute("SELECT * FROM users WHERE numRatings = 0")
                users += cur.fetchall()

    for user in users:
        if user['numRatings'] == 0:
            user['usefulness'] = 0
        else:
            user['usefulness'] = user['usefulness'] / user['numRatings']
    cur.close()
    return render_template('users.html', users=users)

@app.route('/promote/<string:loginName>/')
def promote(loginName):
    if loginName == session['loginName']:
        flash("You cannot demote yourself", "danger")
        return redirect(request.referrer)
    cur = db.cursor(dictionary=True)
    cur.execute('SELECT * FROM users WHERE loginName = %s', (loginName,))
    user = cur.fetchone()
    if user['isManager']:
        cur.execute('UPDATE users SET isManager = 0 WHERE loginName = %s', (loginName,))
        db.commit()
        cur.close()
        flash("%s %s has been successfully demoted" % (user['firstName'], user['lastName']), "success")
        return redirect(url_for('users'))
    cur.execute('UPDATE users SET isManager = 1 WHERE loginName = %s', (loginName,))
    db.commit()
    cur.close()
    flash("%s %s has been successfully promoted to manager" % (user['firstName'], user['lastName']), 'success')
    return redirect(url_for('users'))


@app.route('/award/<string:loginName>/')
def give_award(loginName):
    if loginName == session['loginName']:
        flash("You cannot give yourself an award", "danger")
        return redirect(request.referrer)
    cur = db.cursor(dictionary=True)
    cur.execute('SELECT * FROM users WHERE loginName = %s', (loginName,))
    user = cur.fetchone()
    if user['awarded']:
        flash("User has already received an award", "danger")
        return redirect(request.referrer)
    cur.execute("UPDATE users SET awarded = 1 WHERE loginName = %s", (loginName,))
    db.commit()
    cur.close()
    flash("%s %s has been successfully been awarded" % (user['firstName'], user['lastName']), 'success')
    return redirect(request.referrer)


@app.route('/order/add_<string:cart_owner>/')
def checkout(cart_owner):
    cur = db.cursor(dictionary=True, buffered=True)
    cur.execute("SELECT * FROM cart WHERE cart_owner = %s", (cart_owner,))
    full_cart = cur.fetchone()
    if not full_cart:
        flash("You must add books to your cart before checking out", "danger")
        return redirect(url_for('shopping_cart', loginName=cart_owner))
    cur.execute("INSERT INTO orders(customer) VALUES(%s)", (cart_owner,))
    orderID = cur.lastrowid
    db.commit()
    cur.execute("SELECT * FROM books, cart WHERE isbn = book AND cart_owner = %s", (cart_owner,))
    items = cur.fetchall()
    for item in items:
        cur.execute("INSERT INTO ordercontent(orderID, book, copies, customer) VALUES(%s, %s, %s, %s)", (orderID, item['isbn'], item['copies'], cart_owner))
        cur.execute("UPDATE books SET copiesSold = copiesSold + %s WHERE isbn = %s", (item['copies'], item['isbn'],))
    db.commit()
    cur.execute("SELECT * FROM cart WHERE cart_owner = %s", (cart_owner,))
    items = cur.fetchall()
    for item in items:
        cart_remove(item['book'])
    db.commit()
    cur.close()
    flash("Order Completed", "success")
    return redirect(url_for("recommended_books", user=cart_owner))


@app.route('/orders/<int:orderID>/')
def order_details(orderID):
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM books, ordercontent WHERE isbn = book AND orderID = %s", (orderID,))
    order = cur.fetchall()
    cur.close()
    total_price = 0
    for item in order:
        total_price += (item['price'] * item['copies'])
    return render_template('ordercontent.html', order=order, total_price=total_price, orderID=orderID)


@app.route('/orders/<string:loginName>/')
def order_history(loginName):
    admin = False
    if loginName == 'admin' and session['isManager']:
        admin = True
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT DISTINCT * FROM orders ORDER BY date_ordered DESC")
        orders = cur.fetchall()
    else:
        if loginName != session['loginName'] and not session['isManager']:
            flash("You do not have access to this user's order history", "danger")
            return redirect(url_for("home"))
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT DISTINCT * FROM orders WHERE customer = %s ORDER BY date_ordered DESC", (loginName,))
        orders = cur.fetchall()
    cur.close()
    return render_template('orders.html', orders=orders, admin=admin)


@app.route('/comments/<string:loginName>/')
def comment_history(loginName):
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT DISTINCT * FROM comments, books WHERE book = isbn AND creator = %s ORDER BY c_date DESC", (loginName,))
    comments = cur.fetchall()
    cur.close()
    return render_template('comments.html', comments=comments)


@app.route('/requests')
def request_history():
    if not session['isManager']:
        flash("You do not have access to the book requests", "danger")
        return redirect(url_for("home"))
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT DISTINCT * FROM bookRequests ORDER BY date_requested")
    requests = cur.fetchall()
    cur.close()
    return render_template('requests.html', requests=requests)


@app.route('/trusts/<string:truster>/')
def trusted_users(truster):
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT DISTINCT * FROM trust WHERE truster = %s ORDER BY isTrusted DESC", (truster,))
    trusts = cur.fetchall()
    cur.close()
    return render_template('trusts.html', trusts=trusts)


@app.route('/profile/')
def profile_n():
    flash("You must be signed in to access this feature", "danger")
    return redirect(url_for("login"))


@app.route('/profile/<string:loginName>/')
def profile(loginName):
    if 'loginName' not in session:
        flash("You must be signed in to access this feature", "danger")
        return redirect(url_for("login"))
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE loginName = %s", (loginName,))
    name = cur.fetchone()
    return render_template('profile.html', name=name)


@app.route('/user_info/<string:user>/')
def user_info(user):
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT *, (usefulness/numRatings) as usefulnessScore FROM users WHERE loginName = %s", (user,))
    user = cur.fetchone()
    user_info = []
    user_info.append(('Login Name:', user['loginName']))
    user_info.append(('First Name:', user['firstName']))
    user_info.append(('Last Name:', user['lastName']))
    user_info.append(('Address:', user['address']))
    user_info.append(('Phone Number:', user['phoneNumber']))
    if user['isManager']:
        user_info.append(('Role:', 'Manager'))
    else:
        user_info.append(('Role:', 'Customer'))
    if user['awarded']:
        user_info.append(('Awarded:', 'Awarded'))
    else:
        user_info.append(('Awarded:', 'Not Awarded'))
    user_info.append(('Usefulness Score:', user['usefulnessScore']))
    user_info.append(('Trust Score:', user['trustScore']))
    return render_template('user_info.html', user_info=user_info)

@app.route('/user_books/<string:user>/')
def user_books(user):
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * from books, (SELECT DISTINCT book FROM ordercontent WHERE customer = %s) AS customer WHERE isbn = book", (user,))
    books = cur.fetchall()
    cur.execute("SELECT * FROM users WHERE loginName = %s", (user,))
    name = cur.fetchone()
    cur.close()
    return render_template('user_books.html', user_books=books, name=name)


@app.route('/DOS_search', methods=['GET', 'POST'])
def dos_search():
    if 'loginName' not in session:
        flash("You must be logged in to use this feature", "danger")
        return redirect(url_for('login'))
    result = []
    if request.method == 'POST':
        author = request.form['author']
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT DISTINCT * FROM books, authors, (SELECT DISTINCT a2.NAME FROM authors a1, authors a2 WHERE a1.name = %s AND a1.name != a2.name AND a1.book = a2.book)d1 WHERE authors.name = d1.name AND authors.book = isbn LIMIT 100", (author,))
        d1_books = cur.fetchall()
        for book in d1_books:
            book['degree'] = 1
        cur.execute("SELECT * FROM books, authors, (SELECT DISTINCT authors.name FROM authors, (SELECT DISTINCT authors.book, authors.name FROM authors, (SELECT DISTINCT a2.name FROM authors a1, authors a2 WHERE a1.name = %s AND a1.name != a2.name AND a1.book = a2.book) AS d1 WHERE d1.name = authors.name) AS d2 WHERE d2.name != authors.name AND authors.book = d2.book) AS d1a WHERE d1a.name = authors.name AND authors.book = books.isbn", (author,))
        d2_books = cur.fetchall()
        for book in d2_books:
            book['degree'] = 2
        dos_books = d1_books+d2_books

        for book in dos_books:
            cur.execute("SELECT * FROM authors WHERE book = %s", (book['isbn'],))
            authors = cur.fetchall()
            book['authors'] = ', '.join([author['name'] for author in authors])
            cur.execute("SELECT bookRating FROM comments WHERE book = %s", (book['isbn'],))
            book_rating = 0
            ratings = cur.fetchall()
            if not ratings:
                book['rating'] = 0
            else:
                for rating in ratings:
                    book_rating += rating['bookRating']
                book_rating = book_rating / len(ratings)
                book['rating'] = book_rating

        isbns = []
        result = []
        for x in dos_books:
            if x['isbn'] not in isbns:
                result.append(x)
                isbns.append(x['isbn'])

        cur.close()
    return render_template('dos_search.html', dos_books=result)



@app.route('/remove_trust/<string:truster>.<string:trustee>/')
def remove_trust(truster, trustee):
    if session['loginName'] != truster:
        flash("You are not allowed to edit another user's trusted/un-trusted users", "danger")
        return(url_for('home'))
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM trust WHERE truster = %s AND trustee = %s", (truster, trustee))
    prev_trust = cur.fetchone()
    prev_trust = prev_trust['isTrusted']
    cur.execute("DELETE FROM trust WHERE truster = %s AND trustee = %s", (truster, trustee))
    db.commit()
    if prev_trust:
        cur.execute("UPDATE users SET trustScore = trustScore - 1 WHERE loginName = %s", (trustee,))
    else:
        cur.execute("UPDATE users SET trustScore = trustScore + 1 WHERE loginName = %s", (trustee,))
    db.commit()
    cur.close()
    flash(trustee+" has been removed from your trusted/un-trusted users list", "success")
    return redirect(request.referrer)


@app.route('/profile/<string:loginName>.<string:trust>/')
def trust_users(loginName, trust):
    if session['loginName'] == loginName:
        flash("You cannot mark yourself as trustewd or un-trusted", "danger")
        return redirect(request.referrer)
    cur = db.cursor(dictionary=True)
    cur.execute('SELECT * FROM trust WHERE truster = %s and trustee = %s', (session['loginName'], loginName))
    already_trusted = cur.fetchone()
    if already_trusted:
        if already_trusted['isTrusted'] and trust == 'trusted':
            flash("You already have this user marked as trusted", "danger")
            cur.close()
            return redirect(request.referrer)
        elif not already_trusted['isTrusted'] and trust == 'untrusted':
            flash("You already have this user marked as un-trusted", "danger")
            cur.close()
            return redirect(request.referrer)
        else:
            cur.execute('DELETE FROM trust WHERE truster = %s AND trustee = %s', (session['loginName'], loginName))
            db.commit()
            if trust == 'trusted':
                cur.execute('UPDATE users SET trustScore = trustScore + 1 WHERE loginName = %s', (loginName,))
                flash("User is no longer marked as un-trusted", "danger")
            else:
                cur.execute('UPDATE users SET trustScore = trustScore - 1 WHERE loginName = %s', (loginName,))
                flash("User is no longer marked as trusted", "danger")

    if trust == 'trusted':
        cur.execute('INSERT INTO trust(truster, trustee, isTrusted) VALUES(%s, %s, %s)', (session['loginName'], loginName, True))
        cur.execute('UPDATE users SET trustScore = trustScore + 1 WHERE loginName = %s', (loginName,))
        flash("User is now marked as trusted", "success")
    else:
        cur.execute('INSERT INTO trust(truster, trustee, isTrusted) VALUES(%s, %s, %s)',
                    (session['loginName'], loginName, False))
        cur.execute('UPDATE users SET trustScore = trustScore - 1 WHERE loginName = %s', (loginName,))
        flash("User is now marked as un-trusted", "success")
    db.commit()
    cur.close()
    return redirect(request.referrer)

@app.route("/manager")
def manager():
    if "loginName" not in session:
        flash("You must be signed in to access this feature", "danger")
        return redirect(url_for("login"))
    if not session["isManager"]:
        flash("You must be a manager to access this page", "danger")
        return redirect(url_for('home'))
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE loginName = %s", (session['loginName'],))
    name = cur.fetchone()
    name = name['firstName']
    return render_template('manager.html', name=name)

if __name__ == "__main__":
    app.run(debug=True)
