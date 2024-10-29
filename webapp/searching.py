import os
import pymorphy3
import sqlite3

morph = pymorphy3.MorphAnalyzer()

base_dir = os.path.dirname(os.path.abspath(__file__))
path_to_db = os.path.join(base_dir, 'instance', 'corpus.db')

def process_tokens(tokens):
    """
    Приводит токены к нижнему регистру, если они не являются POS-тегами.
    Проверяет длину списка токенов из запроса.
    Возвращает список обработанных токенов.
    """
    pos_tags = [
        'ADJ', 'ADP', 'ADV', 'AUX', 'CCONJ', 'DET', 
        'INTJ', 'NOUN', 'NUM', 'PART', 'PRON', 'PROPN', 
        'SCONJ', 'VERB', 'X'
    ]
    
    lowered_tokens = [
        token if token in pos_tags else token.lower() for token in tokens
    ]

    if len(lowered_tokens) == 0 or len(lowered_tokens) > 3:
        raise ValueError("Запрос должен содержать от 1 до 3 токенов!")
    
    return lowered_tokens

def build_query(lowered_tokens):
    """
    Строит SQL-запрос на основе обработанных токенов.
    Возвращает строку запроса и параметры для выполнения.
    """
    base_query = '''
        SELECT DISTINCT s.sentence, s.work_title, s.source
        FROM sentences s
    '''
    joins = []
    conditions = []
    params = []

    # Проходим по каждому токену и определяем его тип
    for i, token in enumerate(lowered_tokens):
        # Создаем алиасы для возможности повторно присоединять таблицу
        # в случае поиска по би- и триграммам
        alias = f't{i}'
        joins.append(f'JOIN tokens {alias} ON s.id = {alias}.sentence_id')

        if token.isupper():
            # Если токен — это POS-тег
            conditions.append(f'{alias}.pos = ?')
            params.append(token)

        elif token.startswith('"') and token.endswith('"'):
            # Если токен в кавычках — конкретная словоформа
            token = token[1:-1]
            conditions.append(f'{alias}.token = ?')
            params.append(token)

        elif '+' in token:
            # Если токен содержит словоформу и POS-тег
            token, pos = token.split('+')
            pos = pos.upper()
            conditions.append(f'{alias}.token = ? AND {alias}.pos = ?')
            params.append(token)
            params.append(pos)

        else:
            # Иначе поиск по лемме
            lemma = morph.parse(token)[0].normal_form

            # При лемматизации Stanza заменяет 'ё' на 'е' в лемме,
            # поэтому чтобы избежать несоответствий между леммами
            # Stanza и pymorphy вручную делаем замену
            # после получения леммы введёного токена
            if 'ё' in lemma:
                lemma = lemma.replace('ё', 'е')

            conditions.append(f'{alias}.lemma = ?')
            params.append(lemma)
    
    # Убедимся, что токены идут друг за другом в предложении
    for i in range(len(lowered_tokens) - 1):
        conditions.append(f't{i}.id + 1 = t{i+1}.id')

    query = base_query + ' ' + ' '.join(joins) \
            + ' WHERE ' + ' AND '.join(conditions)
    
    return query, params

def execute_query(query, params):
    """
    Выполняет SQL-запрос и возвращает результаты
    """
    with sqlite3.connect(path_to_db, check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute(query, tuple(params))
        return cursor.fetchall()

def search(query):
    """
    Основная функция поиска
    """
    tokens = query.split()
    lowered_tokens = process_tokens(tokens)
    query, params = build_query(lowered_tokens)
    return execute_query(query, params)
