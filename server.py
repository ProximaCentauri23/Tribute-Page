from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from dotenv import load_dotenv
import os
from smtplib import SMTP
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField, EmailField
from wtforms.validators import InputRequired, Email, Length
from flask_babel import Babel
from flask_babel import gettext as _
# 🟢🟢🟢 TO DO: Add cookie consent check before setting session['lang']
# ###### preden ga javno objaviš:
# zrihtaj https
# izklopi debug
# ######
#!!!! slike samo naložiš v static/img folder carousel naloada vse
#! pushaj v svoj branch

# dodaj coockie accept pop up
################################################
# 1. Extract all translatable strings into a POT template (overwrite each time)
# ---------------------------------------------------------------------------
# pybabel extract -F babel.cfg -o messages.pot . --ignore .venv

# 2. Initialize a new language (only ONCE per language!)
#    This creates translations/sl/LC_MESSAGES/messages.po
# ---------------------------------------------------------------------------
# pybabel init -i messages.pot -d translations -l sl

# 3. Update existing language files after you add new strings (NO init again!)
# ---------------------------------------------------------------------------
# pybabel update -i messages.pot -d translations

# 4. Compile translations into .mo files Flask-Babel uses at runtime
# ---------------------------------------------------------------------------
# pybabel compile -d translations

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

babel = Babel()
app = Flask(__name__)
app.secret_key = secret_key
app.config["BABEL_DEFAULT_LOCALE"] = "en"
app.config["BABEL_TRANSLATION_DIRECTORIES"] = "translations"


def get_locale():
    lang = request.view_args.get("lang_code")
    if lang in ["en","sl","it"]:
        return lang
    return "en"

babel.init_app(app, locale_selector=get_locale)

@app.context_processor
def inject_lang_code():
    return {
        'lang_code': get_locale()
    }
@app.context_processor
def utility_processor():
    def url_for_lang(lang):
        args = dict(request.view_args or {})
        args['lang_code'] = lang
        return url_for(request.endpoint, **args)
    return dict(url_for_lang=url_for_lang)

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


@app.route('/')
def redirect_to_default():
    lang = request.accept_languages.best_match(["en-GB","sl", "it"])
    return redirect(url_for('home', lang_code=lang or "en"))

@app.route("/debug")
def debug_lang():
    return request.headers.get('Accept-Language')

@app.route("/<lang_code>")
def home(lang_code):
    img_folder = os.path.join(app.static_folder, "img")
    images = [f for f in os.listdir(img_folder) if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".gif"))]
    return render_template("index.html", lang_code=lang_code, images=images)

@app.route("/<lang_code>/about")
def about(lang_code):
    return render_template("about.html")

@app.route("/<lang_code>/contact", methods=["GET", "POST"])
def contact(lang_code):
    form = ContactForm()
    if form.validate_on_submit():
        send_email(
            form.name.data,
            form.email.data,
            form.phone.data,
            form.message.data
        )

        flash("Message Sent Successfully", "Success")
        return redirect(url_for("contact"))
    return render_template("contact.html", form=form)

@app.route("/<lang_code>/gallery")
def gallery(lang_code):
    return render_template("galery.html")



if "__main__" == __name__:
    app.run(debug=True)
