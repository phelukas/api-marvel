"""Arquivo principal da aplicação."""
from dotenv import load_dotenv

print("aqui")
from server import Servidor

app = Servidor()
app.init_api()
app.init_database()
# with app.app_context():
#     set_all()
if __name__ == "__main__":
    app.run()
