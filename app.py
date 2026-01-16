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

# =====================================================
# DRIVE MAP (NO SE TOCA)
# =====================================================
DRIVE_MAP = {
    "envios": {
        2021: {
            "uva": "https://drive.google.com/file/d/1I-g0aN3KIgKRzCoT5cR24djQUwakhJxF/view",
            "mango": "https://drive.google.com/file/d/1k6CxjPufa0YF17e264BI8NYO1rFFZuc7/view",
            "arandano": "https://drive.google.com/file/d/1CyFQu-BdYNxFSoed9SGvKnkimrJjS2Q9/view",
            "limon": "https://drive.google.com/file/d/1--9cfYzrB2giYCy5khZmqXdXL_46Zuz8/view",
            "palta": "https://drive.google.com/file/d/1-BK3uEDMAMrTAdqxMJd-pIYCg0Rp-8kJ/view",
        },
        2022: {
            "uva": "https://drive.google.com/file/d/1wHxIXmn2stnjdFSnu8spnOSDw9Q45Dti/view",
            "mango": "https://drive.google.com/file/d/1kjtC1QVGe4w3GWEYhMmB9VD98eYjhvPh/view",
            "arandano": "https://drive.google.com/file/d/1tJRlp3FWvYZBr3LFPV1PFke3o6LZcOfa/view",
            "limon": "https://drive.google.com/file/d/1HfO0jh0yPXK99P8mQ080KLEevc4QVnLT/view",
            "palta": "https://drive.google.com/file/d/1IYS7yUDFmeCw3YyCIgKDbayZ63AORHvf/view",
        },
        2023: {
            "uva": "https://drive.google.com/file/d/1SZjCd3ANa4CF0N0lK_mnOQfzn0-ywTLs/view",
            "mango": "https://drive.google.com/file/d/1S5mMR3nG_DeH3ZpOqAvcjidzPQMW8kw_/view",
            "arandano": "https://drive.google.com/file/d/1JhAhZi3roOQpw5ejm3jnW5Av59De8wc2/view",
            "limon": "https://drive.google.com/file/d/1sGnvph11F431fg5v9c8qzoH-Yxytffti/view",
            "palta": "https://drive.google.com/file/d/1MCaBirErsv3PeJZ4soi2Fszw8QcJbg7w/view",
        },
        2024: {
            "uva": "https://drive.google.com/file/d/1csIY-AT7Uw6QFp49SANyHALHuZO3r65n/view",
            "mango": "https://drive.google.com/file/d/1In6_xnpKZwD1zTG4JrD3uhk7sYNKU4qF/view",
            "arandano": "https://drive.google.com/file/d/1CZSWhLV-STPw9k90cOVzQxJ0V2k7ZTUa/view",
            "limon": "https://drive.google.com/file/d/1XxGB8PGI4yh5K5mO5qGqRnSK_Fe2nPAX/view",
            "palta": "https://drive.google.com/file/d/1mLNGjAunM6HTiCnJIgEoaqZQEuegfSf9/view",
        },
        2025: {
            "uva": "https://drive.google.com/file/d/1iw-OafOHph_epXgf-6kreXhq2GxzNqyN/view",
            "mango": "https://drive.google.com/file/d/1-f5tlde1nBJnl_9BbRJkaDpGBleYtbyG/view",
            "arandano": "https://drive.google.com/file/d/1TxC9TwgFojnNRkQlOI27KJBzG0TK7tp7/view",
            "limon": "https://drive.google.com/file/d/1G8VbTnSeOcJJVDRkze9s12TRts5BvQx6/view",
            "palta": "https://drive.google.com/file/d/1Qt680UXFnKBh7bdV0iGqnJKKmc1suNVA/view",
        },
    },
    "campo": {
        2021: {
            "uva": "https://drive.google.com/file/d/1k6OMQxl7B3hVY9OVECc9UlYcytIjpN1A/view",
            "mango": "https://drive.google.com/file/d/1JX50r2NJYG3HjalUTZ5pCHmbD5DXQDUu/view",
            "arandano": "https://drive.google.com/file/d/1HOKP2FaW9UPRYyA7tIj0oSnGzUhkb3h4/view",
            "limon": "https://drive.google.com/file/d/12xOZVXqxvvepb97On1H8feKUoW_u1Qet/view",
            "palta": "https://drive.google.com/file/d/1ckjszJeuyPQS6oVNeWFd-FwoM8FTalHO/view",
        },
        2022: {
            "uva": "https://drive.google.com/file/d/1LS_80bCCgGE4flJ2BEzav1XeQQSrSX1y/view",
            "mango": "https://drive.google.com/file/d/16CDM3zQnH3S5n2SNjqwJmk0oUGkbxtJS/view",
            "arandano": "https://drive.google.com/file/d/1WTkBElLqv3aLQ8s2rkmlQqHM1zsKE33-/view",
            "limon": "https://drive.google.com/file/d/123wwsJLNrvlTxh2VRZQy1JpVOjI9Oj32/view",
            "palta": "https://drive.google.com/file/d/1uIs_MXnilSoPIGhtJtmOCv8N8un2VoFg/view",
        },
        2023: {
            "uva": "https://drive.google.com/file/d/11sb54WtgNe0poLSR4q-nEGvjMdbnjXiq/view",
            "mango": "https://drive.google.com/file/d/1qV3zoDQNnzeEvQR0eZ0FnrvxdkuruyUM/view",
            "arandano": "https://drive.google.com/file/d/1jdNrMyVcW2HV5PJI63_A_oxl6xLpapl7/view",
            "limon": "https://drive.google.com/file/d/1F708yJNg3mzrdHi53Dmw4RQZkTqUh4YH/view",
            "palta": "https://drive.google.com/file/d/1ZBXYrxS4iJ-lUBPKAMtr4ZIWGf6Wh6ED/view",
        },
        2024: {
            "uva": "https://drive.google.com/file/d/15CoNL-b9tONKTjbj2rIy8cthyeVhsD_F/view",
            "mango": "https://drive.google.com/file/d/1T6OVYHVN6j57Km9Z8zWrKYMlzTUIeRes/view",
            "arandano": "https://drive.google.com/file/d/1YejBbqWi383QjeJntU-AaICQw0TOJyaV/view",
            "limon": "https://drive.google.com/file/d/1JH6oXdDP5z-JAQgu9WvT-ej1pCjnX6WS/view",
            "palta": "https://drive.google.com/file/d/1fxh3QgnZXzjkuqmwG4w9h1YjhK6PPvX9/view",
        },
        2025: {
            "uva": "https://drive.google.com/file/d/15R-9ECTNpSQM1FC8tFPUs0emE16H8cHT/view",
            "mango": "https://drive.google.com/file/d/11IziWG98PfqkSyTaK5GvKwU4NEC9LwXJ/view",
            "arandano": "https://drive.google.com/file/d/15w2FG2TT_qPfxEksBgcGbfPu67yNbvYT/view",
            "limon": "https://drive.google.com/file/d/178kHRjqLgs-EFUmzCsNclBKq-nYmVJPO/view",
            "palta": "https://drive.google.com/file/d/1fo9HKY9DSKAjgLVKsx2H0Y7f_YU4DwRT/view",
        },
    }
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
# AUTH + REGISTRO
# =====================================================
def auth():
    st.title("🔐 Data Core – Acceso")
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
            else: st.error("Usuario o contraseña incorrectos")

    with t2:
        with st.form("reg"):
            d={}
            d["usuario"]=st.text_input("Usuario")
            d["password"]=st.text_input("Contraseña",type="password")
            for f in ["nombre","apellido","dni","correo","celular","empresa","cargo"]:
                d[f]=st.text_input(f.capitalize())
            if st.form_submit_button("Registrarse"):
                df=pd.read_csv(USERS_FILE)
                if d["usuario"] in df.usuario.values: st.error("Usuario ya existe")
                else:
                    d["rol"]="freemium"
                    df.loc[len(df)]=d
                    df.to_csv(USERS_FILE,index=False)
                    st.success("Registro exitoso")

# =====================================================
# DASHBOARD
# =====================================================
def dashboard():
    st.markdown(f"👋 **Bienvenido, {st.session_state.user}**")
    if st.button("Cerrar sesión"):
        st.session_state.logged=False
        st.rerun()

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
