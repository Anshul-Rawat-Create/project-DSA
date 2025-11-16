# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, User, MenuItem, Order, Reservation
from c_wrapper import enqueue_order, set_order_status, calculate_total_bill, schedule_reservation,lib
from utils import is_premium_time_slot, current_timestamp
import json
import os
from datetime import datetime,date


app = Flask(__name__)
app.secret_key = 'tabletrack_2025_secure_key'

# Get absolute path to data folder
project_root = os.path.dirname(os.path.dirname(__file__))  # Go up two levels: backend → Table-Track
db_path = os.path.join(project_root, 'data', 'tabletrack.db')

# Use absolute path for SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Create tables on first run
with app.app_context():
    db.create_all()
    # Add sample menu if empty
    if MenuItem.query.count() == 0:
        items = [
            MenuItem(name="Paneer Butter Masala", description="Creamy curry with cottage cheese", price=220),
            MenuItem(name="Butter Naan", description="Soft leavened bread", price=40),
            MenuItem(name="Veg Biryani", description="Fragrant rice with vegetables", price=180),
            MenuItem(name="Masala Dosa", description="Crispy rice crepe with potato", price=120)
        ]
        for item in items:
            db.session.add(item)
        db.session.commit()

# --- Helper: Login Required ---
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_email'] = user.email
            session['is_vip'] = user.is_vip
            return redirect(url_for('home'))
        flash("Invalid email or password.")
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form.get('phone', '')
        password = request.form['password']
        confirm = request.form['confirm_password']
        
        if password != confirm:
            flash("Passwords do not match.")
        elif User.query.filter_by(email=email).first():
            flash("Email already registered.")
        else:
            user = User(name=name, email=email, phone=phone)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash("Account created! Please log in.")
            return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/home')
@login_required
def home():
    return render_template('home.html')

@app.route('/user-account')
@login_required
def user_account():
    user = User.query.filter_by(email=session['user_email']).first()
    if not user:
        return redirect(url_for('login'))
    
    vip_fee = lib.get_vip_upgrade_fee()
    
    return render_template('user-account.html', user=user, vip_fee=vip_fee)

@app.route('/current-bookings')
@login_required
def current_bookings():
    user_email = session['user_email']
    today = date.today().isoformat()
    now_time = datetime.now().strftime("%H:%M")
    bookings = Reservation.query.filter(
        Reservation.user_email == user_email,
        (Reservation.date > today) |
        ((Reservation.date == today) & (Reservation.time >= now_time))
    ).order_by(Reservation.date, Reservation.time).all()
    return render_template('current-bookings.html', bookings=bookings)

@app.route('/booking-history')
@login_required
def booking_history():
    user_email = session['user_email']
    today = date.today().isoformat()
    now_time = datetime.now().strftime("%H:%M")
    bookings = Reservation.query.filter(
        Reservation.user_email == user_email,
        (Reservation.date < today) |
        ((Reservation.date == today) & (Reservation.time < now_time))
    ).order_by(Reservation.date.desc(), Reservation.time.desc()).all()
    return render_template('booking-history.html', bookings=bookings)

