
# MeteoSwiss Forecast Archive

Automated collection and archiving of MeteoSwiss weather forecasts for Vilters, Switzerland.

This repository supports research on photovoltaic (PV) feed-in forecasting and weather-related forecast errors.

## Data Source

- Provider: Federal Office of Meteorology and Climatology MeteoSwiss
- Dataset: Local Forecast Data (E4)
- Location: Vilters, Switzerland
- Point ID: 732400
- Forecast resolution: Hourly

Source documentation:
https://opendatadocs.meteoswiss.ch/e-forecast-data/e4-local-forecast-data

## Weather Parameters

- nprolohs: Low cloud cover
- gre000h0: Global solar radiation
- sre000h0: Sunshine duration
- ods000h0: Diffuse solar radiation
- tre200h0: Air temperature

## Archive

Forecast runs are stored as compressed CSV files (.csv.gz).

Each file contains weather predictions, forecast run timestamps, retrieval timestamps and location metadata.

## Data Privacy

This repository contains publicly available weather forecasts only.
No confidential ASGAL measurement data or API credentials are included.
