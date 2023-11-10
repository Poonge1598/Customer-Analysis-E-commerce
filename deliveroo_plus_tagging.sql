WITH MTE AS (
SELECT id_customer_synth,order_datetime_synth,is_free_delivery,SUM(is_free_delivery) OVER(PARTITION BY id_customer_synth ORDER BY order_datetime_synth ASC
ROWS 2 PRECEDING) AS running_total,
FROM `dsba-head-of-data-101.assignment_data.synthetic_deliveroo_plus_dataset` ),

CTE AS (
SELECT id_customer_synth,order_datetime_synth,is_free_delivery,running_total,
CASE WHEN running_total=3 THEN 1 ELSE 0
END AS sub
FROM
MTE
),

MAIN AS (
SELECT id_customer_synth,order_datetime_synth,is_free_delivery,running_total,sub,
CASE WHEN is_free_delivery=1 THEN MAX(sub) OVER(PARTITION BY id_customer_synth ORDER BY order_datetime_synth ROWS BETWEEN CURRENT ROW AND 2 FOLLOWING)
ELSE cte.sub 
END AS subscription
FROM CTE

ORDER BY id_customer_synth,order_datetime_synth
),

START AS (
SELECT
id_customer_synth AS id,
order_datetime_synth AS order_time,
is_free_delivery,
running_total,
sub,
subscription,
CASE
WHEN subscription = 1 AND LAG(subscription,1,0) OVER (PARTITION BY id_customer_synth ORDER BY order_datetime_synth) = 0
THEN order_datetime_synth
ELSE NULL
END AS start_date,
CASE
WHEN subscription = 1 AND LEAD(subscription,1,0) OVER (PARTITION BY id_customer_synth ORDER BY order_datetime_synth) = 0
THEN order_datetime_synth
ELSE NULL
END AS end_date
FROM
MAIN
),
CYCLES AS (
SELECT
id,
order_time,
is_free_delivery,
running_total,
sub,
subscription,start_date,end_date,
MAX(start_date) OVER (PARTITION BY id, subscription ORDER BY order_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cycle_start_date,
MIN(end_date) OVER (PARTITION BY id, subscription ORDER BY order_time DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cycle_end_date
FROM
START
)
SELECT
id,order_time,is_free_delivery,subscription,cycle_start_date,cycle_end_date
FROM
CYCLES
ORDER BY id,order_time ASC