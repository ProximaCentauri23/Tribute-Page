from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from dotenv import load_dotenv
import os
from smtplib import SMTP
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField, EmailField
from wtforms.validators import InputRequired, Email, Length


# ###### preden ga javno objaviš:
# zrihtaj https
# izklopi debug
# ######
#!!!! slike samo naložiš v static/img folder carousel naloada vse

class ContactForm(FlaskForm):
    name = StringField('Full Name', validators=[InputRequired()])
    email = EmailField('Email Address', validators=[InputRequired(), Email(message="Invalid email")])
    phone = StringField('Phone Number', validators=[InputRequired()])
    message = StringField("Your Message", validators=[InputRequired(),Length(max=300, message="Message must contain fewer than 300 characters")])
    submit = SubmitField("Submit")





load_dotenv()
#### vneses svoje podatke naredi .env file
password = os.getenv("PASS")
gmail = os.getenv("GMAIL")
secret_key = os.getenv("SECRET_KEY")


app = Flask(__name__)
app.secret_key = secret_key

def send_email(name,email,phone,message):
    with  SMTP("smtp.gmail.com", port=587) as connection:
        connection.starttls()
        connection.login(user=gmail, password=password)
        connection.sendmail(
            from_addr=gmail,
            to_addrs=gmail,
            msg=(
            f"Subject: New Contact Form Submission\n\n"  
            f"Name: {name}\n"
            f"Email: {email}\n"
            f"Phone: {phone}\n"
            f"Message: {message}\n" ))



@app.route("/")
def home():
    img_folder = os.path.join(app.static_folder, "img")
    images = [f for f in os.listdir(img_folder) if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".gif"))]
    return render_template("index.html", images=images)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        send_email(
            form.name.data,
            form.email.data,
            form.phone.data,
            form.message.data
        )

        flash("Message Sent Successfully", "Success")
        return redirect(url_for("contact", msg_snt=True))
    return render_template("contact.html", form=form, msg_snt=False)




if "__main__" == __name__:
    app.run(debug=True)
