Select
    order_id,
    order_item_id,
    product_id,
    shipping_limit_date,
    freight_value,
    seller_id,
    price
from {{ source('raw', 'order_item') }}