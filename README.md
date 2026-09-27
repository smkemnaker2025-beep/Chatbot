# MechaBot - CNC Milling

MechaBot adalah chatbot pembelajaran untuk membantu peserta pelatihan mempelajari Pengoperasian Mesin CNC Milling.

## Fitur

- Chatbot pembelajaran CNC Milling
- Peserta memasukkan nama sebelum mulai belajar
- Bahasa Indonesia santai
- 3 pertanyaan cepat
- Knowledge Base berdasarkan modul CNC Milling
- Menggunakan Google Gemini
- Antarmuka Streamlit

## Struktur proyek

MechaBot-CNC-Milling/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── data/
│   └── knowledge_base.json
└── Buku Informasi Pengoperasian Mesin CNC Milling.docx

## Menjalankan

pip install -r requirements.txt
streamlit run app.py

## API Key

API Key Gemini tidak disimpan di repository.
Gunakan environment variable atau Streamlit Secrets.

## Sumber Materi

Buku Informasi Pengoperasian Mesin CNC Milling.