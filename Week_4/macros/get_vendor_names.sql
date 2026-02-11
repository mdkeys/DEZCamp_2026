{% macro get_vendor_names(vendor_id) -%}
CASE
	WHEN {{vendor_id}} = 1 then 'Creative Mobile Technologies, LLC'
	WHEN {{vendor_id}} = 2 then 'VeriFone Inc.'
	WHEN {{vendor_id}} = 4 then 'Unknown Vendor'
END
{%- endmacro %}
