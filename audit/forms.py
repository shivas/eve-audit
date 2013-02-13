from wtforms import Form, validators
from flask.ext.wtf import Form, TextField, BooleanField, PasswordField,\
    FileField, TextAreaField, HiddenField, SelectField
from wtforms.validators import ValidationError, StopValidation

import evelink


eve = evelink.eve.EVE()


def validate_api(form, field):
    try:
        api = evelink.api.API(api_key=(form.data['api_id'],
                                       form.data['api_vcode']))
        account = evelink.account.Account(api)
        account.characters()
    except evelink.api.APIError:
        print "got exception"
        raise ValidationError("Invalid API or API server is down")


class ApiForm(Form):
    api_id = TextField('API ID', [
        validators.Required(message="API ID is required"),
    ])
    api_vcode = TextField('API vCode', [
        validators.Required(message="API vCode is required"),
        validate_api,
    ])
