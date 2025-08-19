from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
import pickle

# Load model and vectorizer
vector = pickle.load(open("vectorizer.pkl", "rb"))
model = pickle.load(open("Finalize_model.pkl", 'rb'))

app = Flask(__name__)

# SQLite configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'  # database file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database models
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    message = db.Column(db.Text)
    date_sent = db.Column(db.DateTime, default=db.func.current_timestamp())

class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    news = db.Column(db.Text)
    result = db.Column(db.String(50))
    date_predicted = db.Column(db.DateTime, default=db.func.current_timestamp())

# Home page
@app.route("/")
def home():
    return render_template("index.html")

# Prediction page
@app.route('/prediction', methods=['GET', 'POST'])
def prediction():
    if request.method == "POST":
        news = str(request.form["news"])
        print(news)

        # Make prediction
        predict = model.predict(vector.transform([news]))[0]
        print(predict)

        # Save prediction to database
        new_prediction = Prediction(news=news, result=predict)
        db.session.add(new_prediction)
        db.session.commit()

        return render_template("prediction.html", prediction_text=f"News headline is -> {predict}")
    else:
        return render_template("prediction.html")

# Contact page
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")

        # Save contact message to database
        new_contact = Contact(name=name, email=email, message=message)
        db.session.add(new_contact)
        db.session.commit()

        success_message = "Thank you for contacting us! We will get back to you soon."
        return render_template("contact.html", success_message=success_message)
    return render_template("contact.html")

# About page
@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == '__main__':
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
    app.run(debug=True)
