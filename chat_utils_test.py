import unittest

from chat_utils import fix_itin


class TestChatUtils(unittest.TestCase):

    # check itinerary fixing (propertyList transformation) works
    def test_fix_itin(self):
        # unittest crashes when i try to assign it to self in constructor
        incorrect_itin = {'itin': [
            {'id': 18781, 'version': None, 'type': 'CAN_GO', 'startNode': 10002, 'endNode': 11211,
             'primaryIdName': None, 'propertyList': [{'key': 'departureTime', 'value': '2021-05-29T02:20:00'},
                                                     {'key': 'baseCost', 'value': '41'},
                                                     {'key': 'cost', 'value': '3619'},
                                                     {'key': 'fareClasses', 'value': ''},
                                                     {'key': 'type', 'value': 'AIRCRAFT'},
                                                     {'key': 'fareCategory', 'value': 'M'},
                                                     {'key': 'ttl', 'value': 21600},
                                                     {'key': 'flightNumber', 'value': 0}, {'key': 'bookingLink',
                                                                                           'value': 'https://www.kiwi.com/deep?from=LED&to=DME&flightsId=219b01884958000040f2bd87_0&price=41&passengers=1&affilid=raritaflights&lang=ru&currency=RUB&booking_token=BEvqS9Rzb9vdc8O2nd9HC-uMw3KWMfU-5tF3MDoieiSTVLWLjFp4pwhZb4Jd00RpjByOdXLTqXeuEtgutG9OqcFx-ObXfBnJdYC_r5t4Xe_2yj3Ft0zlxv9eRX3Jsysq_AfjoPAA_NqfZLjXn0xNYNSPo0Wzg9zjc4s7oOE4CbFyEB6v9snYbLkSseLiEjllZPWn7uBSNvNJKIlgIFiLlPUmhbsDmUnNcVV5gQDEe3uJJYhMzTZCPfCBfK0Z3cQxFvxsDioADyNU7czCzgED2zbM6OcgMTF4pKRbppWzpyXxywL1j0Yatj4FEIHl8D5ZQO2sydgrh0fhEGWxYZAqrTT0OnbUi5-svm0fz2IQjubApb9gIYM0E_BbQy3SLv1aj4xk9KgmGbQE4l7oKFJGkik1IfevH5fy2cmlgZGI8fgiW6uq5f3AXsoLnfkk3W8hEYKpXfgpwUndKSV92wHXkCbYY1UhsXosptW0QoeGcJPVjns5JWpB6-w6UNRMiJbCRJ7MK9pP8SSaI7qB61FGCByaL7DRmxNup5U6ADxFVfhVTfbB3zMJtNFh5iP6usS9uvNkh3DuObPtbT2whC9hugwU7gX9jR9qte3EvSciVl80tCa1Itjvs18Q2AXsW1TYfvCxXnYHzTbA_Dv_16VIdjJSIBX1ykI6tDk5w_tNvEHbilD67cvE_8M_63D3pWteNAGGViLkmKgRGPGW6g4zt3gk7bxi5QbCUw1tBHnDXBGA6COjlPpqGKBGjgJerMoTcI5bzh3UL7uv-yru1bNyJRB2p4B9fTmF6avRNPcONM2IvDfWlufRsuh66Z6h_QGQIZaMlQFhiYhtYQFx0QS6XZw=='},
                                                     {'key': 'fareBasis', 'value': 'QBSOW'},
                                                     {'key': 'arrivalTime', 'value': '2021-05-29T03:50:00'},
                                                     {'key': 'carrierCode', 'value': 'S7'},
                                                     {'key': 'airlineCode', 'value': 'S7'},
                                                     {'key': 'fareFamily', 'value': ''},
                                                     {'key': 'foundAt', 'value': '2021-05-26T22:52:55.699801'},
                                                     {'key': 'currencyCode', 'value': 'RUB'}]},
            {'id': 18810, 'version': None, 'type': 'CAN_GO', 'startNode': 11211, 'endNode': 12556,
             'primaryIdName': None, 'propertyList': [{'key': 'departureTime', 'value': '2021-05-29T14:50:00'},
                                                     {'key': 'baseCost', 'value': '54'},
                                                     {'key': 'cost', 'value': '4824'},
                                                     {'key': 'fareClasses', 'value': ''},
                                                     {'key': 'type', 'value': 'AIRCRAFT'},
                                                     {'key': 'fareCategory', 'value': 'M'},
                                                     {'key': 'ttl', 'value': 21600},
                                                     {'key': 'flightNumber', 'value': 0}, {'key': 'bookingLink',
                                                                                           'value': 'https://www.kiwi.com/deep?from=DME&to=KUF&flightsId=01881103495800007c92fe2c_0&price=54&passengers=1&affilid=raritaflights&lang=ru&currency=RUB&booking_token=BGLWze4nvWQF2UqFotOeSI3LtpWja7gOkn2_1lB_rxKBALqXKEprLwn4Eg4ivL9K1HBMI-R937g-8SxBmZ9mEdtGJ113YvWhih4otBZoBtwl3BvdGTJUY0CsaBuVzeE9Q0Cd4bqidHzY4ImUEczB8JIwqY0EojrlwXCzTjvBUNdpzDYtEstTOaLba9qEIwvM9WMGgX08JLPgXS_v_DcD8i99d7g6BpwTf30GFf6H7FobOz1ikC-QMxgfuQJV1e2_U7an15sh2BXTXMXzcE7QdbSTtX_GISnExtwHrEvmV_D3hEALnySib39NDDLTg8PZ3_hwxYnmiY9uNAyxOi6k5j8Y6E7ixxFKV0FpRX2Lk2disxYIV8Qt-taWlAiHD5Kegqu-Rjr9DwYBw4nMlbeqTrhQd8Fbp7m8okS188MfojOxDEWmX0tgCGuF6mTejd2dPqphyjaq3fBCXRdVm9CosAZKdFDIy9w5bGNqnk-Wmo0ABh-SuCcvuualTZ4J0qIezqZ17Y4zhYHjdn8N2WQiFohxyKzyzuJ4Idfn7nVyEXvwkXkkc9yrgnUZxC0fJrV23DDMVsO9pq47LNEx8MaKUEVTutkb0FmJUJ2Z6u_t7bfMVHJx8ZegraiIoMdmI9NsoEUuGF2KeUnp9QGvoTHTiezR-3JUrY5sb0bUkljn9S6-_Qt8vDCADIO-rFAryNPCq3acwkwBVyYxSwIwi1Bc4850dftEY1EarpQuYZ97wxkLtm80YzVcomxM70nxaRE4vC3xDZJ1bBC90RkWlscktcM6YoqXHmn-_tFhjM5JIMjRt6dG62USjzZ4rnUrVN8l1'},
                                                     {'key': 'fareBasis', 'value': 'QBSOW'},
                                                     {'key': 'arrivalTime', 'value': '2021-05-29T16:35:00'},
                                                     {'key': 'carrierCode', 'value': 'S7'},
                                                     {'key': 'airlineCode', 'value': 'S7'},
                                                     {'key': 'fareFamily', 'value': ''},
                                                     {'key': 'foundAt', 'value': '2021-05-26T22:52:57.65382'},
                                                     {'key': 'currencyCode', 'value': 'RUB'}]}],
            'dst': {'code': 'KUF', 'name_RU': 'Курумоч', 'name_EN': 'Kurumoch International Airport',
                    'parent': None, 'latitude': 53.50782, 'longitude': 50.14742},
            'src': {'code': 'LED', 'name_RU': 'Пулково', 'name_EN': 'Pulkovo Airport', 'parent': None,
                    'latitude': 59.806084, 'longitude': 30.3083},
            'c_dst': {'code': 'KUF', 'name_RU': 'Самара', 'name_EN': 'Samara', 'parent': None,
                      'latitude': 53.50782, 'longitude': 50.14742},
            'c_src': {'code': 'LED', 'name_RU': 'Санкт-Петербург', 'name_EN': 'Saint Petersburg',
                      'parent': None, 'latitude': 59.939039, 'longitude': 30.315785}}
        itin = fix_itin(incorrect_itin)
        it = itin['itin'][0]

        self.assertTrue('arrivalTime' in it)
        self.assertTrue('departureTime' in it)
        self.assertTrue('cost' in it)

        self.assertGreater(len(it), 20)


if __name__ == '__main__':
    unittest.main()
