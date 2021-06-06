import requests


base_url = 'http://127.0.0.1:5000/'


def sign_up(name, password):
    return requests.put(f'{base_url}user?name={name}&password={password}')


def sign_in(name, password):
    return requests.get(f'{base_url}user?name={name}&password={password}')
