import streamlit as st
import pandas as pd
import os
from fpdf import FPDF
from datetime import datetime
from zoneinfo import ZoneInfo
from collections import Counter

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Conferência - Domínio Ferramentas", layout="wide", initial_sidebar_state="expanded")

# CORES DA DOMÍNIO
COR_PRIMARIA = "#C9AD4E"       # Dourado/Bege
COR_FUNDO_1 = "#192561"        # Azul Superior
COR_FUNDO_2 = "#0B112C"        # Azul Inferior

# --- CSS ESTILIZADO E ALINHADO ---
st.markdown(f"""
    <style>
    /* Fundo da tela principal inteiro */
    [data-testid="stAppViewContainer"] {{
        background: linear-gradient(180deg, {COR_FUNDO_1} 0%, {COR_FUNDO_2} 100%) !important;
    }}
    [data-testid="stHeader"] {{ background: transparent !important; }}
    [data-testid="stSidebar"] {{
        background-color: {COR_FUNDO_2} !important;
        border-right: 1px solid rgba(201, 173, 78, 0.2);
    }}
    .block-container {{ color: #FFFFFF; }}
    .stTextInput > div > div > input, .stNumberInput > div > div > input {{
        color: #FFFFFF !important;
        background-color: #1a1a1a !important;
        border: 1px solid {COR_PRIMARIA} !important;
    }}
    div[data-testid="stTextInput"] label, div[data-testid="stNumberInput"] label {{
        color: {COR_PRIMARIA} !important; font-weight: bold;
    }}
    div.stButton > button {{
        color: #FFFFFF !important;
        border: 1px solid {COR_PRIMARIA};
        background-color: rgba(201, 173, 78, 0.1);
        transition: 0.3s;
    }}
    div.stButton > button:hover {{
        background-color: {COR_PRIMARIA} !important;
        color: black !important;
    }}
    .stDataFrame {{ border: 1px solid {COR_PRIMARIA}; }}
    .stCheckbox label {{ color: white !important; }}

    /* ===== KPI CARD ===== */
    .kpi-card {{
        background: linear-gradient(145deg, rgba(25, 37, 97, 0.6), rgba(11, 17, 44, 0.8));
        padding: 22px;
        border-radius: 18px;
        border: 1px solid rgba(201, 173, 78, 0.3);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        transition: all 0.25s ease-in-out;
        position: relative;
        overflow: hidden;
        margin-bottom: 10px;
    }}
    .kpi-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 15px 40px rgba(201, 173, 78, 0.2);
        border: 1px solid rgba(201, 173, 78, 0.8);
    }}
    .kpi-title {{ font-size: 13px; color: #E2E8F0; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }}
    .kpi-value {{ font-size: 28px; font-weight: 700; line-height: 1.5; color: #FFFFFF; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding-bottom: 25px; }} 
    .kpi-badge {{ position: absolute; bottom: 0; left: 0; width: 100%; padding: 6px 14px; font-size: 11px; font-weight: 600; border-top: 1px solid rgba(201, 173, 78, 0.2); }}
    .badge-gold {{ background: linear-gradient(90deg, rgba(201,173,78,0.2), rgba(201,173,78,0.05)); color: #C9AD4E; }}
    .badge-blue {{ background: linear-gradient(90deg, rgba(255,255,255,0.1), rgba(255,255,255,0.02)); color: #FFFFFF; }}
    </style>
    """, unsafe_allow_html=True)

