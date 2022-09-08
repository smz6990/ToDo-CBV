{% extends "email/base.html" %}
{% block subject %}
Activate account
{% endblock %}

{% block html %}
    <h2>Please click on the link below to activate your account</h2>
    <a href='http://127.0.0.1:8000/accounts/api/v1/verification/confirm/{{token}}/'>Click Here</a>
{% endblock %}