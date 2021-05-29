import unittest
import logging
import datetime
import functions

# Enable logging for tests
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class TestExternalAPIs(unittest.TestCase):

    # try to get itineraries from backend
    def test_be_itin(self):
        out_date = datetime.date.today() + datetime.timedelta(5)
        response = functions.get_itineraries_be(
            "LED",
            "CEK",
            out_date,
            out_date
        )

        self.assertGreater(len(response), 0, "response has 0 itineraries")
        logger.info("Response length is {}".format(len(response)))

    def test_be_iata(self):
        response = functions.get_iata_be("Мос")
        self.assertGreater(len(response), 0, "response has 0 matched city-country pairs")

        response = functions.get_iata_be("Абырвалг!")
        self.assertEqual(len(response), 0)

    def test_be_airport_flavor(self):
        flavor = functions.get_airport_flavor_be(10002)
        self.assertEqual(flavor, "Пулково (LED)")
