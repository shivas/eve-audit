import os
import re

from flask import Flask, render_template, request, redirect,\
    session, escape, flash, g, url_for, abort, jsonify
import evelink

from audit.app import app, db
from audit.forms import ApiForm
from audit.utils import Character, Corporation, Alliance
from audit.models import Skill


@app.before_request
def before_request():
    g.eve = evelink.eve.EVE()
    if 'api_id' in session:
        g.api_id = session['api_id']
    if 'api_vcode' in session:
        g.api_vcode = session['api_vcode']
    if 'char_id' in session:
        g.char_id = int(session['char_id'])
    if 'api_id' in g.__dict__ and 'api_vcode' in g.__dict__:
        g.api = evelink.api.API(api_key=(g.api_id, g.api_vcode))


@app.route("/", methods=['GET', 'POST'])
def index():
    form = ApiForm(request.form)
    if form.validate_on_submit():
        session['api_id'] = request.form['api_id']
        session['api_vcode'] = request.form['api_vcode']
        return redirect(url_for("character_select"))
    return render_template("index.html", form=form)


@app.route("/character_select", methods=['GET', 'POST'])
def character_select():
    if request.method == "POST":
        session['char_id'] = request.form['char_id']
        return redirect(url_for("character_index"))
    acc = evelink.account.Account(g.api)
    chars = []
    for cid, _ in acc.characters().iteritems():
        chars.append(Character().from_api(cid))
    return render_template("character_select.html", chars=chars)


@app.route("/character")
def character_index():
    acc = evelink.account.Account(g.api)
    char = Character().from_api(g.char_id)
    char.skill_sheet_from_api()
    return render_template("character_sheet.html", char=char)


@app.route("/mail")
def mail_index():
    acc = evelink.account.Account(g.api)
    char = Character().from_api(g.char_id)
    char.mails_from_api()
    return render_template("mail_index.html", char=char)


@app.route("/contacts")
def contacts_index():
    acc = evelink.account.Account(g.api)
    char = Character().from_api(g.char_id)
    return render_template("contacts_index.html", char=char)


@app.route("/assets")
def assets_index():
    pass


@app.route("/wallet")
def wallet_index():
    acc = evelink.account.Account(g.api)
    char = Character().from_api(g.char_id)
    return render_template("wallet_index.html", char=char)
    pass


@app.route("/market")
def market_index():
    pass


@app.route("/contracts")
def contracts_index():
    pass


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
