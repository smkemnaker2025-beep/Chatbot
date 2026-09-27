
import os
import json
from pathlib import Path

import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from google import genai


# ============================================================
# KONFIGURASI HALAMAN
# ============================================================

st.set_page_config(
    page_title="MechaBot - CNC Milling",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# PATH KNOWLEDGE BASE
# ============================================================

# Lokasi knowledge base khusus Google Colab
KB_PATH = (
    Path(__file__).resolve().parent
    / "data"
    / "knowledge_base.json"
)


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM = """
Kamu adalah MechaBot, chatbot pembelajaran CNC Milling
untuk peserta pelatihan Teknik Manufaktur.

Gunakan Bahasa Indonesia yang santai, ramah, jelas, dan mudah
dipahami peserta pelatihan.

Jangan menggunakan bahasa yang terlalu kaku atau terlalu formal.

Selalu gunakan nama peserta jika nama peserta tersedia dalam
percakapan.

Contoh:
"Halo Budi, ..."
"Baik Budi, ..."
"Kalau untuk bagian ini, Budi, ..."

Gunakan istilah teknis CNC Milling sesuai modul pembelajaran.

Jika menjelaskan prosedur, gunakan langkah-langkah bernomor.

Jika menjelaskan istilah teknis, berikan penjelasan sederhana
terlebih dahulu kemudian istilah teknisnya.

Prioritaskan informasi dari modul pembelajaran CNC Milling
yang diberikan sebagai sumber pengetahuan.

Jika informasi tidak tersedia dalam modul, katakan:

"Informasi tersebut belum tersedia di modul pembelajaran
yang digunakan."

Jika memberikan pengetahuan di luar modul, tandai dengan:

"Pengetahuan tambahan:"

Untuk materi yang berkaitan dengan pengoperasian mesin secara
nyata, selalu tekankan K3, SOP, dan arahan instruktur.

Jangan mengklaim telah melihat atau memeriksa kondisi mesin
secara langsung.

Jangan mengklaim dapat mengendalikan mesin CNC.

Jawaban harus komunikatif dan tidak terlalu panjang kecuali
peserta meminta penjelasan lebih detail.

Sumber modul:
Buku Informasi Pengoperasian Mesin CNC Milling.
"""


# ============================================================
# CEK KNOWLEDGE BASE
# ============================================================

if not KB_PATH.exists():

    st.error(
        "❌ Knowledge base tidak ditemukan.\n\n"
        f"File yang dicari:\n`{KB_PATH}`\n\n"
        "Pastikan file knowledge_base.json berada di "
        "`/content/data/`."
    )

    st.stop()


# ============================================================
# LOAD KNOWLEDGE BASE
# ============================================================

@st.cache_resource
def load_kb(kb_file, modified_time):

    path = Path(kb_file)

    data = json.loads(
        path.read_text(encoding="utf-8")
    )

    chunks = data["chunks"]

    corpus = [
        f"{c.get('section', '')} {c.get('text', '')}"
        for c in chunks
    ]

    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        max_features=1500
    )

    matrix = vectorizer.fit_transform(corpus)

    return data, chunks, vectorizer, matrix


# Waktu modifikasi knowledge base
KB_MTIME = KB_PATH.stat().st_mtime

data, chunks, vectorizer, matrix = load_kb(
    str(KB_PATH),
    KB_MTIME
)


# ============================================================
# FUNGSI RETRIEVAL
# ============================================================

def retrieve(query, k=5):

    qv = vectorizer.transform([query])

    scores = (
        matrix @ qv.T
    ).toarray().ravel()

    indices = scores.argsort()[::-1][:k]

    results = []

    for idx in indices:

        if scores[idx] <= 0:
            continue

        results.append(
            {
                "score": float(scores[idx]),
                "section": chunks[idx].get(
                    "section",
                    ""
                ),
                "text": chunks[idx].get(
                    "text",
                    ""
                )
            }
        )

    return results


# ============================================================
# GEMINI API
# ============================================================

GEMINI_API_KEY = os.environ.get(
    "GEMINI_API_KEY"
)

GEMINI_MODEL = os.environ.get(
    "GEMINI_MODEL",
    "gemini-3.8-flash"
)

if not GEMINI_API_KEY:

    st.error(
        "❌ GEMINI_API_KEY belum tersedia."
    )

    st.stop()


client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# SESSION STATE
# ============================================================

if "participant_name" not in st.session_state:

    st.session_state.participant_name = ""


if "messages" not in st.session_state:

    st.session_state.messages = []


if "greeted" not in st.session_state:

    st.session_state.greeted = False


# ============================================================
# HEADER
# ============================================================

st.title("🤖 MechaBot")

st.subheader(
    "Asisten Pembelajaran CNC Milling"
)

st.caption(
    "Teman belajar peserta pelatihan Teknik Manufaktur"
)


# ============================================================
# NAMA PESERTA
# ============================================================

