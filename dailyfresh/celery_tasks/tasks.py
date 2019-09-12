from celery import Celery
from django.core.mail import send_mail
from django.conf import settings

app = Celery('celery_tasks.tasks',
             borker='redis:cui123@//39.107.116.79:6379/2')


@app.task
def send_register_active_mail(to_email, username, token):
    html_message = '欢迎%s,请点击<a href ="http://127.0.0.1:8000/user/activate/%s">http://127.0.0.1:8000/user/activate/%s</a>激活' % (
        username, token, token)
    send_mail('激活邮件', '', settings.EMAIL_FROM, [
        to_email], html_message=html_message)
