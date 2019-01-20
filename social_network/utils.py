import clearbit
from social_network.constants import CLEARBIT_SECRET


def get_info_from_clearbit(email):
    data = dict()
    if CLEARBIT_SECRET:
        clearbit.key = CLEARBIT_SECRET
        clearbit_resp = clearbit.Enrichment.find(email=email, stream=True)
        if clearbit_resp['person']:
            data['first_name'] = clearbit_resp['person']['name']['givenName']
            data['last_name'] = clearbit_resp['person']['name']['familyName']
            data['city'] = clearbit_resp['person']['geo']['city']
            data['country'] = clearbit_resp['person']['geo']['country']
            data['about_me'] = clearbit_resp['person']['bio']
    return data
