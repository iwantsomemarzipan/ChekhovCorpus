# Корпус по рассказам А. П. Чехова

**ChekhovCorpus** — размеченный по леммам и частям речи корпус, материалом для которого послужили рассказы А. П. Чехова. 
Тексты были собраны вручную со страницы https://ilibrary.ru/author/chekhov/l.all/index.html.

В описании репозитория указана ссылка на сайт корпуса.

## Структура репозитория

В корневой директории репозитория расположено две папки:

- В папке **corpus** хранится скрипт `create_db.py` для создании базы данных, файл `metadata.py` со словарём метаданных, 
а также папка **texts**, где находятся тексты, на основе которых был составлен корпус. 
Файлы в директории **corpus** не используются для деплоя сайта, однако могут оказаться полезными для тех, кто захочет расширить существующую базу данных.

- Папка **webapp** содержит в себе файлы, необходимые для реализации веб-приложения. 
Директории **instance**, **templates** и **static/css** служат для хранения базы данных (о БД см. [здесь](#хранение-данных)), шаблонов html и css-стилей соответственно.

Шаблонов html всего 4:
- `base.html` задаёт базовую структура сайта, которую наследуют остальные щаблоны
- `index.html` — шаблон главной страницы сайта, где есть поисковая строка для ввода запросов
- `help.html` — шаблон страницы с инструкцией по созданию запросов
- `results.html` — шаблон страницы, на которой показываются результаты поиска

Помимо прочего, в папке **webapp** лежат файлы `app.py` и `searching.py`. В `searching.py` содержится скрипт для обращения к базе данных и осуществления поиска по ней. 
`app.py` — файл Flask-приложения, предоставляющего веб-интерфейс для взаимодействия с корпусом.

## Сайт корпуса

Проект реализован на сайте, где пользователь может ввести интересующий его запрос. Всего корпус поддерживает 4 формата запросов:
- **слово без кавычек** — поиск по лемме; выводятся предложения, в которых найдено заданное слово в любой форме. Лемма извлекается с использованием **pymorphy3**
- **слово в кавычках** — поиск строго по заданной словоформе
- **POS-тег из [списка UD](https://universaldependencies.org/u/pos/)** — поиск по токенам, соответствующим заданному тегу
- слово без кавычек + POS-тег — поиск по словоформе, соответствующей заданному тегу

Примеры запросов:
- "кота"
- а+INTJ
- DET "человек"
- теми VERB
- "мне" было+AUX ADJ
- ни NOUN ни

Разрешённая длина запросов — от 1 до 3 токенов включительно.

## Хранение данных

Весь материал хранится в базе даных SQL. БД имеет две таблицы: `sentences` и `tokens`. `Sentences` служит для хранения id предложений, 
самих предложений, а также метаданных вида название произведения, откуда взято предложение, и URL-ссылка на полный текст.

В таблице `tokens` лежат id токенов, id предложений, в которых эти токены находятся, сами токены, их леммы, 
POS-теги. Морфологическая информация о токенах получена при помощи библиотеки **Stanza**.

## Установка

Проект доступен для запуска на локальном компьютере. Для этого выполните следующие шаги:

1. Клонируйте репозиторий
```
git clone https://github.com/iwantsomemarzipan/ChekhovCorpus.git
```

2. Установите требуемые библиотеки
```
pip install -r requirements.txt
```

3. Запустите `app.py` для локальной инициализации сайта