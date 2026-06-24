import os
from fpdf import FPDF
import tempfile

def generate_invoice_pdf(repair_order):
    try:
        from app import db
        fd, temp_path = tempfile.mkstemp(suffix='.pdf')
        os.close(fd)
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=14)
        
        total_cost = 0.0
        
        pdf.cell(200, 10, txt=f"FAKTURA do zlecenia #{repair_order.id}", ln=True, align='C')
        pdf.cell(200, 10, txt=f"Klient: {repair_order.client.first_name} {repair_order.client.last_name}", ln=True)
        pdf.cell(200, 10, txt=f"Pojazd: {repair_order.vehicle.make} {repair_order.vehicle.model}", ln=True)
        
        pdf.ln(10)
        pdf.set_font("Helvetica", style="B", size=12)
        pdf.cell(200, 10, txt="WYKAZ USLUG:", ln=True)
        pdf.set_font("Helvetica", size=12)
        
        for svc in repair_order.services_used:
            pdf.cell(200, 8, txt=f"- {svc.service.name}: {svc.price_applied} PLN", ln=True)
            total_cost += float(svc.price_applied)
            
        pdf.ln(5)
        pdf.set_font("Helvetica", style="B", size=12)
        pdf.cell(200, 10, txt="WYKAZ CZESCI:", ln=True)
        pdf.set_font("Helvetica", size=12)
        
        for part in repair_order.parts_used:
            cost = float(part.unit_price) * part.quantity
            pdf.cell(200, 8, txt=f"- {part.quantity}x {part.part.name}: {cost:.2f} PLN", ln=True)
            total_cost += cost
            
        pdf.ln(10)
        pdf.set_font("Helvetica", style="B", size=14)
        pdf.cell(200, 10, txt=f"SUMA DO ZAPLATY: {total_cost:.2f} PLN", ln=True)
        
        pdf.output(temp_path)
        return temp_path
        
    except Exception as e:
        print(f"Blad generowania PDF: {e}")
        return None
