import pvlib
import pandas as pd
import datetime
from pathlib import Path

# Define the location and weather data
# Climate data can be downloaded via https://www.equaonline.com/ice4user/new_index.html

# Create location files dictionary by listing epw files in cwd
locations_files = {f.name.split(".")[0]: f for f in Path('./epw').iterdir() if f.suffix == '.epw'}

# Check if the location files dictionary is empty and raise an error if it is

if not locations_files:
    raise FileNotFoundError("No .epw climate data files found in the 'epw' directory. Please download one or more .epw files from https://www.equaonline.com/ice4user/new_index.html and place them in the 'epw' directory. Then please retry.")

def get_location_file(epw_file_path):
    
    # Load weather data from EPW file
    weather_data = pvlib.iotools.read_epw(epw_file_path)
    
    df_weather = weather_data[0]

    df_weather['datetime'] = [datetime.datetime(2023, 1, 1, 0)  + datetime.timedelta(hours=i) for i in range(len(df_weather))]
    df_weather.set_index('datetime', inplace=True)
    meta = weather_data[1]

    # Specify your location latitude and longitude
    latitude = meta['latitude']
    longitude = meta['longitude']
    altitude = meta['altitude']
    albedo = 0.2 # 0.2 is a typical value for ground reflectance
    tz = meta['TZ']  # Timezone, adjust to match your location's timezone

    # Create a location object
    location = pvlib.location.Location(latitude, longitude, altitude=altitude, tz=tz)

    # Free memory
    del weather_data

    return location, df_weather, tz, albedo

def calc_solar_output(epw_file_path, tilt, azimuth, module_peak_power, num_modules):
    # Please see documentation for pvlib library for more information at https://pvlib-python.readthedocs.io/en/stable/


    # Load weather data from EPW file
    location, df_weather, tz, albedo = get_location_file(epw_file_path)

    # System specifications
    system = {
        'surface_tilt': tilt,  # Tilt angle of the panels, adjust to your setup
        'surface_azimuth': azimuth,  # Azimuth angle (180 is south), adjust accordingly
        'albedo': albedo,  # Ground reflectance, typical value is 0.2
        'module_parameters': {
            'pdc0': module_peak_power * num_modules,  # Module power at STC in watts
            'gamma_pdc': -0.004  # Temperature coefficient
        },
        'inverter_parameters': {
            'pdc0': module_peak_power * num_modules,  # Inverter DC input limit
            'eta_inv_nom': 0.8,  # Nominal inverter efficiency
        },
        'modules_per_string': 10,  # Number of modules per string
        'strings_per_inverter': 2,  # Number of strings per inverter
    }

    # Calculate solar position
    solpos = location.get_solarposition(df_weather.index)

    # Calculate POA (plane of array) irradiance
    poa_irradiance = pvlib.irradiance.get_total_irradiance(
        system['surface_tilt'],
        system['surface_azimuth'],
        solpos['apparent_zenith'],
        solpos['azimuth'],
        df_weather['dni'],
        df_weather['ghi'],
        df_weather['dhi'],
        albedo=system['albedo']
    )

    # Prepare temperature model
    temperature_model = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_polymer']

    # Calculate cell temperature
    cell_temperature = pvlib.temperature.sapm_cell(
        poa_irradiance['poa_global'],
        df_weather['temp_air'],
        df_weather['wind_speed'],
        **temperature_model
    )

    # Simulate system performance
    system_performance = pvlib.pvsystem.pvwatts_dc(
        poa_irradiance['poa_global'],
        cell_temperature,
        **system['module_parameters']
    )

    # Calculate AC power using a simple inverter model
    ac_power = system_performance * system['inverter_parameters']['eta_inv_nom'] 

    # Save the results in a new column to get the datetime index on the ac_power
    df_weather['ac_power'] = ac_power
    
    # We only need the ac_power column
    out = df_weather['ac_power'].copy()

    # Free memory
    del df_weather

    return out


