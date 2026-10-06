from math import floor

from .marketplace_service import marketplace


def _item(
    category,
    name,
    price,
    quantity,
    platform,
    reason,
):

    return {
        "category": category,
        "name": name,
        "estimated_price": round(
            float(price),
            2,
        ),
        "quantity": int(quantity),
        "platform": platform,
        "reason": reason,
        "search_url": marketplace.search_url(
            platform,
            name,
        ),
    }


def home_fallback(data: dict):

    budget = data["budget"]

    style = data.get(
        "style",
        "modern",
    )

    items = data.get(
        "items",
        {},
    )

    requested = []

    catalog = [

        (
            "Lighting",
            "LED ceiling light",
            899,
            "Amazon",
        ),

        (
            "Fan",
            "Energy efficient ceiling fan",
            1899,
            "Amazon",
        ),

        (
            "Decor",
            "Minimal wall art set",
            799,
            "IKEA",
        ),

        (
            "Storage",
            "Modular storage shelf",
            2499,
            "IKEA",
        ),

        (
            "Table",
            "Compact dining table",
            6999,
            "IKEA",
        ),

        (
            "Rug",
            "Geometric area rug",
            1799,
            "Amazon",
        ),

        (
            "Curtains",
            "Blackout curtain pair",
            1299,
            "Flipkart",
        ),
    ]

    for category, name, price, platform in catalog:

        qty = int(
            items.get(
                category.lower(),
                items.get(
                    category,
                    1,
                ),
            )
            or 1
        )

        qty = max(
            1,
            min(qty, 10),
        )

        requested.append(
            _item(
                category,
                name,
                price,
                qty,
                platform,
                (
                    f"Works with a {style} "
                    "look and keeps the plan "
                    "budget-conscious."
                ),
            )
        )

    selected = []

    total = 0

    for item in requested:

        cost = (
            item["estimated_price"]
            * item["quantity"]
        )

        if total + cost <= budget:

            selected.append(item)

            total += cost

    if not selected:

        item = requested[0]

        item["quantity"] = 1

        selected = [item]

        total = item["estimated_price"]

    allocations = {

        "Furniture":
            round(
                budget * 0.45,
                2,
            ),

        "Lighting":
            round(
                budget * 0.15,
                2,
            ),

        "Decor":
            round(
                budget * 0.20,
                2,
            ),

        "Storage":
            round(
                budget * 0.20,
                2,
            ),
    }

    return {

        "planner": "home",

        "budget": budget,

        "allocated_total":
            round(total, 2),

        "summary":
            (
                f"A {style} home setup "
                f"using the requested "
                f"rooms/items while "
                f"keeping the estimated "
                f"catalog spend near "
                f"₹{budget:,.0f}."
            ),

        "tips": [

            "Measure rooms before buying large furniture.",

            "Keep a 10% contingency for delivery or installation.",

            "Compare the same item across platforms before purchasing.",
        ],

        "allocations": allocations,

        "recommendations": selected,

        "ai_used": False,
    }


def party_fallback(data: dict):

    budget = data["budget"]

    guests = data["guests"]

    event = data.get(
        "event_type",
        "birthday",
    )

    food_budget = budget * 0.45

    decor_budget = budget * 0.20

    venue_budget = budget * 0.20

    misc_budget = budget * 0.15

    food_per_guest = max(
        120,
        floor(
            food_budget / guests
        ),
    )

    items = [

        _item(
            "Catering",
            f"{event.title()} meal package",
            food_per_guest,
            guests,
            "Swiggy",
            (
                f"Estimated around "
                f"₹{food_per_guest} "
                "per guest."
            ),
        ),

        _item(
            "Decor",
            f"{event.title()} decoration package",
            decor_budget,
            1,
            "Amazon",
            "Budget-friendly decoration direction.",
        ),

        _item(
            "Venue",
            data.get(
                "venue",
                "home",
            ) + " event venue",
            venue_budget,
            1,
            "OYO",
            (
                "Venue allocation is "
                "capped so food remains "
                "the largest spend."
            ),
        ),

        _item(
            "Miscellaneous",
            "Party supplies and contingency",
            misc_budget,
            1,
            "Flipkart",
            (
                "Useful for invitations, "
                "disposables, small props "
                "or last-minute needs."
            ),
        ),
    ]

    return {

        "planner": "party",

        "budget": budget,

        "allocated_total":
            round(budget, 2),

        "summary":
            (
                f"A {event} plan for "
                f"{guests} guests with "
                "proportional allocations "
                "for food, decor, venue "
                "and contingency."
            ),

        "tips": [

            "Confirm per-person food pricing before booking.",

            "Keep a contingency amount for last-minute purchases.",

            "For small groups, a home venue can reduce fixed costs.",
        ],

        "allocations": {

            "Catering":
                round(food_budget, 2),

            "Decoration":
                round(decor_budget, 2),

            "Venue":
                round(venue_budget, 2),

            "Contingency":
                round(misc_budget, 2),
        },

        "recommendations": items,

        "ai_used": False,
    }


def jewelry_fallback(data: dict):

    budget = data["budget"]

    occasion = data.get(
        "occasion",
        "party",
    )

    style = data.get(
        "style",
        "minimal",
    )

    metal = data.get(
        "preferred_metal",
        "any",
    )

    catalog = [

        (
            "Earrings",
            "Minimal statement earrings",
            799,
            "Amazon",
        ),

        (
            "Necklace",
            "Layered elegant necklace",
            1299,
            "Flipkart",
        ),

        (
            "Bracelet",
            "Slim bracelet",
            699,
            "Amazon",
        ),

        (
            "Bangles",
            "Classic bangle set",
            999,
            "Flipkart",
        ),
    ]

    selected = []

    total = 0

    for category, name, price, platform in catalog:

        if total + price <= budget:

            selected.append(
                _item(
                    category,
                    name,
                    price,
                    1,
                    platform,
                    (
                        f"Suitable for a "
                        f"{style} {occasion} look; "
                        f"metal preference: {metal}."
                    ),
                )
            )

            total += price

    if not selected:

        selected = [

            _item(
                "Earrings",
                "Budget fashion earrings",
                min(499, budget),
                1,
                "Amazon",
                "Low-cost starting option.",
            )
        ]

        total = selected[0][
            "estimated_price"
        ]

    return {

        "planner": "jewelry",

        "budget": budget,

        "allocated_total":
            round(total, 2),

        "summary":
            (
                f"Jewelry suggestions for "
                f"a {occasion} occasion with "
                f"a {style} style direction. "
                "Outfit-image analysis is optional."
            ),

        "tips": [

            "Match jewelry scale to the neckline and outfit detail.",

            "Check dimensions and material before purchase.",

            "Treat marketplace prices as estimates until you verify the listing.",
        ],

        "allocations": {

            "Primary piece":
                round(
                    budget * 0.50,
                    2,
                ),

            "Secondary piece":
                round(
                    budget * 0.30,
                    2,
                ),

            "Reserve":
                round(
                    budget * 0.20,
                    2,
                ),
        },

        "recommendations": selected,

        "ai_used": False,
    }