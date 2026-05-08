{{
    config(
        materialized='table'
    )
}}

select
    review_date,
    date_trunc('month', review_date) as review_month,
    department,
    count(*) as total_reviews,
    round(avg(star_rating), 2) as avg_star_rating,
    round(avg(sentiment_score), 3) as avg_sentiment_score,
    sum(case when sentiment_label = 'Positive' then 1 else 0 end) as positive_reviews,
    sum(case when sentiment_label = 'Negative' then 1 else 0 end) as negative_reviews
from {{ ref('stg_reviews') }}
where review_date is not null
group by review_date, date_trunc('month', review_date), department
order by review_date
