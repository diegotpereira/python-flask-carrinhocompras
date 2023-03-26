import psycopg2

class ConectarPostgresql:
    
    def __init__(self, bancoNome = 'tabelas_python', usuario = 'postgres', senha = '123', host = 'localhost', port = 5432):
        self.bancoNome = bancoNome
        self.usuario = usuario
        self.senha = senha
        self.host = host
        self.port = port
        self.connection = None 
        self.cursor = None

    def iniciar_conexao(self):

        try:
            self.connection = psycopg2.connect(

                dbname = self.bancoNome,
                user = self.usuario,
                password = self.senha,
                host = self.host,
                port = self.port
            )
            self.cursor = self.connection.cursor()
            print("Conexão com Postgresql estabelicida")

        except Exception as e:
            print("Erro ao conectar com PostreSQL: ", e)

    def execute_consulta(self, query):
        try:
            self.cursor.execute(query)
            self.connection.commit()
            print("Consulta executada com sucesso")

        except Exception as e:
            print("Erro ao executar a consulta: ", e)

    def fechar_conexao(self):
        self.cursor.close()
        self.connection.close()
        print("Conexão com PostgreAQL encerrada")