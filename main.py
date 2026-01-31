import streamlit as st
import folium
from streamlit_folium import st_folium, folium_static
from folium.plugins import MarkerCluster
from geopy.geocoders import Nominatim
import pandas as pd

st.set_page_config(
    page_title="streamlit-folium documentation",
    page_icon=":world_map:️",
    layout="wide",
)

def get_lat_long(location_name):
    # Initialize Nominatim API with a unique user agent
    # The 'user_agent' parameter is required by the Nominatim service
    geolocator = Nominatim(user_agent="my_geocoder_app")

    # Use the geocode method to get location details
    location = geolocator.geocode(location_name)

    if location:
        latitude = location.latitude
        longitude = location.longitude
        return latitude, longitude
    else:
        return None

def create_map(locais):
    m = folium.Map(location=[-23.55, -46.63], zoom_start=12)
    marker_cluster = MarkerCluster().add_to(m)

    for _, local in locais.iterrows():
        nome_busca=local.endereco+", "+local.cidade+", "+local.estado
        acessibilidade = "<h3>"+local.evento+"<br><br><h4>Espaço: "+local.espaco+"<br>Audiodescrição: "+local.audiodescricao+"<br>LIBRAS: "+local.libras+"<br>Obra tátil: "+local.obra_tatil
        lat_long=get_lat_long(nome_busca)
        if lat_long:
            folium.Marker(location=lat_long, tooltip=local.nome, popup=folium.Popup(acessibilidade, max_width=200)).add_to(marker_cluster)
        else:
            print(local.nome)

    return m

espacos = pd.read_excel("https://docs.google.com/spreadsheets/d/15m2m4X90XtI5ycZ58wu5xUz5_NTXp82_CJuK_ntkd5U/export?format=xlsx", sheet_name="espacos")
eventos = pd.read_excel("https://docs.google.com/spreadsheets/d/15m2m4X90XtI5ycZ58wu5xUz5_NTXp82_CJuK_ntkd5U/export?format=xlsx", sheet_name="eventos")
classificacoes = pd.read_excel("https://docs.google.com/spreadsheets/d/15m2m4X90XtI5ycZ58wu5xUz5_NTXp82_CJuK_ntkd5U/export?format=xlsx", sheet_name="classificacoes")
tipos = pd.read_excel("https://docs.google.com/spreadsheets/d/15m2m4X90XtI5ycZ58wu5xUz5_NTXp82_CJuK_ntkd5U/export?format=xlsx", sheet_name="tipos")

eventos["inicio"] = pd.to_datetime(eventos["inicio"], format="%d/%m/&Y")
eventos["fim"] = pd.to_datetime(eventos["fim"], format="%d/%m/&Y")
hoje = pd.Timestamp.now().normalize()
eventos["ativo"] = (eventos["inicio"]<=hoje) & (eventos["fim"]>=hoje)

eventos = eventos.merge(espacos, left_on="local", right_on="id", how="left")
classificacoes = classificacoes.set_index("id")["classificacao"].to_dict()
eventos["espaco"] = eventos["espaco"].map(classificacoes)
eventos["audiodescricao"] = eventos["audiodescricao"].map(classificacoes)
eventos["libras"] = eventos["libras"].map(classificacoes)
eventos["obra_tatil"] = eventos["obra_tatil"].map(classificacoes)
st.title("Brasilcessível")
st.subheader("A sua plataforma de acessibilidade cultural")

tipos = tipos.set_index("id")["tipo"].to_dict()
eventos["tipo"] = eventos["tipo"].map(tipos)

left, right = st.columns(2)

acessibilidades_validas = ["Não aplicável", "Parcialmente acessível", "Totalmente acessível"]

with left:
    filtros = st.columns(4)
    eh_ativo = filtros[0].toggle("Apenas ativos", True)
    tipo_evento = filtros[1].selectbox("Tipo de evento", ["Todos"]+list(tipos.values()), 0)
    tipo_acessibilidade = filtros[2].selectbox("Tipo de acessibilidade", ["Qualquer", "Espaço", "Audiodescrição", "LIBRAS", "Obra tátil"], 0)

    if eh_ativo:
        eventos = eventos[eventos["ativo"]]
    if tipo_evento != "Todos":
        eventos = eventos[eventos["tipo"] == tipo_evento]
    if tipo_acessibilidade != "Qualquer":
        if tipo_acessibilidade == "Espaço":
            eventos = eventos[eventos["espaco"].isin(acessibilidades_validas)]
        if tipo_acessibilidade == "Audiodescrição":
            eventos = eventos[eventos["audiodescricao"].isin(acessibilidades_validas)]
        if tipo_acessibilidade == "LIBRAS":
            eventos = eventos[eventos["libras"].isin(acessibilidades_validas)]
        if tipo_acessibilidade == "Obra tátil":
            eventos = eventos[eventos["obra_tatil"].isin(acessibilidades_validas)]
    for _, evento in eventos.iterrows():
        with st.expander(evento.evento):
            st.write(evento.descricao)
with right:
    m=create_map(eventos)
    st_data = folium_static(m)

