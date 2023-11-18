from flask import Flask, jsonify, request, render_template, redirect, url_for, session
from flask_mysqldb import MySQL
import datetime

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
    cursor.close()
    return render_template('sports.html', sports=sports)

@app.route('/book', methods=['GET', 'POST'])
def display_sports():
    if request.method == 'POST':
        sport_id = request.form.get('sport_id')
        if sport_id:
            return redirect(url_for('display_slots', sport_id=sport_id))

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM sports")
    sports = cursor.fetchall()
    cursor.close()
    return render_template('book_sport.html', sports=sports)


@app.route('/slots/<int:sport_id>')
def display_slots(sport_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, start_time, end_time, slot_type FROM slots WHERE sport_id = %s", (sport_id,))
    slots = cursor.fetchall()
    cursor.close()
    formatted_slots = []
    for slot in slots:
        start_time = (datetime.datetime.min + slot[1]).time() 
        end_time = (datetime.datetime.min + slot[2]).time()  
        formatted_slot = {
            "id": slot[0],
            "start_time": start_time.strftime("%H:%M"), 
            "end_time": end_time.strftime("%H:%M"),
            "days": slot[3]
        }
        formatted_slots.append(formatted_slot)
    return render_template('book_slots.html', slots=formatted_slots, sport_id=sport_id)


@app.route('/book_slot', methods=['POST'])
def book_slot():
    user_id = session.get('user_id')
    slot_id = request.form.get('slot_id')
    if user_id and slot_id:
        cursor = mysql.connection.cursor()
        try:
            cursor.execute("INSERT INTO bookings (user_id, slot_id, booking_time) VALUES (%s, %s, NOW())", (user_id, slot_id))
            mysql.connection.commit()
            message = 'Booking Successful'
        except Exception as e:
            mysql.connection.rollback()
            message = 'Booking Failed: ' + str(e)
        finally:
            cursor.close()
        return render_template('booking_result.html', message=message)
    
    return "Invalid Request", 400

@app.route('/add_admin', methods=['GET','POST'])
def add_admin():
    if request.method == 'POST':
        username = request.form.get('adminUsername')
        password = request.form.get('adminPassword')
        cursor = mysql.connection.cursor()
        try:
            # Call the stored procedure
            cursor.callproc('AddAdmin', [username, password])
            mysql.connection.commit()
            message = 'Admin added successfully.'
        except Exception as e:
            mysql.connection.rollback()
            message = f'Failed to add admin: {e}'
        finally:
            cursor.close()
        return render_template('admin_feedback.html', message=message)
    return render_template('add_admin.html')

@app.route('/admin_login', methods=['GET'])
def admin_login_form():
    return render_template('admin_login.html')

@app.route('/admin_login', methods=['POST'])
def admin_login():
    username = request.form.get('adminUsername')
    password = request.form.get('adminPassword')
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM admins WHERE admin_username = %s AND admin_password = %s", (username, password))
    admin = cursor.fetchone()
    cursor.close()

    if admin:
        return redirect(url_for('admin_dashboard'))
    else:
        return "Invalid credentials", 401

@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/view_data')
def view_data():
    cursor = mysql.connection.cursor()

    cursor.callproc('GetFormattedBookings')
    formatted_bookings = cursor.fetchall()
    cursor.nextset()

    cursor.callproc('GetFormattedSlots')
    formatted_slots = cursor.fetchall()
    cursor.nextset()

    # Fetch users
    cursor.callproc('GetUsers')
    users = cursor.fetchall()
    cursor.close()
    # print(users)

    return render_template('view_data.html', bookings=formatted_bookings, slots=formatted_slots, users=users)

@app.route('/add_slot_page')
def add_slot_page():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, name FROM sports")
    sports = cursor.fetchall()
    cursor.close()

    return render_template('add_slot.html', sports=sports)

@app.route('/add_slot', methods=['POST'])
def add_slot():
    sport_id = request.form.get('sport_id')
    slot_type = request.form.get('slot_type')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    capacity = request.form.get('capacity')

    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO slots (sport_id, slot_type, start_time, end_time, capacity) VALUES (%s, %s, %s, %s, %s)", 
                   (sport_id, slot_type, start_time, end_time, capacity))
    mysql.connection.commit()
    cursor.close()

    return redirect(url_for('admin_dashboard'))  # Redirect back to the dashboard or a confirmation page


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
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
