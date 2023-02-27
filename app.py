from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from flask import Flask

app = Flask(__name__)

# Configuración de credenciales de Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
creds = None

token_file = 'token.json'

# Carga las credenciales de las credenciales de token.json
if os.path.exists(token_file):
    creds = Credentials.from_authorized_user_file(token_file, SCOPES)

@app.route('/')
def index():
    try:
        # Crear una instancia de la API de Google Drive
        service = build('drive', 'v3', credentials=creds)

        # Buscar el archivo de cuaderno de Jupyter en Google Drive
        file_name = 'bot.ipynb' # Cambiar por el nombre de tu archivo
        query = "mimeType='application/vnd.google-apps.document' and name='{}'".format(file_name)
        results = service.files().list(q=query, fields='files(id)').execute()
        items = results.get('files', [])

        # Verificar si se encontró el archivo
        if not items:
            return "No se encontró el archivo {}".format(file_name)

        # Obtener el ID de archivo del cuaderno de Jupyter
        file_id = items[0]['id']

        # Definir los parámetros para ejecutar el cuaderno de Jupyter en Google Colab
        params = {
            'key': 'INSERT_API_KEY_HERE', # Reemplazar con la clave de la API de Colab
            'includeResults': 'true'
        }

        # Definir el cuerpo de la solicitud para ejecutar el cuaderno de Jupyter en Google Colab
        body = {
            'mode': 'run',
            'url': 'https://colab.research.google.com/drive/' + file_id,
            'params': params
        }

        # Crear una instancia de la API de Google Drive para enviar la solicitud
        colab_service = build('drive', 'v3', credentials=creds)
        response = colab_service.files().executeFunction(fileId=file_id, body=body).execute()

        return "El cuaderno de Jupyter se ha ejecutado correctamente en Google Colab."

    except HttpError as error:
        return "Ocurrió un error: {}".format(error)

if __name__ == '__main__':
    app.run()
