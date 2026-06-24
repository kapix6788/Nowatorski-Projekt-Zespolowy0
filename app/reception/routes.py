from flask import render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from app import db
from app.reception import bp
from app.models import RepairOrder, User, Vehicle
from app.utils import role_required
from app.pdf_generator import generate_invoice_pdf
import os

@bp.route('/orders', methods=['GET'])
@login_required
@role_required('recepcja')
def orders():
    search_query = request.args.get('search', '').strip()
    
    query = RepairOrder.query.join(User, RepairOrder.client_id == User.id)\
                             .join(Vehicle, RepairOrder.vehicle_id == Vehicle.id)
                             
    if search_query:
        terms = search_query.split()
        for term in terms:
            search_term = f'%{term}%'
            query = query.filter(
                db.or_(
                    User.last_name.ilike(search_term),
                    User.first_name.ilike(search_term),
                    Vehicle.license_plate.ilike(search_term)
                )
            )

    all_orders = query.order_by(RepairOrder.created_at.desc()).all()
    mechanics = User.query.filter_by(role='mechanik').all()
    vehicles = Vehicle.query.all()
    clients = User.query.filter_by(role='klient').all()
    
    return render_template('reception/orders.html', 
                           orders=all_orders, 
                           mechanics=mechanics, 
                           vehicles=vehicles,
                           clients=clients,
                           search_query=search_query)

@bp.route('/add-client-vehicle', methods=['POST'])
@login_required
@role_required('recepcja')
def add_client_vehicle():
    email = request.form.get('email')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    phone = request.form.get('phone')
    make = request.form.get('make')
    model = request.form.get('model')
    license_plate = request.form.get('license_plate')
    
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(username=email, email=email, role='klient', first_name=first_name, last_name=last_name, phone=phone)
        user.set_password('startowe123')
        db.session.add(user)
        db.session.flush()
        
    if not Vehicle.query.filter_by(license_plate=license_plate).first():
        v = Vehicle(make=make, model=model, license_plate=license_plate, owner_id=user.id)
        db.session.add(v)
        
    db.session.commit()
    flash('Zarejestrowano klienta i pojazd pomyślnie.', 'success')
    return redirect(url_for('reception.orders'))

@bp.route('/add-order', methods=['POST'])
@login_required
@role_required('recepcja')
def add_order():
    vehicle_id = request.form.get('vehicle_id')
    desc = request.form.get('description')
    
    vehicle = Vehicle.query.get(vehicle_id)
    if vehicle:
        order = RepairOrder(client_id=vehicle.owner_id, vehicle_id=vehicle.id, description=desc, status='oczekujace')
        db.session.add(order)
        db.session.commit()
        flash('Utworzono nowe zlecenie naprawy.', 'success')
    return redirect(url_for('reception.orders'))

@bp.route('/order/<int:order_id>/update', methods=['POST'])
@login_required
@role_required('recepcja')
def update_order(order_id):
    order = RepairOrder.query.get_or_404(order_id)
    new_status = request.form.get('status')
    mechanic_id = request.form.get('mechanic_id')
    
    if new_status:
        order.status = new_status
    if mechanic_id:
        order.mechanic_id = mechanic_id
        if not new_status and order.status == 'oczekujace':
            order.status = 'w_trakcie'
            
    db.session.commit()
    flash('Zaktualizowano parametry zlecenia.', 'success')
    return redirect(url_for('reception.orders'))

@bp.route('/order/<int:order_id>/edit-desc', methods=['POST'])
@login_required
@role_required('recepcja')
def edit_order_desc(order_id):
    order = RepairOrder.query.get_or_404(order_id)
    desc = request.form.get('description')
    if desc:
        order.description = desc
        db.session.commit()
        flash('Opis zlecenia został zaktualizowany.', 'success')
    return redirect(url_for('reception.orders'))

@bp.route('/order/<int:order_id>/delete', methods=['POST'])
@login_required
@role_required('recepcja')
def delete_order(order_id):
    order = RepairOrder.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    flash('Zlecenie zostało trwale usunięte.', 'success')
    return redirect(url_for('reception.orders'))

@bp.route('/order/<int:order_id>/assign', methods=['POST'])
@login_required
@role_required('recepcja')
def assign_mechanic(order_id):
    return update_order(order_id)

@bp.route('/clients', methods=['GET'])
@login_required
@role_required('recepcja')
def clients():
    all_clients = User.query.filter_by(role='klient').all()
    return render_template('reception/clients.html', clients=all_clients)

@bp.route('/order/<int:order_id>/invoice', methods=['GET'])
@login_required
def generate_invoice(order_id):
    order = RepairOrder.query.get_or_404(order_id)
    if current_user.role == 'klient' and order.client_id != current_user.id:
        flash('Brak uprawnień.', 'error')
        return redirect(url_for('index'))
        
    pdf_path = generate_invoice_pdf(order)
    if pdf_path and os.path.exists(pdf_path):
        return send_file(pdf_path, as_attachment=True)
    else:
        flash('Błąd podczas generowania faktury.', 'error')
        if current_user.role == 'recepcja':
            return redirect(url_for('reception.orders'))
        return redirect(url_for('client.my_garage'))
