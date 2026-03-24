{{ config(
    materialized='incremental',
    unique_key=["order_id", "order_item_id"]
) }}

Select o.order_id,
        ot.order_item_id,
        o.customer_id,
        ot.product_id,
        ot.seller_id,
        o.order_purchase_timestamp,
        ot.price,
        ot.freight_value,
        op.payment_value,
        odr.review_score,
        o.order_status
from {{ ref('stg_order') }} o
join {{ ref('stg_order_item') }} ot on o.order_id = ot.order_id
join {{ ref('stg_order_payments') }} op on o.order_id = op.order_id
join {{ ref('stg_order_reviews') }} odr on o.order_id = odr.order_id
{% if is_incremental() %}
where o.order_purchase_timestamp > (select max(order_purchase_timestamp) from {{ this }})
{% endif %}
