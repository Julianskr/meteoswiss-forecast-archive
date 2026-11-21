# MeteoSwiss Forecast Archive

Automated collection and archiving of MeteoSwiss weather forecasts for **Vilters, Switzerland**.

This repository supports a Master's thesis.

## 1. Data Source

- **Provider:** Federal Office of Meteorology and Climatology MeteoSwiss
- **Dataset:** Local Forecast Data (E4)
- **Location:** Vilters, Switzerland
- **Point ID:** `732400`
- **Point Type ID:** `2` (postal-code forecast location)
- **Forecast resolution:** Hourly
- **Format:** Compressed CSV (`.csv.gz`)

Official documentation: [MeteoSwiss Local Forecast Data](https://opendatadocs.meteoswiss.ch/e-forecast-data/e4-local-forecast-data)

## 2. Collected Weather Parameters

| Parameter | Description |
|---|---|
| `nprolohs` | Low cloud cover |
| `gre000h0` | Global solar radiation |
| `sre000h0` | Sunshine duration |
| `ods000h0` | Diffuse solar radiation |
| `tre200h0` | Air temperature |
| `jww003i0` | Weather-type code, including fog and low stratus |

The weather-type parameter is particularly relevant for investigating fog (*Nebel*) and low stratus (*Hochnebel*).

**Note:** Weather-type codes represent predicted conditions, not actual meteorological observations.

## 3. Automated Collection

The collector is implemented in Python (`collect_meteoswiss.py`).

GitHub Actions automatically runs the collector every hour. The script:

1. Retrieves available forecast runs from the MeteoSwiss STAC catalogue.
2. Identifies runs containing all required weather parameters.
3. Downloads the corresponding forecast data.
4. Extracts the records for Vilters.
5. Combines the weather parameters by forecast validity timestamp.
6. Saves each new forecast run as a compressed CSV file.

Previously archived files are skipped to prevent accidental overwriting.

The collection can also be triggered manually using GitHub Actions.

## 4. Archive Structure

Forecasts are stored according to their run timestamps:

`archive/YYYY/MM/YYYYMMDDHHMM_vilters.csv.gz`

Each archived file contains:

- `valid_at_utc`: Forecast validity timestamp
- Weather parameters: Predicted meteorological conditions
- `run_at_utc`: Nominal forecast run timestamp
- `retrieved_at_utc`: Timestamp when the file was collected
- `point_id` and `point_type_id`: Location identifiers
- `source`: Data provider

### Archive Version Note

The weather-type parameter `jww003i0` was added on **21 November 2026**.

Earlier archived forecasts contain five weather parameters. Newly collected forecast runs contain all six.

Existing archives are preserved without modification.

## 5. Research Considerations

These data support research into:

- Day-ahead and intraday PV feed-in forecasting
- Forecast accuracy under different weather conditions
- Fog and low-stratus prediction
- Rapid changes in solar radiation and cloud cover

Forecast runs must be evaluated chronologically. Predictions should only be used when they would have been available at the relevant forecast issuance time.

The nominal forecast run timestamp is not necessarily identical to the actual publication or availability time.

## 6. Data Privacy and Attribution

This repository contains **publicly available MeteoSwiss weather forecast data only**.

It does not contain confidential measurement data, electricity consumption data or proprietary datasets.

**Data source:** Federal Office of Meteorology and Climatology MeteoSwiss.

## 7. Project Status

The collection is operational and configured to run automatically through GitHub Actions.

The archive is intended to grow over time and provide a reproducible historical record of meteorological forecasts.
