import re
import nltk
import sqlite3
import stanza
from metadata import titles

nlp = stanza.Pipeline('ru', processors='tokenize,lemma,pos')

conn = sqlite3.connect('corpus.db')
cursor = conn.cursor()

# Создание таблицы для предложений
cursor.execute('''
    CREATE TABLE sentences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        original_sentence TEXT,
        clean_sentence TEXT,
        work_title TEXT,
        source TEXT
    )
''')

conn.commit()

# Создание таблицы для токенов
cursor.execute('''
    CREATE TABLE tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sentence_id INTEGER,
        token TEXT,
        lemma TEXT,
        pos TEXT,
        FOREIGN KEY (sentence_id) REFERENCES sentences (id)
    )
''')

conn.commit()

# Создание индексов
cursor.execute('CREATE INDEX idx_token ON tokens (token)')
cursor.execute('CREATE INDEX idx_lemma ON tokens (lemma)')
cursor.execute('CREATE INDEX idx_pos ON tokens (pos)')
cursor.execute('CREATE INDEX idx_token_pos ON tokens (token, pos)')
conn.commit()

def split_into_sentences(text):
    """
    Разделяет текст на предложения
    """
    sentences = nltk.sent_tokenize(text, language='russian')
    return sentences

def clean_text(text):
    """
    Удаляет знаки пунктуацию, кроме дефисов;
    оставляет буквы (русские и латинские) и цифры
    """
    cleaned_text = re.sub(r'[^a-zA-Zа-яА-ЯёЁ0-9\s-]', '', text)
    return cleaned_text

def save_morph(sentence):
    """
    Проводит морфологический анализ
    """
    doc = nlp(sentence)
    tokens_data = []
    
    for sent in doc.sentences:
        for token in sent.words:
            if token.upos == 'PUNCT':
                continue
            
            token_text = (token.text.lower() if token.text[0].isupper()
                          else token.text)
            lemma = (token.lemma.lower() if token.lemma[0].isupper()
                     else token.lemma)

            tokens_data.append((token_text, lemma, token.upos))

    return tokens_data

def insert_data_into_db(txt_file, title, url):
    """
    Вставляет данные в таблицы БД
    """    
    with open(txt_file, 'r', encoding='utf-8') as file:
        text = file.read()

    sentences = split_into_sentences(text)
    
    for sentence in sentences:
        # Проводим морфологический анализ
        tokens_data = save_morph(sentence)

        # Очищаем предложение и приводим их к нижнему регистру для записи
        clean_sent = clean_text(sentence).lower()

        cursor.execute('''
            INSERT INTO sentences (
                original_sentence, clean_sentence, work_title, source
            )
            VALUES (?, ?, ?, ?)
        ''', (sentence, clean_sent, title, url))

        # Получаем ID вставленных предложений
        sentence_id = cursor.lastrowid

        # Вставляем токены с заполнением sentence_id
        for token_text, lemma, pos in tokens_data:
            cursor.execute('''
                INSERT INTO tokens (sentence_id, token, lemma, pos)
                VALUES (?, ?, ?, ?)
            ''', (sentence_id, token_text, lemma, pos))

    conn.commit()

for title, url in titles.items():
    file_dir = f'./texts/{title}.txt'
    insert_data_into_db(file_dir, title, url)
