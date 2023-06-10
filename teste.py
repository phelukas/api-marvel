import pyodbc

# Configuração da conexão
server = "172.17.0.2"
database = "dbMarvel"
username = "sa"
password = "Nohaxe100"

# Configuração da string de conexão
driver = "ODBC Driver 17 for SQL Server"
conn_str = (
    f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
)

# Conexão com o banco de dados
try:
    conn = pyodbc.connect(conn_str)
    print("Conexão bem-sucedida!")

    # Agora você pode executar consultas SQL ou realizar outras operações no banco de dados

    # Exemplo: executar uma consulta SQL
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tabela")
    rows = cursor.fetchall()

    for row in rows:
        print(row)

    cursor.close()
    conn.close()

except pyodbc.Error as e:
    print(f"Erro na conexão: {str(e)}")
