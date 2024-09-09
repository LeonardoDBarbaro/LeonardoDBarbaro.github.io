import http.server
import json
import subprocess

class RequestHandler(http.server.BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        # Enviar encabezados CORS para manejar solicitudes preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        # Manejo de la solicitud POST
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        # Decodificar y cargar los datos JSON
        data = json.loads(post_data)
        player_name = data.get('name', '')[:25]  # Limitar el nombre a 25 caracteres
        score = data.get('score')
        emoji = data.get('emoji')
        
        # Guardar puntaje en el archivo de registro general
        file_name = 'all_scores.txt'
        with open(file_name, 'a') as f:
            f.write(f'{player_name} | {score} | {emoji}\n')

        # Determinar el archivo HTML según el emoji
        if emoji == 'palta':
            html_file = 'palta_scores.html'
        elif emoji == 'sol':
            html_file = 'sol_scores.html'
        else:
            html_file = None  # En caso de un emoji inesperado

        # Si el emoji es válido, actualizar el archivo HTML correspondiente
        if html_file:
            with open(html_file, 'a') as f:
                f.write(f'<p>{player_name} | {score} | {emoji}</p>\n')

            # Realizar el commit y push de los cambios a Git
            self.push_to_git([html_file])

        # Responder que se ha guardado correctamente
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Score saved')

    def push_to_git(self, files):
        try:
            # Añadir los archivos modificados al staging
            subprocess.run(['git', 'add'] + files, check=True)
            
            # Hacer commit con un mensaje indicando la actualización
            commit_message = "Updated scores for emoji competition"
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)

            # Hacer push al repositorio remoto
            subprocess.run(['git', 'push'], check=True)

            print(f'Successfully pushed {files} to git repository.')

        except subprocess.CalledProcessError as e:
            print(f"Error during git push: {e}")

# Configurar y ejecutar el servidor
def run(server_class=http.server.HTTPServer, handler_class=RequestHandler, port=8081):
    server_address = ('10.41.101.1', port)
    httpd = server_class(server_address, handler_class)
    print(f'Server running on port {port}')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
