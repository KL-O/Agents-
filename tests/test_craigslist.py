import unittest

from apartment_agent.sources.craigslist import parse_rss

FIXTURE_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>craigslist apa search</title>
    <item>
      <title>$1500 / 2br - Spacious apartment near park</title>
      <link>https://example.craigslist.org/apa/d/spacious-apartment/123.html</link>
      <description>Two bedroom apartment with parking and laundry.</description>
    </item>
    <item>
      <title>$950 / studio - Cozy downtown studio</title>
      <link>https://example.craigslist.org/apa/d/cozy-studio/456.html</link>
      <description>Studio, walk to everything.</description>
    </item>
  </channel>
</rss>
"""


class TestParseRss(unittest.TestCase):
    def test_parses_price_and_bedrooms_from_title(self):
        listings = parse_rss(FIXTURE_RSS, area="Example City")
        self.assertEqual(len(listings), 2)

        first = listings[0]
        self.assertEqual(first.price, 1500)
        self.assertEqual(first.bedrooms, 2)
        self.assertEqual(first.url, "https://example.craigslist.org/apa/d/spacious-apartment/123.html")
        self.assertEqual(first.source, "craigslist")

    def test_handles_missing_bedroom_count(self):
        listings = parse_rss(FIXTURE_RSS, area="Example City")
        second = listings[1]
        self.assertEqual(second.price, 950)
        self.assertIsNone(second.bedrooms)


if __name__ == "__main__":
    unittest.main()
