import sqlite3
from flask import Flask, redirect, render_template, request, session, url_for
from flask_session import Session


app = Flask(__name__)
app.secret_key = 'blablabla'  # Replace 'your_secret_key' with an actual secret key

con = sqlite3.connect("shibi.db" ,check_same_thread=False)
cur = con.cursor()

app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# try:
#     cur.execute("CREATE TABLE users(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)")
#     con.commit()
#     print("Table created successfully.")
# except sqlite3.Error as e:
#     print(f"SQLite error: {e}")
# finally:
#     con.close()


# try:
#     cur.execute("CREATE TABLE AutoShop(id INTEGER PRIMARY KEY AUTOINCREMENT, brand TEXT , model TEXT, color TEXT, year INTEGER)")
#     con.commit()
#     print("Table created successfully.")
# except sqlite3.Error as e:
#     print(f"SQLite error: {e}")
# finally:
#     con.close()


# Helper function to check if a user is logged in
def is_logged_in():
    return 'username' in session

@app.route('/')
def hello():
    if not is_logged_in():
        return redirect(url_for('login'))
    return render_template('layout.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check the username and password against the database
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cur.fetchone()

        if user:
            session['username'] = username  # Set the user as logged in
            return redirect(url_for('hello'))
        else:
            error_message = "Invalid username or password. Please try again."
            return render_template('login.html', error_message=error_message)

    return render_template('login.html', error_message=None)

@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove the username from the session
    return redirect(url_for('login'))


@app.route('/cars')
def cars():
    cur.execute("SELECT rowid, * FROM AutoShop")
    cars = cur.fetchall()
    return render_template('cars.html', cars=cars)

@app.route('/add_car', methods=['POST', 'GET'])
def add_car():
    if request.method == 'POST' :
        brand = request.form['brand']
        model = request.form['model']
        color = request.form['color']
        year = request.form['year']

        cur.execute("INSERT INTO AutoShop (brand, model, color, year) VALUES (?, ?, ?, ?)", (brand, model, color, year))
        con.commit()
        return render_template('add_success.html') 
    return render_template('add.html')

@app.route('/delete_car/<int:car_id>', methods=['GET'])
def delete_car(car_id):
    cur.execute("SELECT rowid, * FROM AutoShop WHERE rowid=?", (car_id,))
    car = cur.fetchone()
    return render_template('delete_car.html', car=car, car_id=car_id)

@app.route('/confirm_delete/<int:car_id>', methods=['POST'])
def confirm_delete(car_id):
    cur.execute("DELETE FROM AutoShop WHERE rowid=?", (car_id,))
    con.commit()
    return redirect(url_for('cars'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username is already taken
        cur.execute("SELECT * FROM users WHERE username=?", (username,))
        existing_user = cur.fetchone()

        if existing_user:
            error_message = "Username is already taken. Please choose a different one."
            return render_template('register.html', error_message=error_message)

        # Insert the new user into the database
        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        con.commit()

        # Set a session variable to indicate the user is logged in
        session['username'] = username

        return redirect(url_for('hello'))

    return render_template('register.html', error_message=None)

# Update Car route
@app.route('/update_car/<int:car_id>', methods=['POST', 'GET'])
def update_car(car_id):
    if request.method == 'POST':
        updated_brand = request.form['brand']
        updated_model = request.form['model']
        updated_color = request.form['color']
        updated_year = request.form['year']

        cur.execute("UPDATE AutoShop SET brand=?, model=?, color=?, year=? WHERE rowid=?", 
                    (updated_brand, updated_model, updated_color, updated_year, car_id))
        con.commit()

        return redirect('/cars')  # Redirect to the cars page

    # Fetch the existing car details from the database
    cur.execute("SELECT rowid, * FROM AutoShop WHERE rowid=?", (car_id,))
    car = cur.fetchone()

    return render_template('update.html', car=car)




if __name__ == '__main__':
    app.run(debug=True)