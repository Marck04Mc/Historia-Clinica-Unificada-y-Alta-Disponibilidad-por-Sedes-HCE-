"""
Router de exportación de historias clínicas a PDF
Genera PDFs con datos FHIR normalizados
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from weasyprint import HTML, CSS
from io import BytesIO
from datetime import datetime

from database import db
from models import User
from routers.auth import get_current_user

router = APIRouter(prefix="/api/pdf", tags=["Exportación PDF"])


def generate_html_historia_clinica(patient_data: dict, encounters: list, 
                                   observations: list, diagnostics: list, 
                                   medications: list, sede_info: dict) -> str:
    """
    Generar HTML de la historia clínica
    """
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Historia Clínica - {patient_data['nombres']} {patient_data['apellidos']}</title>
        <style>
            @page {{
                size: A4;
                margin: 2cm;
                @bottom-right {{
                    content: "Página " counter(page) " de " counter(pages);
                }}
            }}
            body {{
                font-family: Arial, sans-serif;
                font-size: 11pt;
                line-height: 1.4;
            }}
            .header {{
                text-align: center;
                border-bottom: 2px solid #333;
                padding-bottom: 10px;
                margin-bottom: 20px;
            }}
            .header h1 {{
                margin: 0;
                color: #2c3e50;
            }}
            .header p {{
                margin: 5px 0;
                color: #7f8c8d;
            }}
            .section {{
                margin-bottom: 20px;
                page-break-inside: avoid;
            }}
            .section h2 {{
                background-color: #3498db;
                color: white;
                padding: 8px;
                margin: 0 0 10px 0;
                font-size: 14pt;
            }}
            .info-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 10px;
                margin-bottom: 15px;
            }}
            .info-item {{
                padding: 5px;
            }}
            .info-label {{
                font-weight: bold;
                color: #2c3e50;
            }}
            .encounter {{
                border: 1px solid #bdc3c7;
                padding: 10px;
                margin-bottom: 15px;
                background-color: #ecf0f1;
            }}
            .encounter-header {{
                font-weight: bold;
                color: #2980b9;
                margin-bottom: 5px;
            }}
            .sede-badge {{
                display: inline-block;
                background-color: #e74c3c;
                color: white;
                padding: 2px 8px;
                border-radius: 3px;
                font-size: 9pt;
                margin-left: 10px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }}
            table th {{
                background-color: #34495e;
                color: white;
                padding: 8px;
                text-align: left;
                font-size: 10pt;
            }}
            table td {{
                border: 1px solid #bdc3c7;
                padding: 6px;
                font-size: 10pt;
            }}
            .code {{
                font-family: monospace;
                background-color: #f8f9fa;
                padding: 2px 4px;
                border-radius: 3px;
                font-size: 9pt;
            }}
            .footer {{
                margin-top: 30px;
                padding-top: 10px;
                border-top: 1px solid #bdc3c7;
                font-size: 9pt;
                color: #7f8c8d;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Historia Clínica Electrónica Única</h1>
            <p>{sede_info['nombre']} - {sede_info['ciudad']}</p>
            <p>Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
        </div>
        
        <div class="section">
            <h2>Información del Paciente</h2>
            <div class="info-grid">
                <div class="info-item">
                    <span class="info-label">Nombre:</span> {patient_data['nombres']} {patient_data['apellidos']}
                </div>
                <div class="info-item">
                    <span class="info-label">Identificación:</span> {patient_data['tipo_identificacion']} {patient_data['identificacion']}
                </div>
                <div class="info-item">
                    <span class="info-label">Fecha de Nacimiento:</span> {patient_data['fecha_nacimiento']}
                </div>
                <div class="info-item">
                    <span class="info-label">Género:</span> {patient_data['genero']}
                </div>
                <div class="info-item">
                    <span class="info-label">Teléfono:</span> {patient_data.get('telefono', 'N/A')}
                </div>
                <div class="info-item">
                    <span class="info-label">Email:</span> {patient_data.get('email', 'N/A')}
                </div>
            </div>
        </div>
    """
    
    # Agregar encuentros clínicos
    if encounters:
        html += """
        <div class="section">
            <h2>Encuentros Clínicos</h2>
        """
        
        for enc in encounters:
            html += f"""
            <div class="encounter">
                <div class="encounter-header">
                    {enc['tipo_encuentro'].upper()} - {enc['fecha_hora'].strftime('%d/%m/%Y %H:%M')}
                    <span class="sede-badge">{enc.get('sede_nombre', 'Sede desconocida')}</span>
                </div>
                <p><strong>Médico:</strong> {enc.get('doctor_nombre', 'N/A')}</p>
                <p><strong>Motivo:</strong> {enc.get('motivo_consulta', 'N/A')}</p>
                <p><strong>Notas:</strong> {enc.get('notas_clinicas', 'N/A')}</p>
            </div>
            """
        
        html += "</div>"
    
    # Agregar observaciones clínicas
    if observations:
        html += """
        <div class="section">
            <h2>Observaciones Clínicas</h2>
            <table>
                <thead>
                    <tr>
                        <th>Fecha</th>
                        <th>Descripción</th>
                        <th>Código LOINC</th>
                        <th>Valor</th>
                        <th>Unidad</th>
                        <th>Sede</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for obs in observations:
            valor = ""
            if obs.get('valor_numerico'):
                valor = str(obs['valor_numerico'])
            elif obs.get('valor_texto'):
                valor = obs['valor_texto']
            
            html += f"""
                <tr>
                    <td>{obs['fecha_hora'].strftime('%d/%m/%Y')}</td>
                    <td>{obs['descripcion']}</td>
                    <td><span class="code">{obs.get('codigo_loinc', 'N/A')}</span></td>
                    <td>{valor}</td>
                    <td>{obs.get('unidad', '')}</td>
                    <td>{obs.get('sede_nombre', 'N/A')}</td>
                </tr>
            """
        
        html += """
                </tbody>
            </table>
        </div>
        """
    
    # Agregar diagnósticos
    if diagnostics:
        html += """
        <div class="section">
            <h2>Diagnósticos</h2>
            <table>
                <thead>
                    <tr>
                        <th>Fecha</th>
                        <th>Descripción</th>
                        <th>ICD-10</th>
                        <th>SNOMED CT</th>
                        <th>Tipo</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for diag in diagnostics:
            html += f"""
                <tr>
                    <td>{diag['fecha_diagnostico'].strftime('%d/%m/%Y')}</td>
                    <td>{diag['descripcion']}</td>
                    <td><span class="code">{diag.get('codigo_icd10', 'N/A')}</span></td>
                    <td><span class="code">{diag.get('codigo_snomed', 'N/A')}</span></td>
                    <td>{diag.get('tipo', 'N/A')}</td>
                    <td>{diag.get('estado', 'N/A')}</td>
                </tr>
            """
        
        html += """
                </tbody>
            </table>
        </div>
        """
    
    # Agregar medicamentos
    if medications:
        html += """
        <div class="section">
            <h2>Medicamentos Prescritos</h2>
            <table>
                <thead>
                    <tr>
                        <th>Fecha</th>
                        <th>Medicamento</th>
                        <th>Dosis</th>
                        <th>Frecuencia</th>
                        <th>Vía</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for med in medications:
            html += f"""
                <tr>
                    <td>{med['fecha_prescripcion'].strftime('%d/%m/%Y')}</td>
                    <td>{med['nombre']}</td>
                    <td>{med.get('dosis', 'N/A')}</td>
                    <td>{med.get('frecuencia', 'N/A')}</td>
                    <td>{med.get('via_administracion', 'N/A')}</td>
                    <td>{med.get('estado', 'N/A')}</td>
                </tr>
            """
        
        html += """
                </tbody>
            </table>
        </div>
        """
    
    html += """
        <div class="footer">
            <p>Este documento contiene información médica confidencial protegida por la ley.</p>
            <p>Sistema de Historia Clínica Electrónica Interoperable - Estándar HL7 FHIR R4</p>
        </div>
    </body>
    </html>
    """
    
    return html


@router.get("/patient/{patient_id}")
async def export_patient_history(
    patient_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Exportar historia clínica completa de un paciente en PDF
    """
    
    # Obtener información del paciente
    patient = await db.fetch_one(
        "SELECT * FROM pacientes WHERE id_paciente = $1",
        patient_id
    )
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente no encontrado"
        )
    
    # Verificar permisos
    if current_user.rol == "paciente":
        if patient["id_usuario"] != current_user.id_usuario:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para ver este paciente"
            )
    
    # Obtener encuentros
    encounters = await db.fetch_all(
        """
        SELECT e.*, s.nombre as sede_nombre, s.ciudad as sede_ciudad,
               u.nombres || ' ' || u.apellidos as doctor_nombre
        FROM encuentros_clinicos e
        JOIN sedes s ON e.id_sede = s.id_sede
        JOIN usuarios u ON e.id_doctor = u.id_usuario
        WHERE e.id_paciente = $1
        ORDER BY e.fecha_hora DESC
        """,
        patient_id
    )
    
    # Obtener observaciones
    observations = await db.fetch_all(
        """
        SELECT o.*, s.nombre as sede_nombre
        FROM observaciones_clinicas o
        JOIN encuentros_clinicos e ON o.id_encuentro = e.id_encuentro
        JOIN sedes s ON e.id_sede = s.id_sede
        WHERE o.id_paciente = $1
        ORDER BY o.fecha_hora DESC
        """,
        patient_id
    )
    
    # Obtener diagnósticos
    diagnostics = await db.fetch_all(
        """
        SELECT d.*
        FROM diagnosticos d
        WHERE d.id_paciente = $1
        ORDER BY d.fecha_diagnostico DESC
        """,
        patient_id
    )
    
    # Obtener medicamentos
    medications = await db.fetch_all(
        """
        SELECT m.*
        FROM medicamentos m
        WHERE m.id_paciente = $1
        ORDER BY m.fecha_prescripcion DESC
        """,
        patient_id
    )
    
    # Obtener información de la sede
    sede = await db.fetch_one(
        "SELECT * FROM sedes WHERE id_sede = $1",
        current_user.id_sede
    )
    
    # Generar HTML
    html_content = generate_html_historia_clinica(
        patient, encounters, observations, 
        diagnostics, medications, sede
    )
    
    # Generar PDF
    pdf_file = BytesIO()
    HTML(string=html_content).write_pdf(pdf_file)
    pdf_file.seek(0)
    
    # Retornar PDF
    filename = f"historia_clinica_{patient['identificacion']}_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    return Response(
        content=pdf_file.read(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
