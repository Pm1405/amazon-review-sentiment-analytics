{{
    config(
        materialized='view'
    )
}}

with source as (
    select * from {{ source('raw', 'reviews_with_sentiment') }}
),

cleaned as (
    select
        REVIEWID as review_id,
        MAINDEPARTMENT as department,
        SUBDEPARTMENT as sub_department,
        PRODUCTNAME as product_name,
        REVIEWTITLE as review_title,
        REVIEWTEXT as review_text,
        TRY_CAST(REVIEWSTAR as FLOAT) as star_rating,
        AI_SENTIMENT_SCORE as sentiment_score,
        AI_SENTIMENT_LABEL as sentiment_label,
        INCONSISTENTSTATUS as inconsistent_flag,
        TRY_TO_DATE(
            REGEXP_REPLACE(REVIEWDATE, 'Reviewed in the United States on ', ''),
            'MMMM DD, YYYY'
        ) as review_date
    from source
)

select *
from cleaned
where star_rating is not null
