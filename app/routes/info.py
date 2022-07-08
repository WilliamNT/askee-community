from flask import Blueprint, render_template

info = Blueprint("info", __name__)

@info.get("/rules/")
def rules():
    return render_template("info/rules.html")