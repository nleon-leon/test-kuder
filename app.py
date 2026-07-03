import streamlit as st
import pandas as pd
import numpy as np
import io

# Motor de renderizado PDF de ReportLab
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Importamos la base de datos que ya tienes en tu otro archivo
from preguntas import TRIADAS_KUDER

# Configuración estética del sitio institucional
st.set_page_config(
    page_title="Test de Kuder - PACE UCT",
    page_icon="📊",
    layout="centered"
)

# --- HOJA DE ESTILOS CSS PARA LA INTERFAZ WEB ---
st.markdown("""
    <style>
    .report-title { font-size:32px; font-weight:bold; text-align:center; color:#1F4E78; margin-bottom:5px; text-transform: uppercase; }
    .report-subtitle { font-size:16px; text-align:center; color:#595959; margin-bottom:20px; font-weight:500; }
    .description-box { background-color: #F8F9FA; padding: 18px; border-radius: 8px; margin-bottom: 25px; border: 1px solid #E2E8F0; text-align: justify; color: #334155; font-size: 14.5px; line-height: 1.6; }
    .instruction-box { background-color: #EBF5FF; padding: 18px; border-radius: 8px; margin-bottom: 25px; border-left: 5px solid #1D4ED8; color: #1E3A8A; font-size: 14.5px; }
    .instruction-title { font-weight: bold; font-size: 16px; margin-bottom: 8px; display: flex; align-items: center; gap: 8px; }
    .info-box { background-color: #F2F4F7; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 5px solid #1F4E78; text-align: justify; color: #1F4E78; }
    .top-area-card { background-color: #E2EFDA; padding: 10px 15px; border-radius: 6px; margin: 5px 0px; border-left: 4px solid #375623; font-weight: bold; text-align: center; color: #375623; }
    .triada-header { font-size:16px; font-weight:bold; color: #FFFFFF !important; background-color: #1F4E78; padding:8px 12px; border-radius:4px; margin-top:20px; margin-bottom:10px; }
    .footer-box { border-top: 2px solid #1F4E78; margin-top: 50px; padding-top: 15px; text-align: center; color: #595959; font-size: 13px; line-height: 1.6; }
    </style>
""", unsafe_allow_html=True)

# Diccionario global de descripciones de perfiles vocacionales
DESCRIPCIONES = {
    "Exterior": "Disfruta el trabajo al aire libre, actividades agrícolas, forestales o proyectos en terreno.",
    "Mecánica": "Interés por entender el funcionamiento de máquinas, herramientas, armar artefactos u objetos técnicos.",
    "Cálculo": "Disfruta trabajar con números, resolver operaciones y analizar datos o resultados matemáticos.",
    "Científica": "Siente curiosidad por investigar, descubrir cómo funcionan las cosas y buscar soluciones a diferentes problemas.",
    "Persuasiva": "Le gusta comunicar sus ideas, liderar grupos, convencer a otras personas y relacionarse con distintos tipos de público.",
    "Artística": "Disfruta crear, diseñar y expresar ideas mediante dibujos, colores, formas, manualidades u otras expresiones creativas.",
    "Literaria": "Le interesa leer, escribir y expresar sus pensamientos o emociones de manera oral o escrita.",
    "Musical": "Le atrae la música y disfruta actividades como cantar, tocar instrumentos, bailar o aprender sobre artistas y compositores.",
    "Servicio Social": "Le motiva ayudar a otras personas, colaborar con quienes lo necesitan y aportar al bienestar de la comunidad.",
    "Oficina": "Le acomoda realizar trabajos organizados y ordenados, que requieren responsabilidad, precisión y atención a los detalles."
}

# Inicializadores del Estado de la Sesión de Streamlit
if "procesado" not in st.session_state:
    st.session_state.procesado = False
if "lista_top_enviada" not in st.session_state:
    st.session_state.lista_top_enviada = []

