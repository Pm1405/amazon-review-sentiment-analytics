{{
    config(
        materialized='table'
    )
}}

select
    department,
    sub_department,
    count(*) as total_reviews,
    round(avg(star_rating), 2) as avg_star_rating,
    round(avg(sentiment_score) * 100, 1) as happiness_score,
    sum(case when sentiment_label = 'Positive' then 1 else 0 end) as positive_reviews,
    sum(case when sentiment_label = 'Negative' then 1 else 0 end) as negative_reviews,
    round(sum(case when sentiment_label = 'Positive' then 1 else 0 end)::float / count(*) * 100, 1) as positive_pct
from {{ ref('stg_reviews') }}
group by department, sub_department
order by department, total_reviews desc
