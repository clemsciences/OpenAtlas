# Copyright 2017 by Alexander Watzinger and others. Please see README.md for licensing information
from collections import OrderedDict
from flask import flash, render_template, session, url_for
from flask_babel import lazy_gettext as _
from flask_wtf import Form
from werkzeug.utils import redirect
from wtforms import StringField, BooleanField, SelectField

import openatlas
from openatlas import SettingsMapper
from openatlas import app
from openatlas.util.util import uc_first, required_group


class SettingsForm(Form):

    # General
    site_name = StringField(uc_first(_('site name')))
    default_language = SelectField(
        uc_first(_('default language')),
        choices=app.config['LANGUAGES'].items())
    default_table_rows = SelectField(
        uc_first(_('default table rows')),
        choices=app.config['DEFAULT_TABLE_ROWS'].items(),
        coerce=int)
    log_level = SelectField(
        uc_first(_('log level')),
        choices=app.config['LOG_LEVELS'].items(),
        coerce=int)
    maintenance = BooleanField(uc_first(_('maintenance')), false_values='false')
    offline = BooleanField(uc_first(_('offline')), false_values='false')

    # Mail
    mail = BooleanField(uc_first(_('mail')), false_values='false')
    mail_transport_username = StringField(uc_first(_('mail transport username')))
    mail_transport_host = StringField(uc_first(_('mail transport host')))
    mail_transport_port = StringField(uc_first(_('mail transport port')))
    mail_from_email = StringField(uc_first(_('mail from email')))
    mail_from_name = StringField(uc_first(_('mail from name')))
    mail_recipients_login = StringField(uc_first(_('mail recipients login')))
    mail_recipients_feedback = StringField(uc_first(_('mail recipients feedback')))

    # Authentication
    random_password_length = StringField(uc_first(_('random password length')))
    minimum_password_length = StringField(uc_first(_('minimum password length')))
    reset_confirm_hours = StringField(uc_first(_('reset confirm hours')))
    failed_login_tries = StringField(uc_first(_('failed login tries')))
    failed_login_forget_minutes = StringField(uc_first(_('failed login forget minutes')))


@app.route('/admin/settings')
@required_group('admin')
def settings_index():
    settings = session['settings']
    groups = OrderedDict([
        ('general', OrderedDict([
            (_('site name'), settings['site_name']),
            (_('default language'),
                app.config['LANGUAGES'][settings['default_language']]),
            (_('default table rows'), settings['default_table_rows']),
            (_('log level'), app.config['LOG_LEVELS'][int(settings['log_level'])]),
            (_('maintenance'),
                uc_first('on') if settings['maintenance'] == 'true' else uc_first('off')),
            (_('offline'),
                uc_first('on') if settings['offline'] == 'true' else uc_first('off'))])),
        ('mail', OrderedDict([
            (_('mail'), uc_first('on') if settings['mail'] == 'true' else uc_first('off')),
            (_('mail transport username'), settings['mail_transport_username']),
            (_('mail transport host'), settings['mail_transport_host']),
            (_('mail transport port'), settings['mail_transport_port']),
            (_('mail from email'), settings['mail_from_email']),
            (_('mail from name'), settings['mail_from_name']),
            (_('mail recipients login'), ', '.join(settings['mail_recipients_login'])),
            (_('mail recipients feedback'), ', '.join(settings['mail_recipients_feedback']))])),
        ('authentication', OrderedDict([
            (_('random password length'), settings['random_password_length']),
            (_('minimum password length'), settings['minimum_password_length']),
            (_('reset confirm hours'), settings['reset_confirm_hours']),
            (_('failed login tries'), settings['failed_login_tries']),
            (_('failed login forget minutes'), settings['failed_login_forget_minutes'])]))])
    return render_template('settings/index.html', groups=groups, settings=settings)


@app.route('/admin/settings/update', methods=["GET", "POST"])
@required_group('admin')
def settings_update():
    form = SettingsForm()
    if form.validate_on_submit():
        openatlas.get_cursor().execute('BEGIN')
        SettingsMapper.update(form)
        openatlas.get_cursor().execute('END')
        flash(_('info update'), 'info')
        return redirect(url_for('settings_index'))
    for field in SettingsMapper.fields:
        if isinstance(getattr(form, field), BooleanField):
            getattr(form, field).data = True if session['settings'][field] == 'true' else False
        elif field in ['mail_recipients_login', 'mail_recipients_feedback']:
            getattr(form, field).data = ', '.join(session['settings'][field])
        elif field in ['default_table_rows', 'log_level']:
            getattr(form, field).data = int(session['settings'][field])
        else:
            getattr(form, field).data = session['settings'][field]
    return render_template('settings/update.html', form=form, settings=session['settings'])
