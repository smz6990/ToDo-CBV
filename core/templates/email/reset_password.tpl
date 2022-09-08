{% extends "email/base.html" %}
{% block subject %}
Reset Password 
{% endblock %}

{% block html %}
    <h2>Please click on the link below to reset your password</h2>
    <a href='http://127.0.0.1:8000/accounts/api/v1/password-reset/done/{{token}}/'>Click Here</a>
{% endblock %}