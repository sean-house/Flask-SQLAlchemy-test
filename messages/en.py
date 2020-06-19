"""
File with message constants in English
:var
"""
MEASUREMENT_STORED = 'Measurement stored'
FIELD_REQUIRED = "'{}' field must be specified"
USER_EXISTS = 'User with that name already exists'
EMAIL_EXISTS = 'A user with that email already exists'
USER_NONEXISTANT = "User with ID {} does not exist"
USER_ACTIVATED = "User {} has ben activated"
CREATED = "'{}' has been created"
DELETED = "'{}' has been deleted"
INVALID_PASSWORD = 'Invalid credentials'
OWN_RECORD_ONLY = 'You are only permitted to delete your own record'
NOT_CONFIRMED = "You have not confirmed your ID. Check your email - <{}>"

# Confirmation email
FROM_TITLE = 'API Admin'
FROM_EMAIL = 'apis@housesofyateley.net'
MAIL_SUBJECT = 'Measurement API - Confirm your email'
MAIL_BODY = """
Dear {name}, \n
\n
Thank you for registering to use the Measurements API. \n
Please click this link to activate your account: {link}  \n
\n
\n
If you did not register for the Measurement API you can safely ignore this message. \n
\n
API Administrator
"""
MAIL_BODY_HTML = """
<html>
<strong>Dear {name},</strong><br><br>
Thank you for registering to use the Measurements API.<br>
<br>
Please click this link to activate your account:<br>
<a href="{link}">{link}</a><br><br>
API Administrator

</html>
"""
