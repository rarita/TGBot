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
        response = functions.get_itineraries_be(
            "LED",
            "CEK",
            datetime.date(2021, 6, 5),
            datetime.date(2021, 6, 5)
        )

        self.assertGreater(len(response), 0, "response has 0 itineraries")
        logger.info("Response length is {}".format(len(response)))

    def test_be_iata(self):
        response = functions.get_iata_be("Мос")
        self.assertGreater(len(response), 0, "response has 0 matched city-country pairs")
