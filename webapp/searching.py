import sqlite3
import pymorphy3
import os

morph = pymorphy3.MorphAnalyzer()

base_dir = os.path.dirname(os.path.abspath(__file__))
path_to_db = os.path.join(base_dir, 'instance', 'corpus.db')

def search(query):
    """
    Производит поиск предложений в БД в соответствии
    с токенами введёной последовательности длиной от 1 до 3 и форматом запроса
    """
    tokens = query.split()
    if len(tokens) == 0 or len(tokens) > 3:
        raise ValueError("Запрос должен содержать от 1 до 3 токенов!")

    with sqlite3.connect(path_to_db, check_same_thread=False) as conn:
        cursor = conn.cursor()

        # Тело SQL-запроса для поиска последовательности токенов
        base_query = '''
            SELECT DISTINCT s.original_sentence, s.work_title, s.source
            FROM sentences s
        '''
        joins = []
        conditions = []
        params = []

        # Проходим по каждому токену и определяем его тип
        for i, token in enumerate(tokens):
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
                conditions.append(f'{alias}.token = ? AND {alias}.pos = ?')
                params.append(token)
                params.append(pos)

            else:
                # Иначе поиск по лемме
                lemma = morph.parse(token)[0].normal_form
                conditions.append(f'{alias}.lemma = ?')
                params.append(lemma)

        # Убедимся, что токены идут друг за другом в предложении
        for i in range(len(tokens) - 1):
            conditions.append(f't{i}.id + 1 = t{i+1}.id')

        # Строим итоговый SQL-запрос
        query = base_query + ' ' + ' '.join(joins) + ' WHERE ' + ' AND '.join(conditions)

        cursor.execute(query, tuple(params))
        return cursor.fetchall()
