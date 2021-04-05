from twilio.rest import Client

import logging
_logger = logging.getLogger(__name__)

def notify_new_apartment(sid, token, from_, to, apartment):
    account_sid = sid
    auth_token = token

    try:
        client = Client(account_sid, auth_token)
        message = client.messages .create(
            body =  f'New apartment {apartment.url}',
            from_ = from_,
            to = to)
        message.sid
        return True
    except Exception as e:
        _logger.error(f'Error while sending apartment notification: {e}')
        return False