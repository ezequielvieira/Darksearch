#!/usr/bin/python

import sys
sys.path.append('C:/Users/Ezequiel Vieira/Darksearch/darksearch')

from flask import request, render_template
from darksearch.darkmain import app as application
from darksearch.tools.elas import DarkElastic  # Importe a classe DarkElastic

search_engine = DarkElastic()  # Crie uma instância da classe

@application.route('/search/1', methods=['POST'])
def search_results():
    query = request.form.get('query')
    if query:
        results = search_engine.search_index('dark', query)  # Realize a pesquisa
        # ... (processamento dos resultados) ...
        return render_template('results.html', results=results)
    else:
        return "Consulta inválida", 400 

def main():
    # ... (seu código existente) ...

    application.run(
        host='0.0.0.0',
        port=80,
        threaded=True,
        debug=True
    )

if __name__ == '__main__':
    main()
