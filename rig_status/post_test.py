import requests


def test():

    test_params = {'rig': 'T',
                   'status': 'Test',
                   'non_resp': 0,
                   'corr_resp': 100,
                   'n_trials': 300}

    r = requests.post('http://localhost:8001/rig_status/update_status/',
                      data=test_params)
    print(r.url)

    return r.status_code


if __name__ == '__main__':
    print(test())