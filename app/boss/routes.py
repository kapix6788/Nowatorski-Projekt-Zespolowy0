from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.boss import bp
from app.models import User, RepairOrder, ServiceCatalog, PartRequest
from app.utils import role_required
from sqlalchemy import func
from datetime import datetime

# WIDOK 1: Zarządzanie pracownikami (CRUD Personelu)
@bp.route('/employees', methods=['GET', 'POST'])
@login_required
@role_required('szef')
def employees():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            username = request.form.get('username')
            email = request.form.get('email')
            role = request.form.get('role')
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            
            if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
                flash('Konto o takim loginie lub emailu już istnieje.', 'error')
            else:
                new_employee = User(
                    username=username,
                    email=email,
                    role=role,
                    first_name=first_name,
                    last_name=last_name
                )
                new_employee.set_password('startowe123')
                db.session.add(new_employee)
                db.session.commit()
                flash(f'Utworzono pracownika {first_name} wg roli {role}. Hasło to: startowe123', 'success')
                
        elif action == 'delete':
            emp_id = request.form.get('employee_id')
            emp = User.query.get(emp_id)
            if emp and emp.id != current_user.id:
                db.session.delete(emp)
                db.session.commit()
                flash('Usunięto pracownika pomyślnie.', 'success')
            else:
                flash('Nie możesz usunąć konta głównego szefa.', 'error')
                
        return redirect(url_for('boss.employees'))

    # Wyświetla tylko współpracowników bez zwykłych klientów z ulicy
    staff = User.query.filter(User.role.in_(['szef', 'recepcja', 'mechanik'])).all()
    return render_template('boss/employees.html', employees=staff)


# WIDOK 2: Katalog Usług i Cennik (CRUD Katalogu)
@bp.route('/catalog', methods=['GET', 'POST'])
@login_required
@role_required('szef')
def catalog():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            name = request.form.get('name')
            desc = request.form.get('description')
            price = request.form.get('price')
            
            if ServiceCatalog.query.filter_by(name=name).first():
                flash('Usługa o takiej nazwie już istnieje cenniku.', 'error')
            else:
                new_service = ServiceCatalog(name=name, description=desc, price=float(price))
                db.session.add(new_service)
                db.session.commit()
                flash('Dodano pozycję do cennika.', 'success')
                
        elif action == 'delete':
            service_id = request.form.get('service_id')
            service = ServiceCatalog.query.get(service_id)
            if service:
                db.session.delete(service)
                db.session.commit()
                flash('Usługa wyleciała z cennika.', 'success')
                
        return redirect(url_for('boss.catalog'))

    services = ServiceCatalog.query.all()
    return render_template('boss/catalog.html', catalog=services)


# WIDOK 3: Panel Analityczny Szefa (Raporty)
@bp.route('/reports', methods=['GET'])
@login_required
@role_required('szef')
def reports():
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    query_orders = RepairOrder.query
    
    if date_from:
        df = datetime.strptime(date_from, '%Y-%m-%d')
        query_orders = query_orders.filter(RepairOrder.created_at >= df)
    if date_to:
        dt = datetime.strptime(date_to, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
        query_orders = query_orders.filter(RepairOrder.created_at <= dt)

    all_orders_in_period = query_orders.all()
    completed_orders = [o for o in all_orders_in_period if o.status in ['gotowe', 'odebrane']]
    
    revenue = 0.0
    for order in completed_orders:
        for svc in order.services_used:
            revenue += float(svc.price_applied)
        for part in order.parts_used:
            revenue += float(part.unit_price) * part.quantity

    total_all_time = RepairOrder.query.count()
    completed_all_time = RepairOrder.query.filter(RepairOrder.status.in_(['gotowe', 'odebrane'])).count()

    stats = {
        'clients_count': User.query.filter_by(role='klient').count(),
        'period_total': len(all_orders_in_period),
        'period_completed': len(completed_orders),
        'period_revenue': revenue,
        'completion_rate': int((completed_all_time / total_all_time * 100)) if total_all_time > 0 else 0
    }
    
    in_progress = RepairOrder.query.filter_by(status='w_trakcie').all()
    part_reqs = PartRequest.query.filter_by(status='oczekuje').order_by(PartRequest.created_at.desc()).all()
    
    return render_template('boss/reports.html', stats=stats, in_progress=in_progress, part_reqs=part_reqs, 
                           date_from=date_from, date_to=date_to)
