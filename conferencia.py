import streamlit as st
import pandas as pd
import os
from fpdf import FPDF
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Conferência - Domínio Ferramentas", layout="wide")

# CORES DA DOMÍNIO
COR_PRIMARIA = "#C9AD4E"       # Dourado/Bege
COR_FUNDO = "#04082A"          # Azul Marinho Profundo

# CSS ESTILIZADO E ALINHADO
st.markdown(f"""
    <style>
    /* Fundo Geral */
    .stApp {{ background-color: {COR_FUNDO}; color: white; }}
    
    /* Inputs de Texto */
    .stTextInput > div > div > input {{
        color: #FFFFFF !important;
        background-color: #2b2b2b !important;
        border: 2px solid {COR_PRIMARIA} !important;
    }}
    div[data-testid="stTextInput"] label {{
        color: {COR_PRIMARIA} !important; font-weight: bold;
    }}
    
    /* Botões */
    div.stButton > button {{
        color: #FFFFFF !important;
        border: 1px solid {COR_PRIMARIA};
        background-color: transparent;
        transition: 0.3s;
    }}
    div.stButton > button:hover {{
        background-color: {COR_PRIMARIA} !important;
        color: black !important;
    }}
    
    /* Caixa Branca das Métricas (Resumo) */
    div[data-testid="metric-container"] {{
        background-color: #FFFFFF !important;
        border: 1px solid {COR_PRIMARIA};
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 10px;
    }}
    div[data-testid="metric-container"] label {{ color: #000000 !important; }}
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {{ color: #000000 !important; }}
    
    /* Tabela */
    .stDataFrame {{ border: 1px solid {COR_PRIMARIA}; }}
    
    /* Checkbox */
    .stCheckbox label {{ color: white !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- CLASSE DO PDF ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'ROMANEIO DE CONFERÊNCIA - DOMÍNIO FERRAMENTAS', 0, 1, 'C')
        self.ln(10)
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}/{{nb}}', 0, 0, 'C')

def gerar_pdf_bonito(df_dict, pedido, separador, conferente):
    df = pd.DataFrame.from_dict(df_dict, orient='index')
    df.reset_index(inplace=True)
    df.columns = ['Código', 'Descrição', 'Marca', 'Quantidade']
    
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    
    # Bloco de Informações
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 8, f"PEDIDO / NF: {pedido.upper()}", ln=True, fill=True, border='LBRT')
    pdf.cell(0, 8, f"DATA/HORA: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, fill=True, border='LBRT')
    pdf.ln(5)
    
    # Responsáveis
    pdf.set_font("Arial", '', 10)
    pdf.cell(95, 8, f"Separador: {separador.upper()}", border=1)
    pdf.cell(95, 8, f"Conferente: {conferente.upper()}", border=1, ln=True)
    pdf.ln(8)
    
    # Tabela
    pdf.set_font("Arial", 'B', 9)
    pdf.set_fill_color(50, 50, 50)
    pdf.set_text_color(255, 255, 255)
    col_w = [30, 100, 35, 25]
    cols = ['CÓDIGO', 'DESCRIÇÃO', 'MARCA', 'QTD']
    for i in range(4): pdf.cell(col_w[i], 8, cols[i], border=1, fill=True, align='C')
    pdf.ln()
    
    # Linhas
    pdf.set_font("Arial", size=9)
    pdf.set_text_color(0, 0, 0)
    total_itens = 0
    for _, row in df.iterrows():
        pdf.cell(col_w[0], 8, str(row['Código']), border='LBR', align='C')
        desc = (str(row['Descrição'])[:45] + '..') if len(str(row['Descrição'])) > 45 else str(row['Descrição'])
        pdf.cell(col_w[1], 8, desc, border='LBR')
        pdf.cell(col_w[2], 8, str(row['Marca']), border='LBR', align='C')
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

# --- DADOS ---
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

# --- FUNÇÃO MÁGICA DE LIMPEZA (CALLBACK) ---
def limpar_tudo_clique():
    # Limpa a lista de itens
    st.session_state.conferencia = {}
    # Limpa os campos de texto forçando o estado vazio
    st.session_state.input_pedido = ""
    st.session_state.input_separador = ""
    st.session_state.input_conferente = ""
    # Reseta a mensagem
    st.session_state.msg_status = ("info", "Conferência reiniciada com sucesso.")

# --- INTERFACE ---
col_logo, col_tit = st.columns([1, 5])
with col_logo:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.header("🛠️ DF") 
with col_tit:
    st.title("Conferência Física")
    st.caption("Domínio Ferramentas - Sistema de Bipagem Rápida")

st.divider()

# --- INPUTS (COM CHAVES FIXAS) ---
c1, c2, c3 = st.columns(3)
pedido = c1.text_input("Nº Pedido / NF", placeholder="Digite...", key="input_pedido")
separador = c2.text_input("Separador", placeholder="Nome...", key="input_separador")
conferente = c3.text_input("Conferente", placeholder="Nome...", key="input_conferente")

if not (pedido and separador and conferente):
    st.info("👆 Para liberar o scanner, preencha os 3 campos acima.")
    st.stop()

st.markdown("---")

# --- SCANNER ---
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

# --- VISUALIZAÇÃO ---
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
        st.subheader("📊 Resumo")
        st.metric("Total de Peças", df_vis['Quantidade'].sum())
        st.metric("SKUs Distintos", len(df_vis))
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Checkbox para gerar PDF
        gerar_pdf = st.checkbox("🖨️ Finalizar e Gerar PDF")
        
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
        # BOTÃO LIMPAR TUDO (COM CALLBACK CORRETO)
        st.button("🗑️ LIMPAR TUDO", on_click=limpar_tudo_clique, use_container_width=True)
