from flask import Flask, render_template, request, redirect
from searching import search

app = Flask(__name__)


# Главная страница
@app.route("/")
def main_page():
    return render_template('index.html')


# Страница с инструкцией
@app.route("/help")
def help():
    return render_template('help.html')


# Страница, перенаправляющая на репозиторий
@app.route("/repo")
def repo_redirect():
    return redirect("https://github.com/iwantsomemarzipan/ChekhovCorpus",
                    code=302)


# Перенаправляет на страницу с результатами запроса
@app.route('/search', methods=['GET'])
def search_results():
    query = request.args.get('q')
    if not query:
        return render_template(
            'results.html', results=[], query=query,
            error="В поисковой строке пусто :(\
                <br> Попробуйте ввести запрос ещё раз."
            )
    
    try:
        results = search(query)
        if not results:
            message = "По вашему запросу ничего не найдено :("
            return render_template(
                'results.html', results=results,
                query=query, message=message
                )
        
        return render_template(
            'results.html', results=results,
            query=query
            )
    
    except ValueError as e:
        return render_template(
            'results.html', results=[],
            query=query, error=str(e)
        )

    except Exception as e:
        return render_template(
            'results.html', results=[],
            query=query, error=str(e)
            )


if __name__ == '__main__':
    app.run(debug=False)
