from flask import Flask, render_template, url_for, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func, between
import datetime

app = Flask(__name__)

db = SQLAlchemy()
app.config["SECRET_KEY"] = "databaseTESTY123"
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://root:''@localhost/ztbd3' 
db.init_app(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    dob = db.Column(db.Date)
    phone_number = db.Column(db.String(255))
    country = db.Column(db.String(255))

    transactions = db.relationship('Transaction', backref='user', lazy='dynamic', cascade="all, delete", passive_deletes=True)

class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    food_name = db.Column(db.String(255))

    transactions = db.relationship('Transaction', backref='food', lazy='dynamic', cascade="all, delete", passive_deletes=True)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="cascade"))
    food_id = db.Column(db.Integer, db.ForeignKey("food.id", ondelete="cascade"))
    date = db.Column(db.Date)



@app.route("/")
def main():

    """ db.create_all() """

    return render_template("base.html")


@app.route("/users/<int:page_num>")
def users(page_num):

    users = User.query.paginate(per_page=50, page= page_num, error_out=True)

    users_count = User.query.count()
    
    return render_template("users.html", users = users, users_count = users_count)

@app.route("/delete_user/<int:user_id>", methods=['GET', 'POST'])
def delete_user(user_id):

    user = User.query.get_or_404(user_id)

    db.session.delete(user)
    db.session.commit()

    return redirect(url_for('users', page_num = 1))

@app.route("/search_user", methods=['POST', 'GET'])
def search_user():

    error = None
    if request.method == 'POST':
        user_id = request.form['user_id']
        
    user = User.query.get(user_id)

    if not user:
        error = flash(f'Nie znaleziono użytkownika o id: {user_id}')
        return redirect(url_for('users',  page_num = 1, error = error))
        

    return render_template("user.html", user = user)

@app.route("/add_user", methods=['POST', 'GET'])
def add_user():

    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        dob = request.form['dob']
        phone_number = request.form['phone_number']
        country = request.form['country']

        new_user = User(first_name = first_name, last_name = last_name, dob = dob, phone_number = phone_number, country = country)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('users'))

@app.route('/edit_user/<int:user_id>', methods=['POST', 'GET'])
def edit_user(user_id):

    user = User.query.get(user_id)

    if not user:
        return redirect(url_for('users'))
    
    if request.method == 'GET':
        return render_template('edit_user.html', user=user)
    else:
        user.first_name = request.form['first_name']
        user.last_name = request.form['last_name']
        user.dob = request.form['dob']
        user.phone_number = request.form['phone_number']
        user.country = request.form['country']

        db.session.commit()

        return redirect(url_for('users', page_num=1))


@app.route("/food")
def food():


    food = Food.query.all()

    food_count = Food.query.count()

    return render_template("food.html", food = food, food_count = food_count) 

@app.route("/add_food", methods=['POST', 'GET'])
def add_food():

    if request.method == 'POST':
        food_name = request.form['food_name']
        
        new_food = Food(food_name = food_name)
        db.session.add(new_food)
        db.session.commit()

        return redirect(url_for('food'))


@app.route("/delete_food/<int:food_id>", methods=['GET', 'POST'])
def delete_food(food_id):

    food = Food.query.get_or_404(food_id)

    db.session.delete(food)
    db.session.commit()

    return redirect(url_for('food'))

@app.route("/search_food", methods=['POST', 'GET'])
def search_food():

    
    if request.method == 'POST':
        food_id = request.form['food_id']
        
    food = Food.query.get(food_id)

    if not food:
        error = f"Jedzenie o id {food_id} nie istnieje!"
        return render_template('food.html', error = error)
    
    return render_template("food.html", f = food)


@app.route('/edit_food/<int:food_id>', methods=['POST', 'GET'])
def edit_food(food_id):

    food = Food.query.get(food_id)

    if not food:
        return redirect(url_for('food'))
    
    if request.method == 'GET':
        return render_template('edit_food.html', food = food)
    else:
        food.food_name = request.form['food_name']

        db.session.commit()

        return redirect(url_for('food'))


@app.route("/transactions/<int:page_num>")
def transactions(page_num):


    trans = Transaction.query.paginate(per_page=50, page= page_num, error_out=True)

    transactions_count = Transaction.query.count()

    return render_template('transactions.html', trans = trans, transactions_count = transactions_count)