@app.route('/cancel-booking/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = Reservation.query.filter_by(id=booking_id, user_email=session['user_email']).first()
    if booking:
        db.session.delete(booking)
        db.session.commit()
        flash("✅ Your table booking has been cancelled.")
    return redirect(url_for('current_bookings'))


@app.route('/book-table', methods=['GET', 'POST'])
@login_required
def book_table():
    from datetime import date
    if request.method == 'POST':
        booking_date = request.form['date']
        booking_time = request.form['time']
        
        is_premium = is_premium_time_slot(booking_time)
        fee = lib.get_table_reservation_fee(int(is_premium))  # ← Get fee from C module

        # Prepare metadata to pass through payment
        metadata = json.dumps({
            "date": booking_date,
            "time": booking_time,
            "is_premium": is_premium
        })

        if fee > 0:
            # Redirect to payment page
            return redirect(url_for('payment_page',
                amount=fee,
                description=f"Table Reservation on {booking_date} at {booking_time}",
                next_action='confirm_booking',
                metadata=metadata
            ))
        else:
            # Free booking: create directly
            reservation = Reservation(
                user_email=session['user_email'],
                date=booking_date,
                time=booking_time,
                is_premium_slot=is_premium
            )
            db.session.add(reservation)
            db.session.commit()
            schedule_reservation(reservation.id, current_timestamp())
            flash(f"✅ Table reserved for {booking_date} at {booking_time}!")
            return redirect(url_for('home'))
    
    return render_template('book-table.html', min_date=date.today().isoformat())

@app.route('/view-menu')
@login_required
def view_menu():
    menu_items = MenuItem.query.filter_by(available=True).all()
    return render_template('view-menu.html', menu_items=menu_items)

@app.route('/place-order', methods=['POST'])
@login_required
def place_order():
    user = User.query.filter_by(email=session['user_email']).first()
    if not user:
        flash("User not found.")
        return redirect(url_for('login'))

    selected_items = []
    food_prices = []
    quantities = []

    # Parse selected menu items
    for key, qty in request.form.items():
        if key.startswith('qty_') and qty.isdigit() and int(qty) > 0:
            item_id = int(key.replace('qty_', ''))
            menu_item = MenuItem.query.get(item_id)
            if menu_item:
                selected_items.append({"id": item_id, "qty": int(qty)})
                food_prices.append(float(menu_item.price))
                quantities.append(int(qty))

    if not selected_items:
        flash("Please select at least one item.")
        return redirect(url_for('view_menu'))

    # Calculate total using C billing module
    is_premium_slot = False  # You can link to active reservation later if needed
    include_vip_fee = False  # VIP fee is handled separately
    total = calculate_total_bill(food_prices, quantities, is_premium_slot, include_vip_fee)

    # Prepare metadata to pass to payment page
    metadata = {
        "items": selected_items,
        "user_email": user.email,
        "is_vip": user.is_vip
    }

    # Redirect to payment page
    return redirect(url_for('payment_page',
                            amount=total,
                            description="Food Order Payment",
                            next_action='place_food_order',
                            metadata=json.dumps(metadata)))

@app.route('/order-status')
@login_required
def order_status():
    # Get latest order
    order = Order.query.filter_by(user_email=session['user_email']).order_by(Order.id.desc()).first()
    if not order:
        current_step = 0
        progress_percent = 0
    else:
        current_step = order.status
        progress_percent = 100 if current_step == 4 else (current_step - 1) * 33.33
    
    return render_template('order-status.html', current_step=current_step, progress_percent=progress_percent)

@app.route('/payment')
@login_required
def payment_page():
    amount = float(request.args.get('amount', 0))
    description = request.args.get('description', 'Payment')
    next_action = request.args.get('next_action', 'home')
    metadata = request.args.get('metadata', '')
    return render_template('payment.html', 
                          amount=amount, 
                          description=description, 
                          next_action=next_action,
                          metadata=metadata)

@app.route('/process-payment', methods=['POST'])
@login_required
def process_payment():
    next_action = request.form.get('next_action')
    metadata_str = request.form.get('metadata', '{}')
    
    # Safe JSON parsing
    try:
        metadata = json.loads(metadata_str)
    except (ValueError, TypeError):
        metadata = {}

    flash("✅ Payment successful!")

    try:
        if next_action == 'upgrade_to_vip':
            user = User.query.filter_by(email=session['user_email']).first()
            if user:
                user.is_vip = True
                db.session.commit()  # ✅ Save to database
                session['is_vip'] = True
                flash("✅ You are now a VIP member! Enjoy priority service.")
            return redirect(url_for('user_account'))

        elif next_action == 'confirm_booking':
            res = Reservation(
                user_email=session['user_email'],
                date=metadata.get('date'),
                time=metadata.get('time'),
                is_premium_slot=metadata.get('is_premium', False)
            )
            db.session.add(res)
            db.session.commit()
            schedule_reservation(res.id, current_timestamp())
            return redirect(url_for('home'))

        elif next_action == 'place_food_order':
            order = Order(
                user_email=session['user_email'],
                items=json.dumps(metadata.get('items', [])),
                total_price=float(request.form.get('amount', 0)),
                status=1
            )
            db.session.add(order)
            db.session.commit()
            # Use is_vip from metadata if available, else session
            is_vip = metadata.get('is_vip', session.get('is_vip', False))
            enqueue_order(order.id, is_vip)
            set_order_status(order.id, 1)
            return redirect(url_for('order_status'))

        else:
            return redirect(url_for('home'))
            
    except Exception as e:
        db.session.rollback()
        flash("⚠️ Payment succeeded, but order saving failed. Please contact support.")
        return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)