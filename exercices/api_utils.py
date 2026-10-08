import requests

def get_json(url, params):

    try: response = requests.get(url, params=params, timeout=10)


    except requests.exceptions.Timeout as e:
        print("Délai dépassé")
        return None
    except requests.exceptions.ConnectionError as e:
        print("Impossible de se connecter")
        return None

    if response.status_code == 200:
        return response.json()
    else:
        print("Error:", response.url, response.text)
        return None
