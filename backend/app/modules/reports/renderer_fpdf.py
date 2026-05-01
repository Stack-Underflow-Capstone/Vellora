from fpdf import FPDF
from datetime import datetime


class ReportPDFRenderer:

    def format_date(self, date_obj):
        return date_obj.strftime("%b %d, %Y")

    def format_money(self, value: float):
        return f"${value:,.2f}"

    def render(self, data):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        pdf.set_font("Arial", "B", 18)
        pdf.cell(0, 12, "Mileage & Expense Reimbursement Report", ln=True, align="C")
        pdf.ln(6)

        pdf.set_font("Arial", size=11)
        pdf.cell(0, 5, f"Employee: {data.employee_name}", ln=True)
        pdf.cell(0, 5, f"Email: {data.employee_email}", ln=True)
        pdf.cell(0, 5, f"Period: {self.format_date(data.period_start)} to {self.format_date(data.period_end)}", ln=True)
        pdf.cell(0, 5, f"Generated: {data.generated_at.strftime('%b %d, %Y %I:%M %p')}", ln=True)
        pdf.ln(8)

        pdf.set_fill_color(235, 235, 235)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Summary", ln=True, fill=True)

        pdf.set_font("Arial", size=11)
        pdf.cell(0, 6, f"Total Miles: {data.total_miles:.2f}", ln=True)
        pdf.cell(0, 6, f"Mileage Reimbursement: {self.format_money(data.total_mileage_amount)}", ln=True)
        pdf.cell(0, 6, f"Other Expenses: {self.format_money(data.total_expense_amount)}", ln=True)

        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, f"GRAND TOTAL: {self.format_money(data.grand_total)}", ln=True)
        pdf.ln(10)

        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Trips", ln=True)

        if not data.trips:
            pdf.set_font("Arial", size=10)
            pdf.cell(0, 6, "No recorded trips for this reporting period.", ln=True)
        else:
            pdf.set_font("Arial", "B", 10)
            pdf.set_fill_color(230, 230, 230)
            pdf.cell(35, 6, "Date", border=1, align="C", fill=True)
            pdf.cell(65, 6, "Purpose", border=1, align="C", fill=True)
            pdf.cell(20, 6, "Miles", border=1, align="C", fill=True)
            pdf.cell(25, 6, "Rate", border=1, align="C", fill=True)
            pdf.cell(35, 6, "Total", border=1, align="C", fill=True)
            pdf.ln(6)

            pdf.set_font("Arial", size=10)
            for trip in data.trips:
                pdf.cell(35, 6, self.format_date(trip.date), border=1)
                pdf.cell(65, 6, trip.purpose[:30], border=1)
                pdf.cell(20, 6, f"{trip.miles:.2f}", border=1, align="C")
                pdf.cell(25, 6, str(trip.rate_used or "-"), border=1, align="C")
                pdf.cell(35, 6, self.format_money(trip.mileage_total), border=1, align="R")
                pdf.ln(6)

        pdf.ln(10)

        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Expenses", ln=True)

        if not data.expenses:
            pdf.set_font("Arial", size=10)
            pdf.cell(0, 6, "No itemized expenses submitted.", ln=True)
        else:
            pdf.set_font("Arial", "B", 10)
            pdf.set_fill_color(230, 230, 230)
            pdf.cell(35, 6, "Date", border=1, align="C", fill=True)
            pdf.cell(80, 6, "Category", border=1, align="C", fill=True)
            pdf.cell(35, 6, "Amount", border=1, align="C", fill=True)
            pdf.ln(6)

            pdf.set_font("Arial", size=10)
            for exp in data.expenses:
                pdf.cell(35, 6, self.format_date(exp.date), border=1)
                pdf.cell(80, 6, exp.type[:40], border=1)
                pdf.cell(35, 6, self.format_money(exp.amount), border=1, align="R")
                pdf.ln(6)

        pdf.ln(15)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Approvals", ln=True)

        pdf.set_font("Arial", size=11)
        pdf.ln(5)
        pdf.cell(90, 6, "Employee Signature: ____________________", ln=False)
        pdf.cell(0, 6, "Date: _______________", ln=True)

        pdf.ln(5)
        pdf.cell(90, 6, "Manager Approval: ______________________", ln=False)
        pdf.cell(0, 6, "Date: _______________", ln=True)

        output = pdf.output(dest="S")
        return output.encode("latin1") if isinstance(output, str) else output