# --- FUNCIÓN CONSTRUCTORA DEL REPORTE PDF ---
def generar_pdf_reportlab(nombre, colegio, curso, lista_top_areas):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    
    styles = getSampleStyleSheet()
    
    style_header1 = ParagraphStyle('H1', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=13, textColor=colors.HexColor("#1F4E78"), alignment=1, spaceAfter=4)
    style_header2 = ParagraphStyle('H2', parent=styles['Normal'], fontName='Helvetica', fontSize=10, textColor=colors.HexColor("#595959"), alignment=1, spaceAfter=15)
    style_title = ParagraphStyle('Title', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=16, alignment=1, spaceAfter=15)
    
    style_body = ParagraphStyle('Body', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14, spaceAfter=6)
    style_bold_label = ParagraphStyle('BoldLabel', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=14)
    style_area_title = ParagraphStyle('AreaTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, textColor=colors.HexColor("#375623"), spaceBefore=8, spaceAfter=2)
    style_footer = ParagraphStyle('Footer', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=8, textColor=colors.HexColor("#787878"), alignment=1, spaceBefore=20)

    # Encabezados del documento
    story.append(Paragraph("PROGRAMA PACE UCT - UNIVERSIDAD CATÓLICA DE TEMUCO", style_header1))
    story.append(Paragraph("Dirección de Acceso Inclusivo - Componente PEM", style_header2))
    story.append(Paragraph("INFORME DE RESULTADOS: TEST DE KUDER", style_title))
    story.append(Spacer(1, 10))
    
    # Cuadro informativo estructurado
    datos = [
        [Paragraph("<b>DATOS DE IDENTIFICACIÓN</b>", style_bold_label), ""],
        [Paragraph(f"<b>Estudiante:</b> {nombre}", style_body), Paragraph(f"<b>Establecimiento:</b> {colegio}", style_body)],
        [Paragraph(f"<b>Curso:</b> {curso}", style_body), Paragraph("<b>Instrumento:</b> Escala Kuder (Tríadas)", style_body)]
    ]
    t_datos = Table(datos, colWidths=[260, 260])
    t_datos.setStyle(TableStyle([
        ('SPAN', (0, 0), (1, 0)),
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor("#F2F4F7")),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('LINEBELOW', (0, 0), (1, 0), 1, colors.HexColor("#1F4E78")),
    ]))
    story.append(t_datos)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("<b>ÁREAS VOCACIONALES CON MAYOR AFINIDAD</b>", style_header1))
    story.append(Paragraph("Las siguientes áreas obtuvieron los puntajes porcentuales más destacados en tu cuestionario. Indican actividades que guardan relación directa con tus intereses, preferencias y comodidad de desarrollo:", style_body))
    story.append(Spacer(1, 10))
    
    for area_item in lista_top_areas:
        nombre_area = area_item["area"]
        porcentaje_area = area_item["porcentaje"]
        story.append(Paragraph(f"• {nombre_area} ({porcentaje_area}%)", style_area_title))
        story.append(Paragraph(f"<b>Descripción:</b> {DESCRIPCIONES[nombre_area]}", style_body))
        story.append(Spacer(1, 5))
        
    story.append(Spacer(1, 20))
    story.append(Paragraph("Nota: Este reporte sirve como orientación en el marco de los talleres PEM PACE UCT. No representa una limitación académica absoluta.<br/>Desarrollado por Nelson León C. - Coordinador de área PACE UCT.", style_footer))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# --- INTERFAZ GRÁFICA WEB ---
st.markdown('<div class="report-title">TEST DE KUDER</div>', unsafe_allow_html=True)
st.markdown('<div class="report-subtitle">PROGRAMA DE ACOMPAÑAMIENTO Y ACCESO EFECTIVO A LA EDUCACIÓN SUPERIOR (PACE UCT)</div>', unsafe_allow_html=True)

st.markdown("""
    <div class="description-box">
        <b>¿Para qué sirve este test?</b><br>
        El Escala de Preferencias Vocacionales de G.F. Kuder es un instrumento psicométrico diseñado para descubrir tus principales 
        intereses ocupacionales. A diferencia de otras pruebas, este test no evalúa tus conocimientos o capacidades académicas, 
        sino el nivel de agrado, comodidad o entusiasmo que sientes al realizar ciertas actividades.
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="instruction-box">
        <div class="instruction-title">📋 Instrucciones de Aplicación</div>
        A continuación, se presentan los bloques que contienen tres actividades cada uno (tríadas). Por cada bloque debes:<br>
        1. Seleccionar la actividad que <b>MÁS TE GUSTA (+)</b>.<br>
        2. Seleccionar la actividad que <b>MENOS TE GUSTA (-)</b> de las opciones restantes.
    </div>
""", unsafe_allow_html=True)

# --- SECCIÓN I: CAPTURA DE DATOS ---
st.subheader("👤 Datos de Identificación")
col1, col2 = st.columns(2)

with col1:
    nombres = st.text_input("NOMBRE:", placeholder="Ej: Nicole Solange")
    apellidos = st.text_input("APELLIDO:", placeholder="Ej: Carrasco Cantarillane")
with col2:
    colegio = st.text_input("ESTABLECIMIENTO:", placeholder="Ej: Complejo Educacional Luis Durand")
    curso = st.text_input("CURSO:", placeholder="Ej: Tercero AP")

nombre_completo = f"{nombres.strip().upper()} {apellidos.strip().upper()}" if nombres and apellidos else ""
establecimiento_caps = colegio.strip().upper() if colegio else ""

st.markdown("---")

# --- SECCIÓN II: RENDERIZADO DEL FORMULARIO IPSATIVO ---
st.subheader("🎯 Cuestionario de Preferencias Vocacionales")
respuestas_usuario = {}

for t in TRIADAS_KUDER:
    st.markdown('<div class="triada-header">Bloque N° ' + str(t['id']) + '</div>', unsafe_allow_html=True)
    mas = st.selectbox("¿Cuál actividad MÁS te gusta? (+)", ["Selecciona una opción..."] + t["opciones"], key=f"mas_{t['id']}")
    opciones_menos = [op for op in t["opciones"] if op != mas]
    menos = st.selectbox("¿Cuál actividad MENOS te gusta? (-)", ["Selecciona una opción..."] + opciones_menos, key=f"menos_{t['id']}")
    
    respuestas_usuario[t['id']] = {"mas": mas, "menos": menos, "meta": t}

