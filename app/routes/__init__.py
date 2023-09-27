from sanic import Blueprint

from .email import email_notify_bp, emil_callback_bp
from .push import push_notify_bp
from .sms import sms_callback_bp, sms_notify_bp, sms_test_bp
from .whatsapp import wa_callback_bp, wa_notify_bp

blueprint_group = Blueprint.group(
    emil_callback_bp,
    email_notify_bp,
    sms_callback_bp,
    sms_test_bp,
    sms_notify_bp,
    wa_callback_bp,
    wa_notify_bp,
    push_notify_bp,
)
