import os
from enum import Enum

import requests
import streamlit as st


class Categorias(Enum):
    MANIPULACION = "Manipulacion Datos", "🧰"
    VALIDACION = "Validacion Datos", "✅"
    VISUALIZACION = "Visualización y gráficas", "📊"
    BASEDATOS = "Bases de Datos", "📚"
    WEB = "Web frameworks", "🕸"

    def __new__(cls, value: str, icon: str):
        entry = object.__new__(cls)
        entry._value_ = value
        entry.icon = icon  # type: ignore[attr-defined]
        return entry


def format_output_text(text: str, n: int = 11, method: str = "word") -> str:
    if method == "word":
        words = text.split()
        out = ""
        word_count = 0
        for word in words:
            out += word + " "
            word_count += 1
            if word_count == n:
                out += "\n"
                word_count = 0
        return out
    elif method == "character":
        import re

        return "\n ".join(re.findall(".{n}", text))


def get_google_url_img_proyecto(nombre_proyecto: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0"}
    cookies = {"CONSENT": "YES+cb.20210720-07-p0.en+FX+410"}
    response = requests.get(
        f"https://www.google.com/search?q={nombre_proyecto}+logo&source=lnms&tbm=isch&sa=X&ved=2ahUKEwie44_AnqLpAhUhBWMBHUFGD90Q_AUoAXoECBUQAw&biw=1920&bih=947",
        headers=headers,
        cookies=cookies,
    )
    # TODO: https://github.com/ohyicong/Google-Image-Scraper
    return None


@st.cache_data
def load_css(file_name=f"{os.getcwd()}/st_app/style.css"):
    with open(file_name) as f:
        css = f"<style>{f.read()}</style>"
    return css
