from dataclasses import dataclass
from datetime import datetime

from pydantic import BaseModel, Field


class ProductCharacteristicValue(BaseModel):
    """ProductCharacteristicValue model"""

    id: int
    title: str
    value: str


class ProductCharacteristic(BaseModel):
    """ProductCharacteristic model"""

    id: int
    title: str
    values: list[ProductCharacteristicValue]


class ProductSeller(BaseModel):
    """ProductSeller model"""

    id: int
    title: str
    link: str
    banner: str | None = None
    avatar: str | None = None
    description: str | None = None
    has_charity_products: bool = Field(alias="hasCharityProducts")
    registration_date: datetime = Field(alias="registrationDate")
    rating: float
    reviews: int
    orders: int
    official: bool
    contacts: list
    categories: list
    current_category: str | None = Field(alias="currentCategory", default=None)
    filters: list
    applied_filters: list = Field(alias="appliedFilters")
    price_filter: str | None = Field(alias="priceFilter", default=None)
    total_products: int = Field(alias="totalProducts")
    parents: list
    products: list
    seller_account_id: int = Field(alias="sellerAccountId")
    info: str | None = None


class SkuCharacteristic(BaseModel):
    """SkuCharacteristic model"""

    char_index: int = Field(alias="charIndex")
    value_index: int = Field(alias="valueIndex")


class Sku(BaseModel):
    """Sku model"""

    id: int
    characteristics: list[SkuCharacteristic]
    available_amount: int = Field(alias="availableAmount")
    full_price: int | None = Field(alias="fullPrice", default=None)
    charity_profit: int = Field(alias="charityProfit")
    purchase_price: int | float = Field(alias="purchasePrice")
    barcode: int
    address: str | None = None
    dimension: dict
    offer: dict | None = None
    discount_badge: dict | None = Field(alias="discountBadge", default=None)
    installment: dict | None
    product_option_dtos: list = Field(alias="productOptionDtos")
    vat: dict
    circular_photos_list: list = Field(alias="circularPhotosList")
    video_url: str | None = Field(alias="videoUrl", default=None)
    sell_price: int = Field(alias="sellPrice")


class Product(BaseModel):
    """Product model"""

    id: int
    title: str
    category: dict
    rating: float
    reviews_amount: int = Field(alias="reviewsAmount")
    orders_amount: int = Field(alias="ordersAmount")
    r_orders_amount: int = Field(alias="rOrdersAmount")
    total_avaliable_amount: int = Field(alias="totalAvailableAmount")
    charity_commission: int = Field(alias="charityCommission")
    description: str
    comments: list
    attributes: list
    tags: list
    synonyms: list
    photos: list
    video: str | None = None
    has_circular_photos: bool = Field(alias="hasCircularPhotos")
    circular_photos_list: list = Field(alias="circularPhotosList")
    characteristics: list[ProductCharacteristic]
    sku_list: list[Sku] = Field(alias="skuList")
    seller: ProductSeller
    top_feedback: dict | None = Field(alias="topFeedback")
    is_eco: bool = Field(alias="isEco")
    is_perishable: bool = Field(alias="isPerishable")
    has_vertical_photo: bool = Field(alias="hasVerticalPhoto")
    show_kitty: bool = Field(alias="showKitty")
    bonus_product: bool = Field(alias="bonusProduct")
    badges: list
    volume_discount: str | None = None
    color_photo_preview: bool = Field(alias="colorPhotoPreview")
    favourite: bool
    adult_category: bool = Field(alias="adultCategory")


class CatalogCardCharacteristic(BaseModel):
    """CatalogCardCharacteristic model"""

    id: int


class CatalogCardCharacteristicValue(BaseModel):
    """CatalogCardCharacteristicValue model"""

    characteristic: CatalogCardCharacteristic
    id: int
    title: str


