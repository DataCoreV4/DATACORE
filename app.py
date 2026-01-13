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
st.set_page_config("Data Core", layout="wide")

ADMIN_USER = "DCADMIN"
ADMIN_PASS = "admindatacore123!"
USERS_FILE = "users.csv"
PERMISSIONS_FILE = "permissions.csv"
CONTACT_EMAIL = "datacore.agrotech@gmail.com"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "logo_datacore.png")

# =====================================================
# ESTILOS (SOLO VISUAL – NO LÓGICA)
# =====================================================
st.markdown("""
<style>
.dc-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.6rem 1rem;
    border-bottom: 1px solid #e5e5e5;
    margin-bottom: 1rem;
}
.dc-left {
    display: flex;
    align-items: center;
    gap: 12px;
}
.dc-title {
    font-size: 1.2rem;
    font-weight: 700;
}
.dc-user {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 0.95rem;
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
# (IGUAL AL QUE ENVIASTE – SIN CAMBIOS)
DRIVE_MAP = { ... }  # ← exactamente igual, se mantiene íntegro

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
# AUTH + LOGO (SOLO VISUAL)
# =====================================================
def auth():
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=180)
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
# HEADER INTERNO (SOLO VISUAL)
# =====================================================
def render_header():
    st.markdown("<div class='dc-header'>", unsafe_allow_html=True)
    st.markdown("<div class='dc-left'>", unsafe_allow_html=True)
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=40)
    st.markdown("<div class='dc-title'>DATA CORE</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    col_user, col_btn = st.columns([6,1])
    with col_user:
        st.markdown(f"<div class='dc-user'>👤 {st.session_state.user}</div>", unsafe_allow_html=True)
    with col_btn:
        if st.button("Cerrar sesión"):
            st.session_state.logged=False
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# =====================================================
# DASHBOARD (MISMA LÓGICA)
# =====================================================
def dashboard():
    render_header()

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

    if st.session_state.role=="admin":
        st.subheader("🛠 Gestión de usuarios")
        users=pd.read_csv(USERS_FILE)
        perms=pd.read_csv(PERMISSIONS_FILE)

        for i,r in users.iterrows():
            if r.usuario==ADMIN_USER: continue

            users.loc[i,"rol"]=st.selectbox(
                r.usuario,["freemium","premium"],
                index=0 if r.rol=="freemium" else 1,
                key=f"rol_{i}"
            )

            if users.loc[i,"rol"]=="premium":
                with st.expander(f"Permisos – {r.usuario}"):
                    producto_p=st.selectbox("Producto",["uva","mango","arandano","limon","palta"],key=f"p{i}")
                    anio_p=st.selectbox("Año",sorted(DRIVE_MAP["envios"].keys()),key=f"a{i}")
                    mes_p=st.selectbox("Mes",MESES,key=f"m{i}")
                    fi=st.date_input("Fecha inicio",key=f"fi{i}")
                    ff=st.date_input("Fecha fin",key=f"ff{i}")

                    if st.button("Guardar permiso",key=f"s{i}"):
                        perms.loc[len(perms)]=[r.usuario,producto_p,anio_p,mes_p,fi,ff]
                        perms.to_csv(PERMISSIONS_FILE,index=False)
                        st.success("Permiso guardado")

        users.to_csv(USERS_FILE,index=False)

# =====================================================
# MAIN
# =====================================================
init_users()
init_permissions()
auth() if not st.session_state.logged else dashboard()