@app.route("/add_transaction", methods=['POST', 'GET'])
def add_transaction():

    error = None
    if request.method == 'POST':
        
        user_id = request.form['user_id']
        food_id = request.form['food_id']
        trans_date = request.form['trans_date']

        user = User.query.get(user_id)
        food = Food.query.get(food_id)

        if not user:
            error =  flash(f"Użytkownik o id {user_id} nie istnieje!")
            return redirect(url_for('transactions', error = error, page_num=1))
        elif not food:
            error =  flash(f"Jedzenie o id {food_id} nie istnieje!")
            return redirect(url_for('transactions', error = error, page_num=1))

        new_trans = Transaction(user_id = user_id, food_id = food_id, date = trans_date)
        db.session.add(new_trans)
        db.session.commit()

        return redirect(url_for('transactions', page_num=1))


@app.route("/delete_transaction/<int:transaction_id>", methods=['GET', 'POST'])
def delete_transaction(transaction_id):

    trans = Transaction.query.get_or_404(transaction_id)

    db.session.delete(trans)
    db.session.commit()

    return redirect(url_for('transactions'))

@app.route("/search_transaction", methods=['POST', 'GET'])
def search_transaction():

    error = None
    if request.method == 'POST':
        trans_id = request.form['trans_id']
        
    transaction = Transaction.query.get(trans_id)

    if not transaction:
        error = flash(f'Nie znaleziono traksacji o id: {trans_id}')
        return redirect(url_for('transactions', page_num=1, error=error))

    return render_template("transaction.html", transaction = transaction, page_num=1)

@app.route('/edit_transaction/<int:transaction_id>', methods=['POST', 'GET'])
def edit_transaction(transaction_id):

    trans = Transaction.query.get(transaction_id)

    if not trans:
        return redirect(url_for('transactions'))
    
    if request.method == 'GET':
        return render_template('edit_transaction.html', trans = trans)
    else:
        trans.user_id = request.form['user_id']
        trans.food_id = request.form['food_id']
        trans.date = request.form['trans_date']

        db.session.commit()

        return redirect(url_for('transactions'))


@app.route('/test_queries')
def test_queries():

    #1
    transactions = db.session.query(Transaction, User, Food).join(User, Transaction.user_id == User.id).join(Food,Transaction.food_id == Food.id).filter(User.id == 20).limit(5)

    #2
    result_date = db.session.query(Transaction, User, Food).join(User,Transaction.user_id == User.id).join(Food,Transaction.food_id == Food.id).filter(Transaction.date == '2021-04-30').limit(5)
    

    #3
    food = db.session.query(User, Food, Transaction).join(Transaction, Transaction.user_id == User.id).join(Food,Transaction.food_id == Food.id).filter(Transaction.food_id == 897).limit(5)

    #4
    between_date = db.session.query(User, Food, Transaction).join(Transaction, Transaction.user_id == User.id).join(Food,Transaction.food_id == Food.id).filter(Transaction.date.between('2020-08-08', '2020-12-22')).limit(5)

    #5
    result = db.session.query(func.avg(func.year(func.now()) - func.year(User.dob))).all()
    average_age = result[0]
    average_age = average_age[0]
    average_age = f"{average_age:.2f}"

    #6
    max_trans = db.session.query(User, func.count(Transaction.user_id).label("transactions")).join(Transaction,Transaction.user_id == User.id).group_by(User.id).order_by(func.count(Transaction.user_id).desc()).limit(5)

    #7
    max_sale = db.session.query(Food, func.count(Transaction.food_id).label("sale")).join(Transaction, Transaction.food_id == Food.id).group_by(Food.food_name).order_by(func.count(Transaction.food_id).desc()).limit(5)

    #8
  
    max_buy_by = db.session.query(User, Food, func.count(Transaction.food_id).label("sale")).join(Transaction, Transaction.food_id == Food.id).group_by(Food.food_name).order_by(func.count(Transaction.food_id).desc()).join(User, Transaction.user_id == User.id).filter(Transaction.user_id == 4).all()

    #9

    max_num_trans = db.session.query(func.count(Transaction.id).label("transactions"), Transaction.date).group_by(Transaction.date).order_by(func.count(Transaction.id).desc()).limit(5)


    return render_template('tests.html', transactions = transactions, food = food, average_age = average_age, result_date = result_date, between_date = between_date, max_trans = max_trans, max_sale = max_sale, max_num_trans = max_num_trans, max_buy_by = max_buy_by)