class CatalogCard(BaseModel):
    """CatalogCard model"""

    characteristic_values: list[CatalogCardCharacteristicValue] = Field(
        alias="characteristicValues"
    )
    feedback_quantity: int = Field(alias="feedbackQuantity")
    id: int
    min_full_price: int = Field(alias="minFullPrice")
    min_sell_price: int = Field(alias="minSellPrice")
    orders_quantity: int = Field(alias="ordersQuantity")
    product_id: int = Field(alias="productId")
    rating: float
    title: str
    position: int
    cards_count: int


class ReviewReply(BaseModel):
    """ReviewReply model"""

    id: int
    date: datetime
    edited: bool
    content: str
    shop: str
    photos: list
    liked: int | None
    disliked: int | None


class ReviewCharacteristic(BaseModel):
    """ReviewCharacteristic model"""

    characteristic: str
    characteristic_value: str = Field(alias="characteristicValue")


class Review(BaseModel):
    """Review model"""

    review_id: int = Field(alias="reviewId")
    product_id: int = Field(alias="productId")
    date: datetime
    edited: bool
    customer: str
    reply: ReviewReply | None = None
    rating: int
    characteristics: list[ReviewCharacteristic]
    pros: str | None = None
    cons: str | None = None
    content: str | None = None
    photos: list
    status: str
    has_vertical_photo: bool | None = Field(alias="hasVerticalPhoto", default=None)
    like: bool
    dislike: bool
    amount_like: int = Field(alias="amountLike")
    amount_dislike: int = Field(alias="amountDislike")
    id: int
    is_anonymous: bool = Field(alias="isAnonymous")


@dataclass(frozen=True)
class Characteristic:
    """A dataclass for characteristic"""

    char: str
    value: str

    char_index: int
    value_index: int


class CharacteristicView:
    """
    A view defined by the list of
    ProductCharacteristic and Sku
    joins the titles and ids of
    characteristics and its values
    """

    characteristics: list[Characteristic]

    def __init__(self, product_chars: list[ProductCharacteristic], sku: Sku) -> None:
        self.characteristics = [
            Characteristic(
                product_chars[char.char_index].title,
                product_chars[char.char_index].values[char.value_index].title,
                product_chars[char.char_index].id,
                product_chars[char.char_index].values[char.value_index].id,
            )
            for char in sku.characteristics
        ]

    def __eq__(self, characteristic_values: object) -> bool:
        """
        Compare the list of characteristics
        with the characteristic values of the catalog card
        """
        if not isinstance(characteristic_values, list):
            raise NotImplementedError
        if all(
            isinstance(char, CatalogCardCharacteristicValue)
            for char in characteristic_values
        ):
            for char_value in characteristic_values:
                if not any(
                    char.value_index == char_value.id
                    and char.char_index == char_value.characteristic.id
                    for char in self.characteristics
                ):
                    return False
            return True

        if all(
            isinstance(char, ReviewCharacteristic) for char in characteristic_values
        ):
            for char_value in characteristic_values:
                if not any(
                    char.char == char_value.characteristic
                    and char.value == char_value.characteristic_value
                    for char in self.characteristics
                ):
                    return False
            return True

        msg = "Wrong type of list values"
        raise ValueError(msg)


class GoogleSheetProduct(BaseModel):
    """A record of product to insert in Google sheet"""

    title: str = ""
    shop: str = ""
    characteristic: str = ""
    product_id: int | str = ""
    product_skuid: int | str = ""
    reviews_count: int | str = ""
    rating: float | str = ""
    order_count: int | str = ""
    week_order_count: int | str = ""
    stock: int | str = ""
    price: float | str = ""
    search_position: int | str = ""
    total_count: int | str = ""


class SkuRatingsItem(BaseModel):
    """An item of sku ratings"""

    characteristic: str
    rating: float
    sku_id: int
    orders: int
    reviews: int


class SkuRatings(BaseModel):
    """A record of sku ratings"""

    title: str
    link: str
    rating: float
    shop: str
    shop_link: str
    items: list[SkuRatingsItem]
