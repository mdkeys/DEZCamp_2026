{#  -- DEZC: 
    Claude explanation: This macro creates a database-agnostic casting function that uses the best casting method for each database type.
    Uses BQ's "safe_cast" function and returns NULL if the cast fails (instead of error)
    If not BQ, uses standard "cast" function and throws an error if the cast fails
#}

{% macro safe_cast(column, data_type) %}
    {% if target.type == 'bigquery' %}
        safe_cast({{ column }} as {{ data_type }})
    {% else %}
        cast({{ column }} as {{ data_type }})
    {% endif %}
{% endmacro %}