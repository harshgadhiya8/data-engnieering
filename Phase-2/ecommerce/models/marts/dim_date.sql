Select
    ExTRACT(DAY FROM order_purchase_timestamp) AS day, 
    EXTRACT(MONTH FROM order_purchase_timestamp) AS month,
    EXTRACT(YEAR FROM order_purchase_timestamp) AS year,
    EXTRACT(DOW FROM order_purchase_timestamp) AS day_of_week,
    ExTRACT(QUARTER FROM order_purchase_timestamp) AS quarter
from {{ ref('stg_order') }}