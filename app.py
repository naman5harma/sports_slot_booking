from flask import Flask, jsonify, request, render_template, redirect, url_for, session
from flask_mysqldb import MySQL

app = Flask(__name__)

app.secret_key = 'secret'

app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'mysql@12345'
app.config['MYSQL_DB'] = 'sports_booking'

mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/sports')
def list_sports():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM sports")
    sports = cursor.fetchall()
    print(sports)
    cursor.close()
    return render_template('sports.html', sports=sports)

@app.route('/slots/<int:sport_id>')
def show_slots(sport_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM slots WHERE sport_id = %s", (sport_id,))
    slots = cursor.fetchall()
    cursor.close()
    return render_template('slots.html', slots=slots, sport_id=sport_id)

@app.route('/book')
def display_sports():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM sports")
    sports = cursor.fetchall()
    cursor.close()
    return render_template('book_sport.html', sports=sports)

@app.route('/book_slot', methods=['POST'])
def book_slot():
    user_id = session.get('user_id', None)  # Ensure the user is logged in
    slot_id = request.form.get('slot_id')

    if user_id and slot_id:
        cursor = mysql.connection.cursor()
        try:
            cursor.execute("INSERT INTO bookings (user_id, slot_id, booking_time) VALUES (%s, %s, NOW())", (user_id, slot_id))
            mysql.connection.commit()
            message = 'Booking Successful'
        except Exception as e:
            mysql.connection.rollback()
            message = str(e)
        cursor.close()
    else:
        message = 'Invalid Data'

    return render_template('booking_result.html', message=message)


@app.route('/slots/<int:sport_id>')
def fetch_slots(sport_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, start_time, end_time FROM slots WHERE sport_id = %s", (sport_id,))
    slots = cursor.fetchall()
    cursor.close()
    return jsonify(slots)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  # Hash in production
        email = request.form['email']
        phone_number = request.form['phone_number']
        roll_number = request.form['roll_number']

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users (username, password, email, phone_number, roll_number) VALUES (%s, %s, %s, %s, %s)", 
                       (username, password, email, phone_number, roll_number))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        if user:
            session['logged_in'] = True
            session['user_id'] = user[0]
            return redirect(url_for('home'))
        else:
            return 'Invalid credentials'
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
