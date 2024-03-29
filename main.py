import decimal
from app import app
from flask import session, render_template, request, redirect, url_for
from conexao import ConectarPostgresql
from decimal import Decimal
from babel.numbers import format_currency
from decimal import Decimal
from babel.numbers import format_currency
import locale
from decimal import Decimal

@app.route('/')
def produtos():

    con = ConectarPostgresql()
    con.iniciar_conexao()

    cursor = con.cursor
    cursor.execute("SELECT * FROM produto")

    rows = cursor.fetchall()
        
    con.fechar_conexao()

    return render_template('index.html', produtos=rows)

@app.template_filter('currency')
def currency_filter(value):
    try:
        value_decimal = Decimal(str(value))
        return f'R${value_decimal:.2f}'
    except (ValueError, TypeError, decimal.InvalidOperation):
        return value

@app.route('/add', methods=['POST'])
def adiciona_produto_no_carrinho():

    try:
        _quantidade = int(request.form['quantidade'])
        _codigo = str(request.form['codigo'])

        # verifica se a quantidade e o código foram recebidos corretamente
        if _quantidade and _codigo and request.method == 'POST':

            # recupera as informações do produto adicionado ao carrinho
            con = ConectarPostgresql()
            con.iniciar_conexao()
            cursor = con.cursor
            query = "SELECT * FROM produto WHERE codigo = %s"
            cursor.execute(query, (_codigo,))
            row = cursor.fetchone()

            # cria um dicionário com as informações do produto adicionado ao carrinho
            preco = row[4]
            if type(preco) == str:
                preco = float(preco.replace(',', '.'))

            itemArray = {_codigo: {'nome': row[1], 'codigo': _codigo, 'quantidade': _quantidade, 'preco': row[4], 'imagem': row[3], 'preco_total': _quantidade * row[4]}}

            todo_preco_total = 0
            toda_quantidade_total = 0

            session.modified = True

            # verifica se o carrinho já existe na sessão do usuário
            if 'carrinho_item' in session:

                # verifica se o item já está no carrinho
                if _codigo in session['carrinho_item']:

                    # atualiza a quantidade e o preço total do produto no carrinho
                    velha_quantidade = session['carrinho_item'][_codigo]['quantidade']
                    quantidade_total = velha_quantidade + _quantidade
                    session['carrinho_item'][_codigo]['quantidade'] = quantidade_total
                    session['carrinho_item'][_codigo]['preco_total'] = quantidade_total * preco

                else:
                    # adiciona o item ao carrinho
                    session['carrinho_item'].update(itemArray)

                # calcula o preço e a quantidade totais do carrinho    
                for key, value in session['carrinho_item'].items():
                    quantidade_individual = (session['carrinho_item'][key]['quantidade'])
                    preco_individual = float(session['carrinho_item'][key]['preco_total'])

                    toda_quantidade_total += quantidade_individual
                    todo_preco_total += preco_individual

            else: 
                # cria um novo carrinho com o item adicionado
                session['carrinho_item'] = itemArray
                toda_quantidade_total = _quantidade
                todo_preco_total = _quantidade * row[4]

            # atualiza as informações do carrinho na sessão do usuário
            session['toda_quantidade_total'] = toda_quantidade_total
            session['todo_preco_total'] = todo_preco_total

            return redirect(url_for('.produtos'))

        else:
            # retorna uma mensagem de erro se a quantidade e o código não foram recebidos corretamente
            return 'Erro ao adicionar item ao carrinho'

    except TypeError as e:
        # trata exceções do tipo TypeError
        print("Erro: ocorreu uma exceção do tipo TypeError:", e)

    except Exception as e:
        # trata exceções genéricas
        print("Erro: ocorreu uma exceção do tipo", type(e).__name__, ":", e)

    finally:
        con.fechar_conexao()

    return redirect('/')

def fusao_matriz(primeiro_array, segundo_array):
    
    # Verifica se os dois argumentos são listas
    if isinstance(primeiro_array, list) and isinstance(segundo_array, list):

        # Concatena as duas listas e retorna o resultado
        return primeiro_array + segundo_array
    
    # Verifica se os dois argumentos são dicionários
    elif isinstance(primeiro_array, dict) and isinstance(segundo_array, dict):

        # Cria um novo dicionário com a união dos dois dicionários e retorna o resultado
        return dict(list(primeiro_array.items()) + list(segundo_array, dict))
    
    # Verifica se os dois argumentos são conjuntos (sets)
    elif isinstance( primeiro_array , set ) and isinstance( segundo_array , set ):

        # Faz a união dos dois conjuntos e retorna o resultado
        return primeiro_array.union( segundo_array )
    
    # Se os argumentos não são do mesmo tipo, retorna False
    return False

@app.route('/deleta/<string:codigo>')
def deleta_produto_no_carrinho(codigo):

    try:
        # Inicia a variável que irá armazenar o preço total de todos os produtos no carrinho
        todo_preco_total = 0
        # Inicia a variável que irá armazenar a quantidade total de todos os produtos no carrinho
        toda_quantidade_total = 0

        # Percorre todos os itens no carrinho e verifica se o código do produto a ser deletado existe
        for item in session['carrinho_item'].items():

            if item[0] == codigo:

                # Remove o item com o código especificado do carrinho
                session['carrinho_item'].pop(item[0], None)

                # Verifica se ainda existem itens no carrinho
                if 'carrinho_item' in session:

                    # Percorre todos os itens no carrinho novamente para calcular a quantidade total e o preço total
                    for key, value in session['carrinho_item'].items():

                        # Obtém a quantidade e o preço total do produto atual
                        quantidade_individual = int(session['carrinho_item'][key]['quantidade'])
                        preco_individual = float(session['carrinho_item'][key]['preco_total'])

                        # Adiciona a quantidade e o preço total do produto atual às variáveis de quantidade e preço total
                        toda_quantidade_total += quantidade_individual
                        todo_preco_total += preco_individual

                # Sai do loop de itens no carrinho
                break 

        # Verifica se a quantidade total de itens no carrinho é zero
        if toda_quantidade_total == 0:

            # Limpa a sessão do carrinho, pois não há mais itens nele
            session.clear()

        else:
            # Atualiza as variáveis de quantidade total e preço total na sessão
            session['toda_quantidade_total'] = toda_quantidade_total
            session['todo_preco_total'] = todo_preco_total

        return redirect(url_for('.produtos'))
    
    except Exception as e:

        # Se ocorrer uma exceção, imprime a mensagem de erro no console
        print(e)

    # Retorna uma mensagem de sucesso indicando que o produto foi excluído com sucesso
    return 'Produto deletado com sucesso!'



# incialização
if __name__ == "__main__":
    app.debug = True
    app.run()