@app.route('/queries')
def queries():


    return render_template('queries.html')


@app.route('/query_1', methods=['POST', 'GET'])
def query_1():

    if request.method == 'POST':
        id = request.form['user_id']


    transactions = db.session.query(Transaction, User, Food).join(User, Transaction.user_id == User.id).join(Food,Transaction.food_id == Food.id).filter(User.id == id).limit(5)

    

    return render_template('query.html', transactions = transactions)

@app.route('/query_2', methods=['POST', 'GET'])
def query_2():

    if request.method == 'POST':
        date = request.form['date']

    result_date = db.session.query(Transaction, User, Food).join(User,Transaction.user_id == User.id).join(Food,Transaction.food_id == Food.id).filter(Transaction.date == date).limit(5)

    

    return render_template('query.html', result_date = result_date)


@app.route('/query_3', methods=['POST', 'GET'])
def query_3():

    if request.method == 'POST':
        id = request.form['food_id']

    food = db.session.query(User, Food, Transaction).join(Transaction, Transaction.user_id == User.id).join(Food,Transaction.food_id == Food.id).filter(Transaction.food_id == id).limit(5)


    return render_template('query.html', food = food)


@app.route('/query_4', methods=['POST', 'GET'])
def query_4():

    if request.method == 'POST':
        date_from = request.form['date_from']
        date_to = request.form['date_to']

    between_date = db.session.query(User, Food, Transaction).join(Transaction, Transaction.user_id == User.id).join(Food,Transaction.food_id == Food.id).filter(Transaction.date.between(date_from, date_to)).limit(5)


    return render_template('query.html', between_date = between_date)


@app.route('/query_5')
def query_5():

    result = db.session.query(func.avg(func.year(func.now()) - func.year(User.dob))).all()
    average_age = result[0]
    average_age = average_age[0]
    average_age = f"{average_age:.0f} lat"

    return render_template('query.html', average_age = average_age)


@app.route('/query_6')
def query_6():

    max_trans = db.session.query(User, func.count(Transaction.user_id).label("transactions")).join(Transaction,Transaction.user_id == User.id).group_by(User.id).order_by(func.count(Transaction.user_id).desc()).limit(5)

    data_chart = []
    for user, count in max_trans:
        user = f"{user.first_name} {user.last_name}"
        data_chart.append((user, count))

    

    labels = [ row[0] for row in data_chart ]
    values = [ row[1] for row in data_chart ]

    return render_template('query.html', max_trans = max_trans, labels = labels, values = values)
                           

@app.route('/query_7')
def query_7():

    max_sale = db.session.query(Food, func.count(Transaction.food_id).label("sale")).join(Transaction, Transaction.food_id == Food.id).group_by(Food.food_name).order_by(func.count(Transaction.food_id).desc()).limit(5)

    data_chart = []
    for food, count in max_sale:
        data_chart.append((food.food_name, count))

    

    labels = [ row[0] for row in data_chart ]
    values = [ row[1] for row in data_chart ]

    return render_template('query.html', max_sale = max_sale, labels= labels, values = values)



@app.route('/query_8', methods=['POST', 'GET'])
def query_8():

    if request.method == 'POST':
        id = request.form['user_id']

    max_buy_by = db.session.query(User, Food, func.count(Transaction.food_id).label("sale")).join(Transaction, Transaction.food_id == Food.id).group_by(Food.food_name).order_by(func.count(Transaction.food_id).desc()).join(User, Transaction.user_id == User.id).filter(Transaction.user_id == id).limit(5)

    for i in max_buy_by:
        print(i)

    return render_template('query.html', max_buy_by = max_buy_by)

@app.route('/query_9', methods=['POST', 'GET'])
def query_9():

    max_num_trans = db.session.query(func.count(Transaction.id).label("transactions"), Transaction.date).group_by(Transaction.date).order_by(func.count(Transaction.id).desc()).limit(10)

    data_chart = []
    for count, date in max_num_trans:
        date = f'{date.day}-{date.month}-{date.year}'
        data_chart.append((date, count))

    

    labels = [ row[0] for row in data_chart ]
    values = [ row[1] for row in data_chart ]

    return render_template('query.html', max_num_trans = max_num_trans, labels = labels, values= values)



