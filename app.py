"""Num2Vid Flask Server.

All Flask-related logic, as well as routes are centralized here.
"""
import logging
import sys
from os import path as osp
from os import environ

from flask import Flask, render_template, send_file
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

import num2vid

APP = Flask(__name__)
APP.config["WTF_CSRF_ENABLED"] = False
CONFIG = num2vid.Config(environ["NUM2VID_CONFIG"])

logging.basicConfig(filename=osp.join(
    CONFIG.get("logging_output_dir"), "num2vid_log"), level=logging.DEBUG)
sys.stdout.write("Logging to: {0}\n".format(osp.abspath(CONFIG.get("logging_output_dir"))))

## routes
@APP.route("/", methods=["GET", "POST"])
def server_ui():
    """Serve server index with form and calculation result if present."""
    form = Num2VidServerForm()
    # data to be sent to UI
    data = {
        "ver": num2vid.__version__,
        "form": form
    }
    # if something was entered attempt calculation
    if form.math_str.data:
        try:
            data["calculated_result"] = num2vid.calculate(form.math_str.data)
        except (num2vid.errors.InvalidMathStrError,
                num2vid.errors.InvalidMathStrResultError) as err:
            data["calculated_result"] = err  # err implements custom-defined __repr__ method

    return render_template("num2vid_server_ui.html", data=data)

@APP.route("/convert/<int:num>")
def convert(num) -> "ffmpeg-generated vid":
    """Convert num to video.

    :param num: the num received from client.
    """
    APP.logger.info("Recieved request for num: {0}".format(num))

    return send_file(num2vid.convert(num), as_attachment=True)


class Num2VidServerForm(FlaskForm):
    """flask_wtf FlaskForm description."""
    math_str = StringField("Enter a math equation:", validators=[DataRequired()])
    submit = SubmitField("Calculate.")

APP.run(host=CONFIG.get("flask_host"), port=CONFIG.get("flask_port"), debug=True)