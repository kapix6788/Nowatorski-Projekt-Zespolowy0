from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.client import bp
from app.models import Vehicle, RepairOrder

@bp.route('/my-garage', methods=['GET'])
@login_required
def my_garage():
    if current_user.role != 'klient':
        flash('Brak dostępu do wirtualnego garażu.', 'error')
        return redirect(url_for('index'))
        
    vehicles = Vehicle.query.filter_by(owner_id=current_user.id).all()
    orders = RepairOrder.query.filter_by(client_id=current_user.id).order_by(RepairOrder.created_at.desc()).all()
    
    return render_template('client/garage.html', vehicles=vehicles, orders=orders)

@bp.route('/add-vehicle', methods=['POST'])
@login_required
def add_vehicle():
    if current_user.role != 'klient':
        return redirect(url_for('index'))
        
    make = request.form.get('make')
    model = request.form.get('model')
    year = request.form.get('year')
    license_plate = request.form.get('license_plate')
    vin = request.form.get('vin')
    
    if Vehicle.query.filter_by(license_plate=license_plate).first() or (vin and Vehicle.query.filter_by(vin=vin).first()):
        flash('Pojazd o takich numerach (Rej/VIN) w bazie już istnieje.', 'error')
    else:
        v = Vehicle(make=make, model=model, year=year if year else None, 
                    license_plate=license_plate, vin=vin, owner_id=current_user.id)
        db.session.add(v)
        db.session.commit()
        flash('Pojazd został dodany do garażu.', 'success')
        
    return redirect(url_for('client.my_garage'))

@bp.route('/delete-vehicle/<int:vehicle_id>', methods=['POST'])
@login_required
def delete_vehicle(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    if vehicle.owner_id == current_user.id:
        db.session.delete(vehicle)
        db.session.commit()
        flash('Pojazd usunięto.', 'success')
    return redirect(url_for('client.my_garage'))

@bp.route('/book-appointment', methods=['POST'])
@login_required
def book_appointment():
    vehicle_id = request.form.get('vehicle_id')
    desc = request.form.get('description')
    
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    if vehicle.owner_id != current_user.id:
        flash('Brak uprawnień.', 'error')
        return redirect(url_for('client.my_garage'))
        
    order = RepairOrder(client_id=current_user.id, vehicle_id=vehicle.id, description=desc, status='oczekujace')
    db.session.add(order)
    db.session.commit()
    flash('Zgłoszenie naprawy wysłane. Oczekuj na akceptację serwisu.', 'success')
    return redirect(url_for('client.my_garage'))
