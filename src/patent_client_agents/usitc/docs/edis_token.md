## EDIS API Tokens

1. Log into https://edis.usitc.gov via Login.gov.
2. Use the profile dropdown → "API Token Generator" to issue a bearer token.
3. Set `USITC_EDIS_TOKEN` in your environment; include `Authorization: Bearer <token>` on calls.
4. Tokens expire; regenerate via the UI and update the env var when requests start failing.
