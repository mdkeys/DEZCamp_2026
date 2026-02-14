{% macro get_payment_type(payment_type) -%}
CASE
	WHEN {{payment_type}} = 0 then 'Flex Fare trip'
	WHEN {{payment_type}} = 1 then 'Credit card'
	WHEN {{payment_type}} = 2 then 'Cash'
    WHEN {{payment_type}} = 3 then 'No charge'
    WHEN {{payment_type}} = 4 then 'Dispute'
    WHEN {{payment_type}} = 5 then 'Unknown'
    WHEN {{payment_type}} = 6 then 'Voided trip'            
END
{%- endmacro %}