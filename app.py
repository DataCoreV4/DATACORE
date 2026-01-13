import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import os
import unicodedata
from datetime import date

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(
    page_title="Data Core",
    page_icon="📊",
    layout="wide"
)

ADMIN_USER = "DCADMIN"
ADMIN_PASS = "admindatacore123!"
USERS_FILE = "users.csv"
PERMISSIONS_FILE = "permissions.csv"
CONTACT_EMAIL = "datacore.agrotech@gmail.com"
LOGO_PATH = "logo_datacore.png"

# =====================================================
# ESTILOS (DISEÑO – SOLO TEXTO)
# =====================================================
st.markdown("""
<style>
.brand-title {
    font-size: 1.3rem;
    font-weight: 700;
}
.login-title {
    font-size: 2rem;
    font-weight: 800;
    text-align: center;
}
.login-sub {
    text-align: center;
    color: #6c757d;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# DRIVE MAP (NO SE TOCA)
# =====================================================
DRIVE_MAP = {
    # ⬅️ PEGA AQUÍ EXACTAMENTE TU DRIVE_MAP COMPLETO
}

# =====================================================
# UTILIDADES MES
# =====================================================
MESES = ["Todos","Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
MESES_MAP = {m.lower():i for i,m in enumerate(MESES) if i>0}

def normalize(txt):
    return unicodedata.normalize("NFKD", txt).encode("ascii","ignore").decode().lower()

def find_mes_column(df):
    for c in df.columns:
        if "mes" in normalize(c):
            return c
    return None

def parse_mes(val):
    if pd.isna(val): return None
    if isinstance(val,(int,float)): return int(val)
    return MESES_MAP.get(str(val).lower()[:3])

# =====================================================
# DRIVE
# =====================================================
def drive_download(url):
    return f"https://drive.google.com/uc?id={url.split('/d/')[1].split('/')[0]}"

def load_csv(url):
    r = requests.get(drive_download(url))
    r.raise_for_status()
    return pd.read_csv(BytesIO(r.content), sep=";", encoding="latin1", on_bad_lines="skip", low_memory=False)

# =====================================================
# USUARIOS
# =====================================================
def init_users():
    if not os.path.exists(USERS_FILE):
        pd.DataFrame(columns=["usuario","password","rol"]).to_csv(USERS_FILE,index=False)
    df=pd.read_csv(USERS_FILE)
    df=df[df.usuario!=ADMIN_USER]
    df=pd.concat([df,pd.DataFrame([{"usuario":ADMIN_USER,"password":ADMIN_PASS,"rol":"admin"}])])
    df.to_csv(USERS_FILE,index=False)

def init_permissions():
    if not os.path.exists(PERMISSIONS_FILE):
        pd.DataFrame(columns=[
            "usuario","producto","anio","mes",
            "fecha_inicio","fecha_fin"
        ]).to_csv(PERMISSIONS_FILE,index=False)

def has_premium_access(user, producto, anio, mes):
    df = pd.read_csv(PERMISSIONS_FILE, parse_dates=["fecha_inicio","fecha_fin"])
    today = pd.to_datetime(date.today())
    df = df[
        (df.usuario==user) &
        (df.producto==producto) &
        (df.anio==anio) &
        ((df.mes=="Todos") | (df.mes==mes)) &
        (df.fecha_inicio<=today) &
        (df.fecha_fin>=today)
    ]
    return not df.empty

# =====================================================
# SESIÓN
# =====================================================
if "logged" not in st.session_state:
    st.session_state.update({"logged":False,"role":"","user":""})

# =====================================================
# AUTH + LOGO (PORTADA)
# =====================================================
def auth():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
st.image("./logo_datacore.png", width=180)
        st.markdown("<div class='login-title'>DATA CORE</div>", unsafe_allow_html=True)
        st.markdown("<div class='login-sub'>Plataforma inteligente de datos agroexportadores</div>", unsafe_allow_html=True)

    t1,t2=st.tabs(["Ingresar","Registrarse"])

    with t1:
        u=st.text_input("Usuario",key="lu")
        p=st.text_input("Contraseña",type="password",key="lp")
        if st.button("Ingresar"):
            df=pd.read_csv(USERS_FILE)
            ok=df[(df.usuario==u)&(df.password==p)]
            if not ok.empty:
                st.session_state.update({"logged":True,"role":ok.iloc[0].rol,"user":u})
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

    with t2:
        with st.form("reg"):
            d={}
            d["usuario"]=st.text_input("Usuario")
            d["password"]=st.text_input("Contraseña",type="password")
            for f in ["nombre","apellido","dni","correo","celular","empresa","cargo"]:
                d[f]=st.text_input(f.capitalize())
            if st.form_submit_button("Registrarse"):
                df=pd.read_csv(USERS_FILE)
                if d["usuario"] in df.usuario.values:
                    st.error("Usuario ya existe")
                else:
                    d["rol"]="freemium"
                    df.loc[len(df)]=d
                    df.to_csv(USERS_FILE,index=False)
                    st.success("Registro exitoso")

# =====================================================
# HEADER INTERNO (LOGO FUNCIONAL)
# =====================================================
def header():
    col1, col2, col3, col4 = st.columns([1,3,5,2])

    with col1:
       st.image("./logo_datacore.png", width=180)

    with col2:
        st.markdown("### Data Core")

    with col3:
        st.markdown(f"👤 **{st.session_state.user}**")

    with col4:
        if st.button("Cerrar sesión"):
            st.session_state.logged=False
            st.rerun()

    st.markdown("---")

# =====================================================
# DASHBOARD
# =====================================================
def dashboard():
    header()

    producto=st.selectbox("Producto",["uva","mango","arandano","limon","palta"])
    anio=st.selectbox("Año",sorted(DRIVE_MAP["envios"].keys()))
    mes=st.selectbox("Mes",MESES)

    for tipo,titulo in [("envios","📦 Envíos"),("campo","🌾 Campos certificados")]:
        st.subheader(titulo)
        try:
            df=load_csv(DRIVE_MAP[tipo][anio][producto])
            mc=find_mes_column(df)
            if mc and mes!="Todos":
                df["_mes"]=df[mc].apply(parse_mes)
                df=df[df["_mes"]==MESES_MAP[mes.lower()]]

            full_access = (
                st.session_state.role=="admin" or
                (st.session_state.role=="premium" and has_premium_access(
                    st.session_state.user, producto, anio, mes))
            )

            st.dataframe(df if full_access else df.head(3))

            if not full_access:
                st.markdown("🔓 **Acceso completo disponible**")
                st.link_button(
                    "📩 Solicitar acceso completo",
                    f"mailto:{CONTACT_EMAIL}?subject=Acceso {tipo.upper()} {producto} {anio}"
                )
        except:
            st.info("📌 Información en proceso de mejora")

# =====================================================
# MAIN
# =====================================================
init_users()
init_permissions()
auth() if not st.session_state.logged else dashboard()
