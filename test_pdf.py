from weasyprint import HTML
from io import BytesIO

try:
    print("Iniciando prueba de WeasyPrint...")
    html_content = "<h1>Prueba PDF</h1><p>Hola Mundo</p>"
    pdf_file = BytesIO()
    HTML(string=html_content).write_pdf(pdf_file)
    print("✅ PDF generado exitosamente")
except Exception as e:
    print(f"❌ Error generando PDF: {e}")
    import traceback
    traceback.print_exc()
