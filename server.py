import flask
app=flask.Flask(__name__)


@app.route('/<page>')
def index(page):
    return flask.render_template(f'{page}/index.html')
@app.route('/')
def main():
    return flask.render_template('index.html')
@app.route('/assets/<file>')
def cdn(file):
    return flask.send_file(f'./templates/cdn/{file}')

def run_server(debug:bool=False,port:int=5000):
    app.run(port=port,debug=debug)