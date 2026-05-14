## HTS REST endpoints

* Search: `GET https://hts.usitc.gov/reststop/search?keyword=...` (returns up to 100 rows).
* Range export: `GET .../exportList?from=XXXX&to=YYYY&format=JSON|CSV|XLSX&styles=true|false`.
* No auth required, but respect polite rate limits and reuse cached data when possible.
