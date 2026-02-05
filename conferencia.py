import streamlit as st
import pandas as pd
import io
import shutil
import os

# --- CONFIGURAÇÃO DA PÁGINA E ESTILO DOMÍNIO FERRAMENTAS ---
st.set_page_config(page_title="Conferência - Domínio Ferramentas", layout="wide")

COR_PRIMARIA = "#FF6600"
COR_FUNDO = "#1E1E1E"
COR_TEXTO = "#FFFFFF"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {COR_FUNDO}; color: {COR_TEXTO}; }}
    .stTextInput > div > div > input {{
        font-size: 20px; text-align: center; border: 2px solid {COR_PRIMARIA}; color: #333;
    }}
    div[data-testid="metric-container"] {{
        background-color: #2b2b2b; border-left: 5px solid {COR_PRIMARIA}; padding: 10px; border-radius: 5px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- CABEÇALHO ---
col_logo, col_titulo = st.columns([1, 5])
with col_logo:
    st.markdown(f"## 🛠️ DF") 
with col_titulo:
    st.title("Conferência - Domínio Ferramentas")
    st.caption("Sistema de Bipagem Inteligente e Contagem Automática")

st.divider()

# --- LÓGICA DE DADOS (COM TRATAMENTO DE .0) ---

@st.cache_data
def carregar_base():
    arquivo = "produtos.xlsx"
    if not os.path.exists(arquivo):
        return None
    
    try:
        # Cópia temporária para evitar erro de permissão (OneDrive/Excel)
        temp_arquivo = "temp_produtos.xlsx"
        shutil.copy2(arquivo, temp_arquivo)
        
        df = pd.read_excel(temp_arquivo)
        if os.path.exists(temp_arquivo):
            os.remove(temp_arquivo)
        
        df.columns = df.columns.str.lower()
        
        def limpar_codigo(val):
            if pd.isna(val): return ""
            s = str(val).strip()
            if s.endswith('.0'): s = s[:-2]
            return s

        if 'codigo' in df.columns:
            df['codigo'] = df['codigo'].apply(limpar_codigo)
        
        return df
    except Exception as e:
        st.error(f"Erro ao acessar planilha: {e}")
        return None

base_produtos = carregar_base()

if 'conferencia' not in st.session_state:
    st.session_state.conferencia = {} 
if 'mensagem_status' not in st.session_state:
    st.session_state.mensagem_status = ("info", "Aguardando scanner...")

def processar_bip():
    codigo_original = st.session_state.input_bip.strip()
    # Limpa o código bipado para bater com a base (remove .0 se o scanner mandar)
    codigo_limpo = codigo_original[:-2] if codigo_original.endswith('.0') else codigo_original
    
    if not codigo_limpo: return

    if base_produtos is not None:
        produto = base_produtos[base_produtos['codigo'] == codigo_limpo]
        
        if not produto.empty:
            item = produto.iloc[0]
            desc = item['descricao']
            marca = item['marca'] if 'marca' in item else '-'
            
            if codigo_limpo in st.session_state.conferencia:
                st.session_state.conferencia[codigo_limpo]['qtd'] += 1
                st.session_state.mensagem_status = ("success", f"➕ Atualizado: {desc}")
            else:
                st.session_state.conferencia[codigo_limpo] = {'desc': desc, 'marca': marca, 'qtd': 1}
                st.session_state.mensagem_status = ("success", f"✅ Adicionado: {desc}")
        else:
            st.session_state.mensagem_status = ("error", f"❌ Não cadastrado: {codigo_original}")
    
    st.session_state.input_bip = ""

# --- INTERFACE ---

if base_produtos is None:
    st.warning("⚠️ Arquivo 'produtos.xlsx' não encontrado na pasta.")
else:
    st.text_input("Bipe o código:", key="input_bip", on_change=processar_bip, placeholder="Aguardando scanner...")

    tipo, msg = st.session_state.mensagem_status
    if tipo == "success": st.success(msg)
    elif tipo == "error": st.error(msg)
    else: st.info(msg)

    st.divider()

    if st.session_state.conferencia:
        # Prepara os dados para a tabela
        df_vis = pd.DataFrame.from_dict(st.session_state.conferencia, orient='index')
        df_vis.reset_index(inplace=True)
        df_vis.columns = ['Código', 'Descrição', 'Marca', 'Quantidade']
        
        col_tabela, col_resumo = st.columns([3, 1])
        
        with col_tabela:
            st.subheader("📦 Itens na Conferência")
            st.dataframe(df_vis, use_container_width=True, hide_index=True)

        with col_resumo:
            st.subheader("📊 Resumo")
            # Métricas solicitadas de volta
            st.metric("Total de Peças", df_vis['Quantidade'].sum())
            st.metric("Produtos Distintos (SKUs)", len(df_vis))
            
            st.write("") # Espaçador
            
            if st.button("🗑️ Limpar Conferência", type="primary", use_container_width=True):
                st.session_state.conferencia = {}
                st.rerun()
            
            # Download em Excel
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_vis.to_excel(writer, index=False)
            
            st.download_button(
                label="📥 Baixar Relatório",
                data=buffer.getvalue(),
                file_name="conferencia_dominio.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    else:
        st.info("Nenhum item bipado ainda.")