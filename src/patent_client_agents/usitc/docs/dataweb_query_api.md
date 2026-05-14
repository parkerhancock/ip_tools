# USITC Dataweb Query API - Complete Reference Guide

## Quick Start

**Base URL:** `https://datawebws.usitc.gov/dataweb`

**Authentication:** Bearer token in Authorization header
```
Authorization: Bearer <your-api-token>
```

Get your API token from: https://dataweb.usitc.com/api-key (requires login)

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Query Structure](#query-structure)
4. [Core Endpoints](#core-endpoints)
5. [Query Parameters Reference](#query-parameters-reference)
6. [Data Models](#data-models)
7. [Examples](#examples)
8. [API Reference - All Endpoints](#api-reference---all-endpoints)

---

## Overview

The USITC Dataweb API allows users with API credentials to bypass the web application and send queries directly to the API. The Dataweb API is tool-agnostic, so any HTTP-capable tools will be compatible.

**Key Features:**
- Tool-agnostic HTTP API (works with any HTTP client)
- Direct data access via API queries
- Support for complex trade data queries
- Saved query management
- Multiple data formats and aggregation options

---

## Authentication

### Bearer Token

Include your API token in the Authorization header:

```
Authorization: Bearer <your-api-token>
```

### Token Management

- Get your API token from: https://dataweb.usitc.com/api-key
- Tokens are user-specific and tied to your Dataweb account
- Tokens can be created, copied, and revoked through the Dataweb UI

---

## Query Structure

All data queries to the API use a standardized JSON query object structure.

### Basic Query Object

```json
{
 "savedQueryName":"",
 "savedQueryDesc":"",
 "isOwner":True,
 "runMonthly":False,
 "reportOptions":{
 "tradeType":"Import",
 "classificationSystem":"HTS"
 },
 "searchOptions":{
 "MiscGroup":{
 "districts":{
 "aggregation":"Aggregate District",
 "districtGroups":{
 "userGroups":[]
 },
 "districts":[],
 "districtsExpanded":
 [
 {
 "name":"All Districts",
 "value":"all"
 }
 ],
 "districtsSelectType":"all"
 },
 "importPrograms":{
 "aggregation":None,
 "importPrograms":[],
 "programsSelectType":"all"
 },
 "extImportPrograms":{
 "aggregation":"Aggregate CSC",
 "extImportPrograms":[],
 "extImportProgramsExpanded":[],
 "programsSelectType":"all"
 },
 "provisionCodes":{
 "aggregation":"Aggregate RPCODE",
 "provisionCodesSelectType":"all",
 "rateProvisionCodes":[],
 "rateProvisionCodesExpanded":[]
 }
 },
 "commodities":{
 "aggregation":"Aggregate Commodities",
 "codeDisplayFormat":"YES",
 "commodities":[],
 "commoditiesExpanded":[],
 "commoditiesManual":"",
 "commodityGroups":{
 "systemGroups":[],
 "userGroups":[]
 },
 "commoditySelectType":"all",
 "granularity":"2",
 "groupGranularity":None,
 "searchGranularity":None
 },
 "componentSettings":{
 "dataToReport":
 [
 "CONS_FIR_UNIT_QUANT"
 ],
 "scale":"1",
 "timeframeSelectType":"fullYears",
 "years":
 [
 "2022","2023"
 ],
 "startDate":None,
 "endDate":None,
 "startMonth":None,
 "endMonth":None,
 "yearsTimeline":"Annual"
 },
 "countries":{
 "aggregation":"Aggregate Countries",
 "countries":[],
 "countriesExpanded":
 [
 {
 "name":"All Countries",
 "value":"all"
 }
 ],
 "countriesSelectType":"all",
 "countryGroups":{
 "systemGroups":[],
 "userGroups":[]
 }
 }
 },
 "sortingAndDataFormat":{
 "DataSort":{
 "columnOrder":[],
 "fullColumnOrder":[],
 "sortOrder":[]
 },
 "reportCustomizations":{
 "exportCombineTables":False,
 "showAllSubtotal":True,
 "subtotalRecords":"",
 "totalRecords":"20000",
 "exportRawData":False
 }
 }
}
```


### Query Object Properties

The query object contains the following main sections:

#### Report Options
- **tradeType**: Type of trade data (Import, Export, GenImp, TotExp, Balance, ForeignExp, ImpExp)
- **classificationSystem**: Classification system (QUICK, HTS, SIC, SITC, NAIC, EXPERT)

#### Search Options
- **componentSettings**: Time period, data metrics, scale
- **countries**: Country selection and grouping
- **commodities**: Product/commodity selection and grouping
- **MiscGroup**: Districts, programs, provision codes

#### Sorting and Data Format
- **DataSort**: Column order and sort order
- **reportCustomizations**: Export options, subtotals, row limits

---

## Core Endpoints

### 1. Run Query/Report

```
POST /api/v2/report2/runReport
```

**Description:** Execute a data query and return results

**Request Body:** Query object (see Query Structure above)

**Response:** JSON object with data in tables, rows, and columns

**Example:**
```json
{
  "reportOptions": {
    "tradeType": "Import",
    "classificationSystem": "HTS"
  },
  "searchOptions": {
    "countries": { "countriesSelectType": "all" },
    "commodities": { "commoditySelectType": "all" },
    "componentSettings": {
      "timeframeSelectType": "fullYears",
      "years": ["2022", "2023"],
      "yearsTimeline": "Annual",
      "dataToReport": ["CONS_FIR_UNIT_QUANT"],
      "scale": "1"
    },
    "MiscGroup": { ... }
  },
  "sortingAndDataFormat": { ... }
}
```

### 2. Get All Countries

```
GET /api/v2/country/getAllCountries
```

**Description:** Retrieve list of all available countries

**Response:** Array of country objects with value and name

**Example Response:**
```json
{
  "options": [
    {"value": "0016", "name": "Afghanistan"},
    {"value": "0002", "name": "Albania"},
    ...
  ]
}
```

### 3. Get User Country Groups

```
GET /api/v2/country/getAllUserGroupsWithCountries
```

**Description:** Get user-saved country groupings

**Response:** Array of user-defined country groups

### 4. Get Saved Queries

```
GET /api/v2/savedQuery/getAllSavedQueries
```

**Description:** Retrieve all saved queries associated with the API token user

**Response:** Array of saved query objects

### 5. Get All Commodities (System Groups)

```
POST /api/v2/commodity/getAllSystemGroupsWithCommodities
```

**Description:** Get system-managed commodity groups

**Request Body:**
```json
{
  "tradeType": "Import",
  "classificationSystem": "HTS",
  "timeframesSelectedTab": "fullYears"
}
```

### 6. Get All Commodities (User Groups)

```
POST /api/v2/commodity/getAllUserGroupsWithCommodities
```

**Description:** Get user-saved commodity groups

**Request Body:** Same as system groups

### 7. Get Districts (User Groups)

```
GET /api/v2/district/getAllUserGroupsWithDistricts
```

**Description:** Get user-saved district groupings

### 8. Get All Districts

```
GET /api/v2/district/getAllDistricts
```

**Description:** Get complete list of all available districts

### 9. Get Import Programs

```
POST /api/v2/query/getImportPrograms
```

**Description:** Get list of available import programs

**Request Body:**
```json
{"tradeType": "Import"}
```

### 10. Get Rate Provision Codes

```
POST /api/v2/query/getRPCodesList
```

**Description:** Get list of rate provision codes

**Request Body:**
```json
{"tradeType": "Import"}
```

---

## Query Parameters Reference

### Trade Types

- **Import**: Imports for Consumption
- **Export**: Domestic Exports
- **GenImp**: General Imports
- **TotExp**: Total Exports
- **Balance**: Trade Balance
- **ForeignExp**: Foreign Exports
- **ImpExp**: Imports and Exports

### Classification Systems

- **QUICK**: Quick Query
- **HTS**: HTS Items (Harmonized Tariff Schedule)
- **SIC**: SIC Codes (1989-2001)
- **SITC**: SITC Codes (Standard International Trade Classification)
- **NAIC**: NAICS Codes (1997-present)
- **EXPERT**: Expert Mode

### Date Selection Types

- **fullYears**: Select entire years (use `years` array)
- **specificDateRange**: Select specific date range (use `startDate` and `endDate` in MM/YYYY format)

### Timeline Aggregation

- **Annual**: Aggregate by calendar year
- **Monthly**: Aggregate by month

### Common Data Metrics

- `CONS_FIR_UNIT_QUANT`: Quantity in first unit of quantity
- `CONS_FIR_VIZ_QUANT`: Quantity in first visa quantity
- `CONS_QUANTITY_2`: Second quantity measure
- `CONS_CUSTOMS_VALUE`: Customs value

### Aggregation Options

- **Aggregate Countries**: Group all countries together
- **Break Out Countries**: Show individual countries
- **Aggregate Commodities**: Group commodities
- **Aggregate Districts**: Group districts
- **Aggregate RPCODE**: Group rate provision codes
- **Aggregate CSC**: Group import programs by CSC

---

## Data Models

### Query Response Structure

```json
{
  "dto": {
    "tables": [
      {
        "column_groups": [
          {
            "columns": [
              {
                "label": "Column Name",
                "dataType": "string"
              }
            ]
          }
        ],
        "row_groups": [
          {
            "rowsNew": [
              {
                "rowEntries": [
                  {"value": "data1"},
                  {"value": "data2"}
                ]
              }
            ]
          }
        ]
      }
    ]
  }
}
```

### Response Data Extraction

The response contains hierarchical column and row structures:
- Column groups organize columns by category
- Row groups contain individual row data
- Each row entry contains a value field with the actual data

---

## Examples

### Basic Python Query

```python
import requests
import json

# Setup
token = '<your-api-token>'
base_url = 'https://datawebws.usitc.gov/dataweb'
headers = {
    'Content-Type': 'application/json; charset=utf-8',
    'Authorization': f'Bearer {token}'
}

# Basic query
query = {
    "reportOptions": {
        "tradeType": "Import",
        "classificationSystem": "HTS"
    },
    "searchOptions": {
        "countries": {"countriesSelectType": "all"},
        "commodities": {"commoditySelectType": "all"},
        "componentSettings": {
            "timeframeSelectType": "fullYears",
            "years": ["2022", "2023"],
            "yearsTimeline": "Annual",
            "dataToReport": ["CONS_FIR_UNIT_QUANT"],
            "scale": "1"
        },
        "MiscGroup": {
            "districts": {
                "aggregation": "Aggregate District",
                "districtGroups": {"userGroups": []},
                "districts": [],
                "districtsExpanded": [{"name": "All Districts", "value": "all"}],
                "districtsSelectType": "all"
            },
            "importPrograms": {"aggregation": None, "importPrograms": [], "programsSelectType": "all"},
            "extImportPrograms": {"aggregation": "Aggregate CSC", "extImportPrograms": [], "extImportProgramsExpanded": [], "programsSelectType": "all"},
            "provisionCodes": {"aggregation": "Aggregate RPCODE", "provisionCodesSelectType": "all", "rateProvisionCodes": [], "rateProvisionCodesExpanded": []}
        }
    },
    "sortingAndDataFormat": {
        "DataSort": {"columnOrder": [], "fullColumnOrder": [], "sortOrder": []},
        "reportCustomizations": {
            "exportCombineTables": False,
            "showAllSubtotal": True,
            "subtotalRecords": "",
            "totalRecords": "20000",
            "exportRawData": False
        }
    }
}

# Make request
response = requests.post(
    f'{base_url}/api/v2/report2/runReport',
    headers=headers,
    json=query,
    verify=False
)

# Parse response
data = response.json()
print(json.dumps(data, indent=2))
```

### Extracting Data from Response

```python
def extract_data(response_json):
    """Extract data from Dataweb API response"""
    
    table = response_json['dto']['tables'][0]
    
    # Extract column names
    columns = []
    for col_group in table['column_groups']:
        if 'columns' in col_group:
            for col in col_group['columns']:
                columns.append(col['label'])
    
    # Extract row data
    data = []
    for row in table['row_groups'][0]['rowsNew']:
        row_data = [entry['value'] for entry in row['rowEntries']]
        data.append(row_data)
    
    return columns, data

# Usage
columns, data = extract_data(response.json())
print(f"Columns: {columns}")
print(f"Data rows: {len(data)}")
for row in data[:5]:
    print(row)
```

---

## API Reference - All Endpoints

# USITC Dataweb API - Complete Documentation

## Overview

This page provides API endpoints that provide public data. Note: some endpoints require an API token, which can be generated/copied from the API page in the Dataweb application, https://dataweb.usitc.com/api-key (requires login). To use your API token with swagger, click on the <strong><font color="#49cc90">AUTHORIZE</font></strong> button on the right and paste in the token.

**Base URL:** `https://datawebws.usitc.gov/dataweb`
**API Version:** v0.0.1

## Authentication

The API uses Bearer token authentication. Include your API token in the Authorization header:

```
Authorization: Bearer <your-api-token>
```

**Important:** API tokens can be generated/copied from the API page in the Dataweb application at https://dataweb.usitc.com/api-key (requires login).

## Common Request/Response Patterns

### Request Headers

```json
{
  "Content-Type": "application/json; charset=utf-8",
  "Authorization": "Bearer <your-api-token>"
}
```

### Response Format

All responses are in JSON format. Successful responses return HTTP 200 with data.

## API Endpoints

### Commodities

#### `POST /api/v2/commodity/validateCommoditySearch`

**Description:** Returns a list of commodities based on comma separated list of search terms for a given commodity system classification level. Supplying a commodity classification system level of null will search all levels.

**Operation ID:** `validateCommoditySearch`

**Request Body:** JSON object

**Responses:**

- **200:** OK

---

#### `POST /api/v2/commodity/validateCommodityNumbersOnly`

**Description:** Returns a list of commodities based on comma separated list of search terms (numbers only) for a given commodity system classification level. Supplying a commodity classification system level of null will search all levels.

**Operation ID:** `validateCommodityNumbersOnly`

**Request Body:** JSON object

**Responses:**

- **200:** OK

---

#### `POST /api/v2/commodity/getAllUserGroupsWithCommodities`

**Description:** Returns a list of the user defined commodities groups along with all the corresponding commodities within the group. Trade type and classification is required.

**Operation ID:** `getAllUserGroupsWithCommodities`

**Request Body:** JSON object

**Responses:**

- **200:** OK

---

#### `POST /api/v2/commodity/getAllSystemGroupsWithCommodities`

**Description:** Returns a list system commodity groups, i.e. ones administered through the dataweb admin app.

**Operation ID:** `getAllSystemGroupsWithCommodities`

**Request Body:** JSON object

**Responses:**

- **200:** OK

---

#### `POST /api/v2/commodity/commodityTree`

**Description:** Returns a list commodity numbers a particular level, classification system and trade type (import/export).

**Operation ID:** `commodityTree`

**Request Body:** JSON object

**Responses:**

- **200:** OK

---

#### `POST /api/v2/commodity/commodityTranslationLookup`

**Description:** Returns a list of translated commodity classification system number i.e. from HTS to SITC.

**Operation ID:** `translateCommodity`

**Request Body:** JSON object

**Responses:**

- **200:** OK

---

#### `POST /api/v2/commodity/commodityDescriptionLookup`

**Description:** Returns a list of all of commodity numbers with descriptions for a commodity classification system.

**Operation ID:** `getDescriptions`

**Request Body:** JSON object

**Responses:**

- **200:** OK

---

#### `GET /api/v2/commodity/getAllTotalUserGroupsWithCommodities`

**Description:** Returns a list of the user defined commodities groups along with all the corresponding commodities within the group.

**Operation ID:** `getAllTotalUserGroupsWithCommodities`

**Responses:**

- **200:** OK

---

### Countries

#### `GET /api/v2/country/getAllUserGroupsWithCountries`

**Description:** Return a list of user defined country groups along with all the corresponding countries and respective country codes in the group.

**Operation ID:** `getAllUserGroupsWithCountries`

**Responses:**

- **200:** OK

---

#### `GET /api/v2/country/getAllSystemGroupsWithCountries`

**Description:** Return a list of default system defined country groups with their corresponding list of countries.

**Operation ID:** `getAllSystemGroupsWithCountries`

**Responses:**

- **200:** OK

---

#### `GET /api/v2/country/getAllCountries`

**Description:** Returns a list of all countries with their respective country codes.

**Operation ID:** `getAllCountries`

**Responses:**

- **200:** OK

---

### Districts

#### `GET /api/v2/district/getAllUserGroupsWithDistricts`

**Description:** Returns as list of user defined district groups along with all the corresponding districts and their respective district in the group.

**Operation ID:** `getAllUserGroupsWithDistricts`

**Responses:**

- **200:** OK

---

#### `GET /api/v2/district/getAllDistricts`

**Description:** Returns a list of all districts with their respective district codes.

**Operation ID:** `getAllDistricts`

**Responses:**

- **200:** OK

---

### Notifications

#### `GET /api/v2/notification/notification-preferences`

**Description:** No description provided

**Operation ID:** `getNotificationPreferences`

**Responses:**

- **200:** OK

---

#### `POST /api/v2/notification/notification-preferences`

**Description:** No description provided

**Operation ID:** `updateNotificationPreferences`

**Request Body:** JSON object

**Responses:**

- **200:** OK

---

### Programs

#### `GET /api/v2/program/programs`

**Description:** No description provided

**Operation ID:** `getAllPrograms`

**Path/Query Parameters:**

- `country` (query, optional)
- `hts8` (query, optional)
- `beginYear` (query, optional)
- `endYear` (query, optional)

**Responses:**

- **200:** OK

---

#### `GET /api/v2/program/programCountryYears`

**Description:** No description provided

**Operation ID:** `getProgramYears`

**Path/Query Parameters:**

- `programId` (query, required)
- `countryCode` (query, required)

**Responses:**

- **200:** OK

---

#### `GET /api/v2/program/programCountries`

**Description:** No description provided

**Operation ID:** `getCountriesForProgram`

**Path/Query Parameters:**

- `programId` (query, required)

**Responses:**

- **200:** OK

---

#### `GET /api/v2/program/getPrograms`

**Description:** No description provided

**Operation ID:** `getProgramDetails`

**Path/Query Parameters:**

- `hts8` (query, required)
- `year` (query, required)
- `countryCode` (query, required)

**Responses:**

- **200:** OK

---

#### `GET /api/v2/program/getProgramsAndHtsNums`

**Description:** No description provided

**Operation ID:** `getProgramsAndHtsNums`

**Path/Query Parameters:**

- `country` (query, required)
- `year` (query, required)

**Responses:**

- **200:** OK

---

#### `GET /api/v2/program/getProgramsAndCountries`

**Description:** No description provided

**Operation ID:** `getProgramsAndCountries`

**Path/Query Parameters:**

- `hts8` (query, required)
- `year` (query, required)

**Responses:**

- **200:** OK

---

### Query Info

#### `POST /api/v2/query/getRPCodesList`

**Description:** Returns a list of all rate provision codes.

**Operation ID:** `getRPCodesList`

**Request Body:** JSON object

**Responses:**

- **200:** OK

---

#### `POST /api/v2/query/getRPCodeGroups`

**Description:** Returns a list of all rate provision code groups.

**Operation ID:** `getRPCodeGroups`

**Request Body:** JSON object

**Responses:**

- **200:** OK

---

#### `POST /api/v2/query/getImportPrograms`

**Description:** Returns a list of all import programs.

**Operation ID:** `getImportPrograms`

**Request Body:** JSON object

**Responses:**

- **200:** OK

---

#### `POST /api/v2/query/getDistrictUserGroupByHash`

**Description:** Returns the list of districts in a user saved district group.

**Operation ID:** `getDistrictUserGroupByHash`

**Request Body:** JSON object

**Responses:**

- **200:** OK

---

#### `POST /api/v2/query/getCountryUserGroupByHash`

**Description:** Returns the list of countries in a user saved country group.

**Operation ID:** `getCountryUserGroupByHash`

**Request Body:** JSON object

**Responses:**

- **200:** OK

---

#### `POST /api/v2/query/getCommodityUserGroupByHash`

**Description:** Returns the list of commodities in a user saved commodities group.

**Operation ID:** `getCommodityUserGroupByHash`

**Request Body:** JSON object

**Responses:**

- **200:** OK

---

#### `GET /api/v2/query/getUnitConversionList`

**Description:** Returns the list of unit conversion objects.

**Operation ID:** `getUnitConversionList`

**Responses:**

- **200:** OK

---

#### `GET /api/v2/query/getGlobalVars`

**Description:** Returns current year, month, and quarter information.

**Operation ID:** `getGlobalVars`

**Responses:**

- **200:** OK

---

### Run Query

#### `POST /api/v2/report2/runReport`

**Description:** Returns import export data based on sent query parameters.

**Operation ID:** `runReport`

**Request Body:** JSON object

**Responses:**

- **200:** OK

---

### Saved Queries

#### `POST /api/v2/savedQuery/getSavedQuery`

**Description:** Returns a user all the parameters of a saved query based on user specific query ID.

**Operation ID:** `getSavedQuery`

**Request Body:** JSON object

**Responses:**

- **200:** OK

---

#### `GET /api/v2/savedQuery/getAllSystemSavedQueries`

**Description:** Returns  list of all system defined saved queries.

**Operation ID:** `getAllSystemSavedQueries`

**Responses:**

- **200:** OK

---

#### `GET /api/v2/savedQuery/getAllSharedQueries`

**Description:** Returns a list of all queries a user has shared.

**Operation ID:** `getAllSharedQueries`

**Responses:**

- **200:** OK

---

#### `GET /api/v2/savedQuery/getAllSavedQueries`

**Description:** Returns a list of all queries a user has saved.

**Operation ID:** `getAllSavedQueries`

**Responses:**

- **200:** OK

---

### System Alerts

#### `GET /api/v2/system-alert`

**Description:** No description provided

**Operation ID:** `getAllSystemAlerts`

**Responses:**

- **200:** OK

---

#### `POST /api/v2/system-alert`

**Description:** No description provided

**Operation ID:** `updateSystemAlert`

**Request Body:** JSON object

**Responses:**

- **200:** OK

---

#### `GET /api/v2/system-alert/alert/{id}`

**Description:** No description provided

**Operation ID:** `getSystemAlert`

**Path/Query Parameters:**

- `id` (path, required)

**Responses:**

- **200:** OK

---

#### `DELETE /api/v2/system-alert/alert/{id}`

**Description:** No description provided

**Operation ID:** `updateSystemAlert_1`

**Path/Query Parameters:**

- `id` (path, required)

**Responses:**

- **200:** OK

---

### Tariffs

#### `POST /api/v2/tariff/tariffSummaryDetails`

**Description:** Returns a list of countries for a given tariff group code.

**Operation ID:** `getTariffSummaryDetails`

**Request Body:** JSON object

**Responses:**

- **200:** OK

---

#### `POST /api/v2/tariff/tariffSummaryCounts`

**Description:** Returns a list of countries for a given tariff group code.

**Operation ID:** `getTariffSummaryCounts`

**Request Body:** JSON object

**Responses:**

- **200:** OK

---

#### `POST /api/v2/tariff/tariffProgramSingle`

**Description:** Returns a list of countries for a given tariff group code.

**Operation ID:** `getTariffProgram`

**Request Body:** JSON object

**Responses:**

- **200:** OK

---

#### `POST /api/v2/tariff/getNaftaUSMCADetails`

**Description:** Returns a list of countries for a given tariff group code.

**Operation ID:** `getNaftaUSMCADetails`

**Request Body:** JSON object

**Responses:**

- **200:** OK

---

#### `POST /api/v2/tariff/futureTariffAgreementSingle`

**Description:** Returns a tariff information for a give country and commodity ID (HTS number).

**Operation ID:** `getDetails`

**Request Body:** JSON object

**Responses:**

- **200:** OK

---

#### `POST /api/v2/tariff/futureTariffAgreementLookup`

**Description:** Returns the detailed data for a single tariff agreement program.

**Operation ID:** `getAgreements`

**Request Body:** JSON object

**Responses:**

- **200:** OK

---

#### `POST /api/v2/tariff/currentTariffLookup`

**Description:** Returns a list of HTS numbers.

**Operation ID:** `currentTariffLookup`

**Request Body:** JSON object

**Responses:**

- **200:** OK

---

#### `GET /api/v2/tariff/tariffProgramsLookup`

**Description:** Returns a list of tariff programs with descriptions.

**Operation ID:** `getTariffPrograms`

**Responses:**

- **200:** OK

---

#### `GET /api/v2/tariff/currentTariffYear`

**Description:** Returns the current year for which the database has tariff information.

**Operation ID:** `currentTariffYear`

**Responses:**

- **200:** OK

---

#### `GET /api/v2/tariff/currentTariffDetails`

**Description:** Returns details about a particular HTS8 number and year.

**Operation ID:** `currentTariffDetails`

**Path/Query Parameters:**

- `year` (query, required)
- `hts8` (query, required)

**Responses:**

- **200:** OK

---