if not st.session_state.participant_name:

    st.info(
        "👋 Sebelum mulai belajar, "
        "MechaBot ingin mengenal kamu terlebih dahulu."
    )

    name = st.text_input(
        "Nama Peserta Pelatihan",
        placeholder="Masukkan nama lengkap kamu...",
        key="name_input"
    )

    if st.button(
        "🚀 Mulai Belajar",
        use_container_width=True
    ):

        if name.strip():

            st.session_state.participant_name = (
                name.strip()
            )

            st.session_state.messages = []

            st.session_state.greeted = False

            st.rerun()

        else:

            st.warning(
                "Silakan masukkan nama terlebih dahulu."
            )

    st.stop()


# ============================================================
# SAPAAN AWAL
# ============================================================

if not st.session_state.greeted:

    participant = (
        st.session_state.participant_name
    )

    greeting = f"""
### 👋 Halo, {participant}!

Selamat datang di **MechaBot** 🤖

Saya siap menemani kamu belajar tentang
**Pengoperasian Mesin CNC Milling**.

Kamu bisa bertanya tentang materi CNC Milling,
atau gunakan salah satu **pertanyaan cepat** di sebelah kiri.

Yuk mulai belajar, {participant}! 💪
"""

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": greeting
        }
    )

    st.session_state.greeted = True


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("🤖 MechaBot")

    st.write(
        f"Peserta: **{st.session_state.participant_name}**"
    )

    st.divider()

    st.subheader("💡 Pertanyaan Cepat")

    # HANYA 3 PERTANYAAN
    quick_questions = [
        "Apa itu CNC Milling?",
        "Apa fungsi sumbu X, Y dan Z?",
        "Apa saja persiapan sebelum mengoperasikan CNC?"
    ]

    for question in quick_questions:

        if st.button(
            question,
            use_container_width=True
        ):

            st.session_state.quick_question = (
                question
            )

    st.divider()

    if st.button(
        "🔄 Mulai Percakapan Baru",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.session_state.greeted = False

        st.rerun()

    if st.button(
        "👤 Ganti Nama Peserta",
        use_container_width=True
    ):

        st.session_state.participant_name = ""

        st.session_state.messages = []

        st.session_state.greeted = False

        st.rerun()


# ============================================================
# TAMPILKAN RIWAYAT CHAT
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# ============================================================
# INPUT CHAT
# ============================================================

prompt = st.chat_input(
    "💬 Ketik pertanyaan tentang CNC Milling..."
)


# Pertanyaan dari tombol cepat
if "quick_question" in st.session_state:

    prompt = st.session_state.quick_question

    del st.session_state.quick_question


# ============================================================
# PROSES PERTANYAAN
# ============================================================

if prompt:

    participant = (
        st.session_state.participant_name
    )

    # --------------------------------------------------------
    # SIMPAN PERTANYAAN PESERTA
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):

        st.markdown(prompt)


    # --------------------------------------------------------
    # RETRIEVE INFORMASI DARI MODUL
    # --------------------------------------------------------

    results = retrieve(
        prompt,
        k=5
    )


    if results:

        context_parts = []

        for item in results:

            context_parts.append(
                f"""
Bagian: {item['section']}

{item['text']}
"""
            )

        context = "\n\n".join(
            context_parts
        )

    else:

        context = (
            "Tidak ditemukan informasi yang "
            "relevan dalam modul."
        )


    # --------------------------------------------------------
    # PROMPT UNTUK GEMINI
    # --------------------------------------------------------

    user_prompt = f"""
Nama peserta: {participant}

Pertanyaan peserta:

{prompt}


Konteks dari modul pembelajaran:

{context}


Jawab pertanyaan peserta dengan Bahasa Indonesia
yang santai, ramah, dan mudah dipahami.

Sapa peserta menggunakan namanya secara natural
jika sesuai dengan konteks jawaban.

Prioritaskan informasi dari modul.

Jika informasi tidak tersedia dalam konteks,
jangan mengarang.

Jika memberikan informasi tambahan di luar modul,
gunakan label:

"Pengetahuan tambahan:"
"""


    # --------------------------------------------------------
    # PANGGIL GEMINI
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner(
            "🤖 MechaBot sedang mencari jawaban..."
        ):

            try:

                response = client.models.generate_content(

                    model=GEMINI_MODEL,

                    contents=user_prompt,

                    config={
                        "system_instruction": SYSTEM,
                        "temperature": 0.2,
                        "max_output_tokens": 1400
                    }
                )

                answer = response.text

            except Exception as e:

                answer = (
                    "Maaf, saya sedang mengalami "
                    "masalah saat menghubungi Gemini API.\n\n"
                    f"Detail error: `{e}`"
                )

        st.markdown(answer)


    # --------------------------------------------------------
    # SIMPAN JAWABAN
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "⚠️ Untuk pengoperasian mesin secara nyata, "
    "ikuti SOP K3 dan arahan instruktur."
)

st.caption(
    "Sumber: Buku Informasi Pengoperasian Mesin CNC Milling."
)