st.markdown("---")

# --- SECCIÓN III: PROCESAMIENTO MATEMÁTICO ---
if st.button("📊 Generar Informe de Resultados Inmediato", type="primary"):
    if not nombres or not apellidos or not colegio or not curso:
        st.error("Por favor, rellena todos tus Datos de Identificación antes de continuar.")
        st.session_state.procesado = False
    else:
        incompletas = any(v["mas"] == "Selecciona una opción..." or v["menos"] == "Selecciona una opción..." for v in respuestas_usuario.values())
        
        if incompletas:
            st.warning("⚠️ Por favor, selecciona una opción (+) y una opción (-) para todos los bloques antes de generar el informe.")
            st.session_state.procesado = False
        else:
            st.session_state.procesado = True
            
            escalas_kuder = ["Exterior", "Mecánica", "Cálculo", "Científica", "Persuasiva", "Artística", "Literaria", "Musical", "Servicio Social", "Oficina"]
            puntajes_obtenidos = {esc: 0 for esc in escalas_kuder}
            maximos_por_escala = {esc: 0 for esc in escalas_kuder}
            
            for k, v in respuestas_usuario.items():
                opts = v["meta"]["opciones"]
                escs = v["meta"]["escalas"]
                for opt, esc in zip(opts, escs):
                    maximos_por_escala[esc] += 2 
                    if opt == v["mas"]:
                        puntajes_obtenidos[esc] += 2
                    elif opt == v["menos"]:
                        puntajes_obtenidos[esc] += 0
                    else:
                        puntajes_obtenidos[esc] += 1
            
            porcentajes = {}
            for esc in escalas_kuder:
                if maximos_por_escala[esc] > 0:
                    porcentajes[esc] = min(int((puntajes_obtenidos[esc] / maximos_por_escala[esc]) * 100), 100)
                else:
                    porcentajes[esc] = 0
            
            st.session_state.df_resultados = pd.DataFrame({
                "Área": escalas_kuder,
                "Porcentaje obtenido": [porcentajes[e] for e in escalas_kuder]
            })
            
            df_ordenado = st.session_state.df_resultados.sort_values(by="Porcentaje obtenido", ascending=False)
            top_areas_df = df_ordenado.head(3)
            
            st.session_state.lista_top_enviada = []
            for _, fila in top_areas_df.iterrows():
                st.session_state.lista_top_enviada.append({
                    "area": fila["Área"],
                    "porcentaje": fila["Porcentaje obtenido"]
                })

# --- SECCIÓN IV: DESPLIEGUE VISUAL ESTABLE Y DESCARGA ---
if st.session_state.procesado:
    st.markdown(f"""
        <div class="info-box">
        <b>ESTUDIANTE:</b> {nombre_completo}<br>
        <b>ESTABLECIMIENTO:</b> {establecimiento_caps} (Curso: {curso.upper()})<br><br>
        El análisis de tus resultados refleja qué tan presentes están estas habilidades e intereses en tu forma de ser.
        </div>
    """, unsafe_allow_html=True)
    
    st.subheader("📊 Distribución de tus intereses vocacionales")
    st.bar_chart(data=st.session_state.df_resultados, x="Área", y="Porcentaje obtenido", color="#1F4E78", use_container_width=True)
    
    st.subheader("🌟 Tus áreas con mayor afinidad")
    col_cards = st.columns(3)
    for idx, item in enumerate(st.session_state.lista_top_enviada):
        with col_cards[idx]:
            st.markdown(f'<div class="top-area-card">{item["area"]} ({item["porcentaje"]}%)</div>', unsafe_allow_html=True)
    
    st.subheader("📋 Descripción de tus áreas destacadas")
    tabla_data = []
    for item in st.session_state.lista_top_enviada:
        tabla_data.append({
            "Área Destacada": item["area"],
            "Descripción del Perfil": DESCRIPCIONES[item["area"]]
        })
    st.table(pd.DataFrame(tabla_data))
    
    # Bloque de persistencia binaria para el PDF
    st.markdown("---")
    st.subheader("💾 Guardar Resultados")
    try:
        pdf_bytes = generar_pdf_reportlab(nombre_completo, establecimiento_caps, curso.upper(), st.session_state.lista_top_enviada)
        
        st.download_button(
            label="📥 Descargar Reporte Vocacional en PDF",
            data=pdf_bytes,
            file_name=f"Resultado_Kuder_{nombre_completo.replace(' ', '_')}.pdf",
            mime="application/pdf",
            key="btn_descarga_pdf"
        )
    except Exception as e:
        st.error(f"Hubo un detalle técnico con la descarga: {e}")

# --- PIE DE PÁGINA ---
st.markdown("""
    <div class="footer-box">
        Desarrollado por el equipo del componente PEM del programa PACE UCT.<br>
        Dirección de Acceso Inclusivo. Adaptación de la versión aplicada a los estudiantes PACE.<br>
        <b>Desarrollador:</b> Nelson León C. - Coordinador de área.
    </div>
""", unsafe_allow_html=True)