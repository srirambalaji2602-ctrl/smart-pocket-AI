from urllib.parse import quote_plus


class MarketplaceService:
    """
    Mock marketplace/search layer.

    It creates search links instead of pretending
    to access private marketplace APIs.
    """

    DOMAINS = {

        "Amazon":
            "https://www.amazon.in/s?k={q}",

        "Flipkart":
            "https://www.flipkart.com/search?q={q}",

        "IKEA":
            "https://www.ikea.com/in/en/search/?q={q}",

        "Swiggy":
            "https://www.swiggy.com/search?query={q}",

        "Zomato":
            "https://www.zomato.com/search?query={q}",

        "OYO":
            "https://www.oyorooms.com/search?location={q}",
    }

    def search_url(
        self,
        platform: str,
        query: str,
    ) -> str:

        template = self.DOMAINS.get(
            platform
        )

        if not template:
            return ""

        return template.format(
            q=quote_plus(query)
        )


marketplace = MarketplaceService()