
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Create a new PDF
c = canvas.Canvas("generated_document.pdf", pagesize=letter)
# Add some text
c.setFont("Helvetica", 12)
c.drawString(100, 750, "Hello, this is a generated PDF with Python!")
# Save the PDF
c.save()
print("✅ PDF generated!")
#This will create a new PDF called generated_document.pdf with some basic text