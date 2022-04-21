from kavenegar import *


def send_otp_sms(receptor, template, token, token2='', token3=''):
    try:
        api = KavenegarAPI('725050506934746361716E7531626B6259793679614C53573759656D6B737730376F47786272764A665A343D', timeout=20)
        params = {
            'receptor': receptor,
            'template': template,
            'token': token,
            'token2': token2,
            'type': 'sms',
        }
        response = api.verify_lookup(params)
    except APIException as e:
        print(e)

    except HTTPException as e:
        print(e)
    else:
        return response