def kpi_card(title, value, badge_text, badge_color="gold"):
    badge_class = "badge-gold" if badge_color == "gold" else "badge-blue"
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-badge {badge_class}">{badge_text}</div>
        </div>
    """, unsafe_allow_html=True)

# --- CLASSE DO PDF ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'ROMANEIO DE CONFERENCIA - DOMINIO FERRAMENTAS', 0, 1, 'C')
        self.ln(10)
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Pagina {self.page_no()}/{{nb}}', 0, 0, 'C')

def gerar_pdf_bonito(df_dict, pedido, separador, conferente):
    df = pd.DataFrame.from_dict(df_dict, orient='index')
    df.reset_index(inplace=True)
    df.columns = ['Código', 'Descrição', 'Marca', 'Quantidade']
    
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 8, f"PEDIDO / NF: {pedido.upper()}", ln=True, fill=True, border='LBRT')
    
    data_hora_certa = datetime.now(ZoneInfo("America/Sao_Paulo")).strftime('%d/%m/%Y %H:%M')
    pdf.cell(0, 8, f"DATA/HORA: {data_hora_certa}", ln=True, fill=True, border='LBRT')
    pdf.ln(5)
    
    pdf.set_font("Arial", '', 10)
    separador_limpo = separador.upper().encode('latin-1', 'ignore').decode('latin-1')
    conferente_limpo = conferente.upper().encode('latin-1', 'ignore').decode('latin-1')
    pdf.cell(95, 8, f"Separador: {separador_limpo}", border=1)
    pdf.cell(95, 8, f"Conferente: {conferente_limpo}", border=1, ln=True)
    pdf.ln(8)
    
    pdf.set_font("Arial", 'B', 9)
    pdf.set_fill_color(50, 50, 50)
    pdf.set_text_color(255, 255, 255)
    col_w = [30, 100, 35, 25]
    cols = ['CODIGO', 'DESCRICAO', 'MARCA', 'QTD']
    for i in range(4): pdf.cell(col_w[i], 8, cols[i], border=1, fill=True, align='C')
    pdf.ln()
    
    pdf.set_font("Arial", size=9)
    pdf.set_text_color(0, 0, 0)
    total_itens = 0
    for _, row in df.iterrows():
        pdf.cell(col_w[0], 8, str(row['Código']), border='LBR', align='C')
        desc = str(row['Descrição'])
        desc = (desc[:45] + '..') if len(desc) > 45 else desc
        desc = desc.encode('latin-1', 'ignore').decode('latin-1') 
        pdf.cell(col_w[1], 8, desc, border='LBR')
        marca = str(row['Marca']).encode('latin-1', 'ignore').decode('latin-1')
        pdf.cell(col_w[2], 8, marca, border='LBR', align='C')
        pdf.cell(col_w[3], 8, str(row['Quantidade']), border='LBR', align='C')
        pdf.ln()
        total_itens += row['Quantidade']

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"TOTAL DE VOLUMES: {total_itens}", ln=True, align='R')
    
    pdf.ln(25)
    pdf.set_font("Arial", '', 10)
    pdf.cell(95, 0, "_______________________________", align='C')
    pdf.cell(95, 0, "_______________________________", align='C', ln=True)
    pdf.cell(95, 8, "Visto do Conferente", align='C')
    pdf.cell(95, 8, "Visto do Supervisor", align='C')

    return pdf.output(dest="S").encode("latin-1")

@st.cache_data
def carregar_base():
    arquivo = "produtos.xlsx"
    if not os.path.exists(arquivo): return None
    try:
        df = pd.read_excel(arquivo)
        df.columns = df.columns.str.lower()
        def limpar(val):
            s = str(val).strip()
            return s[:-2] if s.endswith('.0') else s
        if 'codigo' in df.columns: df['codigo'] = df['codigo'].apply(limpar)
        return df
    except: return None

base_produtos = carregar_base()

if 'conferencia' not in st.session_state: st.session_state.conferencia = {} 
if 'msg_status' not in st.session_state: st.session_state.msg_status = ("info", "Preencha os dados para iniciar.")
if 'historico' not in st.session_state: st.session_state.historico = [] 

def finalizar_e_limpar():
    if st.session_state.conferencia and st.session_state.input_pedido:
        st.session_state.historico.append({
            "pedido": st.session_state.input_pedido,
            "separador": st.session_state.input_separador.strip().upper(),
            "conferente": st.session_state.input_conferente.strip().upper(),
            "qtd_pecas": sum(item['qtd'] for item in st.session_state.conferencia.values())
        })
        st.toast('🔥 PEDIDO REGISTRADO! MANDA O PRÓXIMO!', icon='🚀')
    
    st.session_state.conferencia = {}
    st.session_state.input_pedido = ""
    st.session_state.input_separador = ""
    st.session_state.input_conferente = ""
    st.session_state.msg_status = ("info", "Pronto para o próximo pedido!")

# --- FUNÇÃO DO POP-UP DE RANKING ---
@st.dialog("🏆 RANKING GERAL DA EQUIPE")
def popup_ranking():
    if not st.session_state.historico:
        st.warning("Nenhum pedido finalizado ainda hoje.")
        return
    
    df_hist = pd.DataFrame(st.session_state.historico)
    
    # Conta pedidos por separador
    rank_sep = df_hist['separador'].value_counts().reset_index()
    rank_sep.columns = ['Separador', 'Pedidos Separados']
    
    # Conta pedidos por conferente
    rank_conf = df_hist['conferente'].value_counts().reset_index()
    rank_conf.columns = ['Conferente', 'Pedidos Conferidos']

    c_sep, c_conf = st.columns(2)
    with c_sep:
        st.markdown("<h4 style='color: #C9AD4E; text-align: center;'>📦 Top Separadores</h4>", unsafe_allow_html=True)
        st.dataframe(rank_sep, hide_index=True, use_container_width=True)
    with c_conf:
        st.markdown("<h4 style='color: #C9AD4E; text-align: center;'>✅ Top Conferentes</h4>", unsafe_allow_html=True)
        st.dataframe(rank_conf, hide_index=True, use_container_width=True)

with st.sidebar:
    st.markdown(f"<h3 style='color: {COR_PRIMARIA};'>⚙️ Configurações</h3>", unsafe_allow_html=True)
    st.write("Defina a meta de pedidos a serem conferidos hoje:")
    meta_diaria = st.number_input("Meta Diária", min_value=1, value=100, step=10)

col_logo, col_tit = st.columns([1, 5])
with col_logo:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.header("🛠️ DF") 
with col_tit:
    st.title("Conferência Física")
    st.caption("Domínio Ferramentas - Sistema de Bipagem Rápida")

hist = st.session_state.historico
total_pedidos = len(hist)
total_pecas_dia = sum(h['qtd_pecas'] for h in hist)

if hist:
    separadores = [h['separador'] for h in hist if h['separador']]
    conferentes = [h['conferente'] for h in hist if h['conferente']]
    top_sep = Counter(separadores).most_common(1)[0][0] if separadores else "N/A"
    top_conf = Counter(conferentes).most_common(1)[0][0] if conferentes else "N/A"
else:
    top_sep = "N/A"
    top_conf = "N/A"

k1, k2, k3 = st.columns(3)
with k1: kpi_card("Pedidos Conferidos", f"{total_pedidos}", f"{total_pecas_dia} peças totais", "gold")
with k2: kpi_card("Top Separador", top_sep, "Líder em Separação", "blue")
with k3: kpi_card("Top Conferente", top_conf, "Líder em Conferência", "blue")

# BOTÃO DO POP-UP
if st.button("👁️ VER RANKING COMPLETO DA EQUIPE", use_container_width=True):
    popup_ranking()

st.write("") 
porcentagem = min(total_pedidos / meta_diaria, 1.0)
st.progress(porcentagem, text=f"🎯 Progresso da Meta Diária: {total_pedidos} de {meta_diaria} pedidos")

st.divider()

c1, c2, c3 = st.columns(3)
pedido = c1.text_input("Nº Pedido / NF", placeholder="Digite...", key="input_pedido")
separador = c2.text_input("Separador", placeholder="Nome...", key="input_separador")
conferente = c3.text_input("Conferente", placeholder="Nome...", key="input_conferente")

if not (pedido and separador and conferente):
    st.info("👆 Para liberar o scanner, preencha os 3 campos acima.")
    st.stop()

st.markdown("---")

def processar():
    cod = st.session_state.input_bip.strip()
    cod_limpo = cod[:-2] if cod.endswith('.0') else cod
    if not cod_limpo: return
    if base_produtos is not None:
        prod = base_produtos[base_produtos['codigo'] == cod_limpo]
        if not prod.empty:
            item = prod.iloc[0]
            if cod_limpo in st.session_state.conferencia:
                st.session_state.conferencia[cod_limpo]['qtd'] += 1
                st.session_state.msg_status = ("success", f"➕ Somado: {item['descricao'][:30]}...")
            else:
                m = item['marca'] if 'marca' in item else '-'
                st.session_state.conferencia[cod_limpo] = {'desc': item['descricao'], 'marca': m, 'qtd': 1}
                st.session_state.msg_status = ("success", f"✅ Novo: {item['descricao'][:30]}...")
        else:
            st.session_state.msg_status = ("error", f"❌ Erro: Código '{cod}' não encontrado.")
    st.session_state.input_bip = ""

st.text_input("Bipe aqui:", key="input_bip", on_change=processar, placeholder="Aguardando scanner...")

t, m = st.session_state.msg_status
if t == "success": st.success(m)
elif t == "error": st.error(m)

if st.session_state.conferencia:
    st.divider()
    df_vis = pd.DataFrame.from_dict(st.session_state.conferencia, orient='index')
    df_vis.reset_index(inplace=True)
    df_vis.columns = ['Código', 'Descrição', 'Marca', 'Quantidade']
    
    col_tabela, col_resumo = st.columns([2.5, 1.2])
    with col_tabela:
        st.subheader("📦 Itens Bipados")
        st.dataframe(df_vis, use_container_width=True, hide_index=True, height=400)
    
    with col_resumo:
        st.subheader("📊 Resumo do Pedido")
        kpi_card("Total de Peças", df_vis['Quantidade'].sum(), "Neste Pedido", "blue")
        kpi_card("SKUs Distintos", len(df_vis), "Itens Únicos", "blue")
        
        st.markdown("<br>", unsafe_allow_html=True)
        gerar_pdf = st.checkbox("🖨️ Encerrar e Gerar PDF")
        
        if gerar_pdf:
            with st.spinner("Gerando Romaneio..."):
                pdf_bytes = gerar_pdf_bonito(st.session_state.conferencia, pedido, separador, conferente)
                st.download_button(
                    label="📥 BAIXAR ROMANEIO (PDF)",
                    data=pdf_bytes,
                    file_name=f"Romaneio_{pedido}.pdf",
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )
        
        st.write("")
        st.button("💾 REGISTRAR E PRÓXIMO", on_click=finalizar_e_limpar, use_container_width=True)
