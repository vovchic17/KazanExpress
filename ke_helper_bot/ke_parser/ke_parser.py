import re
import statistics
from typing import Any, ClassVar

from aiohttp import ClientSession

from .models import (
    CatalogCard,
    CharacteristicView,
    GoogleSheetProduct,
    Product,
    Review,
    Sku,
    SkuRatings,
    SkuRatingsItem,
)


class KEParser:
    """KazanExpress parser"""

    headers: ClassVar[dict[str, str]] = {
        "x-iid": "/",
        "user-agent": "/",
        "apollographql-client-name": "web-customers",
    }
    product_base_url = "https://api.kazanexpress.ru/api/v2/product"
    reviews_base_url = "https://api.kazanexpress.ru/api/product"
    actions_base_url = "https://api.kazanexpress.ru/api/product/actions"
    graphql_base_url = "https://graphql.kazanexpress.ru"

    @staticmethod
    def get_id_from_link(link: str) -> int:
        """Return poduct id from the product link"""
        matches = re.search(r"([\d]{5,}\?|[\d]{5,}$)", link)
        if matches is not None:
            return int(matches.group(1).replace("?", ""))
        msg = "No product id was found in the link"
        raise ValueError(msg, link)

    @staticmethod
    def get_skuid_from_link(link: str) -> int:
        """Return sku id from the product link"""
        matches = re.search(r"sku[I|i]d=([\d]+)", link)
        if matches is not None:
            return int(matches.group(1))
        msg = "No sku id was found in the link"
        raise ValueError(msg, link)

    async def get_product(self, session: ClientSession, product_id: int) -> Product:
        """Return the Product object"""
        resp = await session.get(
            f"{self.product_base_url}/{product_id}", headers=self.headers
        )
        resp_json = await resp.json()
        if "errors" in resp_json:
            raise LookupError(resp_json["errors"][0]["detailMessage"])
        product = resp_json["payload"]["data"]
        return Product.model_validate(product)

    async def get_info(
        self, link: str
    ) -> tuple[int, int, str, str, int | float, str, int | str]:
        """
        Return product_id, stock, title, shop name,
        price, characteristic, sku_id of product
        """
        prod_id = self.get_id_from_link(link)
        try:
            sku_id: int | str = self.get_skuid_from_link(link)
        except ValueError:
            sku_id = "no sku"

        async with ClientSession(headers=self.headers) as session:
            product = await self.get_product(session, prod_id)

        for sku in product.sku_list:
            if sku_id in (sku.id, "no sku"):
                return (
                    prod_id,
                    sku.available_amount,
                    product.title,
                    product.seller.title,
                    sku.purchase_price,
                    "".join(
                        [
                            product.characteristics[char.char_index]
                            .values[char.value_index]
                            .title
                            for char in sku.characteristics
                        ]
                    ),
                    sku_id,
                )

        msg = "The product with the following sku id was not found"
        raise LookupError(msg, sku_id)

    async def get_reviews(
        self, session: ClientSession, product_id: int
    ) -> list[Review]:
        """Return the reviews of the product"""
        resp = await session.get(
            f"{self.reviews_base_url}/{product_id}/reviews",
            headers=self.headers,
        )
        resp_json = await resp.json()
        reviews_raw = resp_json["payload"]
        return [Review.model_validate(review) for review in reviews_raw]

    async def get_ratings(
        self,
        session: ClientSession,
        link: str | None = None,
        product: Product | None = None,
    ) -> dict[int, Any]:
        """Return the rating of the each sku"""
        if link and product:
            msg = "Either link or product must be specified"
            raise ValueError(msg)
        if link is None and product is None:
            msg = "Either link or product must be specified"
            raise ValueError(msg)
        if link is not None:
            prod_id = self.get_id_from_link(link)
            product = await self.get_product(session, prod_id)
        else:
            prod_id = product.id

        reviews = await self.get_reviews(session, prod_id)

        ratings = {}

        for sku in product.sku_list:
            char_view = CharacteristicView(product.characteristics, sku)
            rates = [
                review.rating
                for review in reviews
                if char_view == review.characteristics
            ]
            ratings[sku.id] = {
                "rating": round(statistics.mean(rates), 2) if rates else 0,
                "reviews_count": len(rates),
            }
        return ratings

    async def get_week_orders(self, session: ClientSession, product_id: int) -> int:
        """Return the week product orders"""
        resp = await session.get(
            f"{self.actions_base_url}/{product_id}", headers=self.headers
        )
        resp_json = await resp.json()
        try:
            poppup_text = resp_json[0]["text"]
            return int(poppup_text.split()[0]) if "на этой неделе" in poppup_text else 0
        except IndexError as e:
            msg = "The product with the following id has no action"
            raise LookupError(msg, product_id) from e

    async def make_search(
        self,
        session: ClientSession,
        text: str,
        offset: int = 0,
        limit: int = 100,
    ) -> list[CatalogCard]:
        """
        Make a graphql makeSearch request
        returns a list of catalog cards
        """
        body = {
            "operationName": "getMakeSearch",
            "variables": {
                "queryInput": {
                    "text": text,
                    "showAdultContent": "NONE",
                    "correctQuery": True,
                    "getFastCategories": True,
                    "getPromotionItems": True,
                    "filters": [],
                    "sort": "BY_RELEVANCE_DESC",
                    "pagination": {"offset": offset, "limit": limit},
                }
            },
            "query": """
                query getMakeSearch($queryInput:MakeSearchQueryInput!)
                {
                    makeSearch(query:$queryInput) {
                        items {
                            catalogCard {
                                ...SkuGroupCardFragment
                            }
                        }
                        total
                    }
                }
                fragment SkuGroupCardFragment on SkuGroupCard {
                    ...DefaultCardFragment
                    characteristicValues {
                        title
                        id
                        characteristic {
                            id
                        }
                    }
                }
                fragment DefaultCardFragment on CatalogCard {
                    feedbackQuantity
                    id
                    minFullPrice
                    minSellPrice
                    ordersQuantity
                    productId
                    rating
                    title
                }
            """,
        }
        resp = await session.post(
            self.graphql_base_url, json=body, headers=self.headers
        )
        resp_json = await resp.json()
        items_raw = tuple(
            item["catalogCard"] for item in resp_json["data"]["makeSearch"]["items"]
        )
        for pos, item in enumerate(items_raw, offset + 1):
            item["position"] = pos
            item["cards_count"] = resp_json["data"]["makeSearch"]["total"]
        return [CatalogCard.model_validate(item) for item in items_raw]

    async def make_search_all(
        self,
        session: ClientSession,
        text: str,
    ) -> list[CatalogCard]:
        """Return all the catalog cards from the search"""
        offset = 0
        cards = await self.make_search(session, text)
        while len(cards) < cards[-1].cards_count:
            offset += 100
            cards.extend(await self.make_search(session, text, offset))
        return cards

    async def get_all_info(
        self, session: ClientSession, search_query: str, link: str
    ) -> GoogleSheetProduct:
        """Return all the product info"""
        # get the product id and the product sku id
        try:
            product_id = self.get_id_from_link(link)
        except ValueError:
            return GoogleSheetProduct(shop="Не найдено")
        try:
            product_skuid: int | str = self.get_skuid_from_link(link)
        except ValueError:
            product_skuid = "no sku"
        try:
            product = await self.get_product(session, product_id)
        except LookupError:
            return GoogleSheetProduct(shop="Не найдено")
        product_sku: Sku
        for sku in product.sku_list:
            if product_skuid in (sku.id, "no sku"):
                product_sku = sku
                break
        else:
            return GoogleSheetProduct(shop="Не найдено")
        char_view = CharacteristicView(product.characteristics, product_sku)
        search_position: int | str = "no"
        search_result = await self.make_search_all(session, search_query)
        total_count = search_result[-1].cards_count
        for card in search_result:
            if (
                card.product_id == product_id
                and char_view == card.characteristic_values
            ):
                search_position = card.position
                product.orders_amount = card.orders_quantity
                break
        # parse reviews to calculate
        # the rating for each sku
        reviews = [
            review
            for review in await self.get_reviews(session, product_id)
            if char_view == review.characteristics
        ]

        rating = round(
            statistics.mean([review.rating for review in reviews] or [0]),
            2,
        )
        # get week orders
        week_order_count = await self.get_week_orders(session, product_id)
        return GoogleSheetProduct(
            title=product.title,
            shop=product.seller.title,
            characteristic=" ".join([char.value for char in char_view.characteristics]),
            product_id=product_id,
            product_skuid=product_skuid,
            reviews_count=len(reviews),
            rating=rating,
            order_count=product.orders_amount,
            week_order_count=week_order_count,
            stock=product_sku.available_amount,
            price=product_sku.purchase_price,
            search_position=search_position,
            total_count=total_count,
        )

    async def get_ratings_info(self, link: str) -> SkuRatings:
        """Return info of product and its skus rating"""
        prod_id = self.get_id_from_link(link)
        async with ClientSession(headers=self.headers) as session:
            product = await self.get_product(session, prod_id)
            cards = list(
                filter(
                    lambda x: x.product_id == prod_id,
                    # search by title to get all the skus
                    await self.make_search_all(session, product.title),
                )
            )
            ratings = await self.get_ratings(session, product=product)

            items: list[SkuRatingsItem] = []

            for sku in product.sku_list:
                char_view = CharacteristicView(product.characteristics, sku)
                items.extend(
                    [
                        SkuRatingsItem(
                            characteristic=" ".join(
                                char.title for char in card.characteristic_values
                            ),
                            rating=ratings[sku.id]["rating"],
                            sku_id=sku.id,
                            orders=card.orders_quantity,
                            reviews=ratings[sku.id]["reviews_count"],
                        )
                        for card in cards
                        if char_view == card.characteristic_values
                    ]
                )

        return SkuRatings(
            title=product.title,
            link=f"https://kazanexpress.ru/product/{prod_id}",
            rating=product.rating,
            shop=product.seller.title,
            shop_link=f"https://kazanexpress.ru/{product.seller.link}",
            items=items,
        )
