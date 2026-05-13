# EUIPO API — authoritative facts from OpenAPI specs

Sourced directly from `research/openapi/euipo_trademark_search.json` and `euipo_design_search.json` (downloaded from the authenticated EUIPO Dev Portal, 2026-05-13).

## Auth

| Item | Value |
|---|---|
| Production token URL | `https://euipo.europa.eu/cas-server-webapp/oidc/accessToken` |
| ClientID header (apiKey) | `X-IBM-Client-Id` (in: header) |
| OAuth scheme name (server flow) | `Oauth2ClientCredentials` |
| OAuth scheme name (user flow) | `Oauth2AuthorizationCode` |
| Bearer header | `Authorization: Bearer <access_token>` |

Every request requires **BOTH** `X-IBM-Client-Id` AND OAuth2 Bearer token.

### Scope choice per flow

| API | `clientCredentials` scope | `authorizationCode` scope |
|---|---|---|
| Trademark Search | `uid` — "Grants read access to trade marks" | `trademark-search.trademarks.read` — "Grants read access to trade marks" |
| Design Search | `uid` — "Grants **partial** read access to user EU Designs **under certain conditions**" | `design-search.designs.read` — "Grants **complete** read access to user EU designs" |

**Design Search** explicitly warns that the `clientCredentials` flow has partial coverage. For full register access, the 3-legged `authorizationCode` flow appears necessary for designs.

**Trademark Search** scope descriptions look equivalent for both flows on the surface; needs live testing to confirm whether `clientCredentials` actually covers the full register.

## Base URLs (production)

- Trademark Search: `https://api.euipo.europa.eu/trademark-search`
- Design Search:    `https://api.euipo.europa.eu/design-search`

## Endpoint surface

### Trademark Search (OpenAPI 3.0.0, v1.0.0)

| Method | Path |
|---|---|
| GET | `/trademarks` (search) |
| GET | `/trademarks/{applicationNumber}` |
| GET | `/trademarks/{applicationNumber}/image` |
| GET | `/trademarks/{applicationNumber}/image/thumbnail` |
| GET | `/trademarks/{applicationNumber}/sound` |
| GET | `/trademarks/{applicationNumber}/video` |
| GET | `/trademarks/{applicationNumber}/model` |

### Design Search (OpenAPI 3.0.2, v1.0.0)

| Method | Path |
|---|---|
| GET | `/designs` (search) |
| GET | `/designs/{designNumber}` |
| GET | `/designs/{designNumber}/views/{order}` |
| GET | `/designs/{designNumber}/views/{order}/thumbnail` |
| GET | `/designs/{designNumber}/model` |

## Other useful specs also saved (bonus, downloaded same trip)

- `euipo_document_repository.json` — file inspection / docs
- `euipo_persons.json` — applicant/rep lookups
- `euipo_goods_and_services.json` — Nice classification helpers
- `euipo_product_indications.json` — TMclass-style product lookups

## Open question (post-spec)

The original research doc flagged "OAuth flow choice" as uncertain. **The spec now confirms BOTH flows exist for both APIs**, but with different scopes. The narrow question is now: does `clientCredentials` + scope `uid` give full-register reads, or only entries owned by the calling user/firm? Design Search explicitly says "partial under certain conditions"; Trademark Search's description is ambiguous. Resolve with a live smoke test once credentials are issued.

## What the user still needs to do

1. Create an **App** in the dev portal at `https://dev.euipo.europa.eu/user/{uid}/apps/create` — generates `client_id` and `client_secret`.
2. Subscribe the app to the **Trademark Search** and **Design Search** products (and any others we want, e.g. Document Repository).
3. Decide which OAuth flow we wire into the library — see "Scope choice" above.
