from flask import Flask

app = Flask(__name__)

 

@app.route("/")

def home():

    return """

    <h1>Hello Students!</h1>

    <p>My first Flask application is working.</p>

    """

 

if __name__ == "__main__":

    app.run(debug=True)




