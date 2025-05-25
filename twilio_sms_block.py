from twilio.rest import Client

def send_sms(to, score, advice):
    account_sid = "ACxxxx"
    auth_token = "your_auth_token"
    client = Client(account_sid, auth_token)
    msg = f"Your credit score: {score}. Advice: {advice}"
    client.messages.create(
        body=msg,
        from_='+1234567890',
        to=to
    )
# Usage: send_sms("+1987654321", score, advice)