from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.mechanic import bp
from app.models import RepairOrder, Part, ServiceCatalog, OrderPart, OrderService, RepairNote, PartRequest
from app.utils import role_required
from datetime import datetime

@bp.route('/my-orders', methods=['GET'])
@login_required
@role_required('mechanik')
def my_orders():
    orders = RepairOrder.query.filter_by(mechanic_id=current_user.id).all()
    return render_template('mechanic/my_orders.html', orders=orders)

@bp.route('/order/<int:order_id>', methods=['GET'])
@login_required
@role_required('mechanik')
def order_details(order_id):
    order = RepairOrder.query.get_or_404(order_id)
    if order.mechanic_id != current_user.id:
        flash('Możesz podglądać tylko swoje zlecenia.', 'error')
        return redirect(url_for('mechanic.my_orders'))
        
    parts = Part.query.all()
    services = ServiceCatalog.query.all()
    return render_template('mechanic/order_details.html', order=order, parts=parts, services=services)

@bp.route('/order/<int:order_id>/update-status', methods=['POST'])
@login_required
@role_required('mechanik')
def update_status(order_id):
    order = RepairOrder.query.get_or_404(order_id)
    if order.mechanic_id == current_user.id:
        order.status = request.form.get('status')
        db.session.commit()
        flash('Status zlecenia zaktualizowany.', 'success')
    return redirect(url_for('mechanic.order_details', order_id=order.id))

@bp.route('/order/<int:order_id>/add-part', methods=['POST'])
@login_required
@role_required('mechanik')
def add_part(order_id):
    order = RepairOrder.query.get_or_404(order_id)
    part_id = request.form.get('part_id')
    qty = int(request.form.get('quantity', 1))
    
    part = Part.query.get(part_id)
    if part and part.stock_quantity >= qty:
        part.stock_quantity -= qty
        op = OrderPart(repair_order_id=order.id, part_id=part.id, quantity=qty, unit_price=part.unit_price)
        db.session.add(op)
        db.session.commit()
        flash('Rozliczono część z magazynu.', 'success')
    else:
        flash('Brak wystarczającej ilości w magazynie!', 'error')
        
    return redirect(url_for('mechanic.order_details', order_id=order.id))

@bp.route('/order/<int:order_id>/add-service', methods=['POST'])
@login_required
@role_required('mechanik')
def add_service(order_id):
    order = RepairOrder.query.get_or_404(order_id)
    service_id = request.form.get('service_id')
    
    svc = ServiceCatalog.query.get(service_id)
    if svc:
        os = OrderService(repair_order_id=order.id, service_id=svc.id, price_applied=svc.price)
        db.session.add(os)
        db.session.commit()
        flash('Dodano usługę.', 'success')
        
    return redirect(url_for('mechanic.order_details', order_id=order.id))

@bp.route('/order/<int:order_id>/add-note', methods=['POST'])
@login_required
@role_required('mechanik')
def add_note(order_id):
    content = request.form.get('content')
    req_parts = True if request.form.get('requires_parts') else False
    
    note = RepairNote(repair_order_id=order_id, author_id=current_user.id, content=content, requires_parts=req_parts)
    db.session.add(note)
    db.session.commit()
    flash('notatki zostały zaktualizowane.', 'success')
    return redirect(url_for('mechanic.order_details', order_id=order_id))

@bp.route('/order/<int:order_id>/request-part', methods=['POST'])
@login_required
@role_required('mechanik')
def request_part(order_id):
    name = request.form.get('part_name')
    qty = request.form.get('quantity', 1)
    
    pr = PartRequest(mechanic_id=current_user.id, repair_order_id=order_id, part_name=name, quantity=qty)
    db.session.add(pr)
    db.session.commit()
    flash('Wysłano zgłoszenie zapotrzebowania na części.', 'warning')
    return redirect(url_for('mechanic.order_details', order_id=order_id))

@bp.route('/parts', methods=['GET'])
@login_required
@role_required('mechanik')
def parts_catalog():
    parts = Part.query.all()
    return render_template('mechanic/parts.html', parts=parts)