from flask import Flask, render_template, request

 

 

# Create the Flask application

app = Flask(__name__)

 

 

# Home-page route

@app.route("/")

def home():

    return render_template("index.html")

 

 

# This route receives the form data

@app.route("/greet", methods=["POST"])

def greet():

    # Get the name entered by the user

    name = request.form.get("name", "").strip()

 

    # Use a default value if the user enters nothing

    if not name:

        name = "Student"

 

    # Send the name to result.html

    return render_template("result.html", name=name)

 

 

# Run the application

if __name__ == "__main__":

    app.run(debug=True)






