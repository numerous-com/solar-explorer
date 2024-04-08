import marimo

__generated_with = "0.3.10"
app = marimo.App()


@app.cell
def __():
    # Import the necessary libraries
    import marimo as mo
    import plotly.graph_objects as go
    import pandas as pd


    # Import the necessary functions from the solar_calc.py file
    from solar_calc import calc_solar_output, get_location_file, locations_files
    return calc_solar_output, get_location_file, go, locations_files, mo, pd


@app.cell
def __():
    # Define the degree sign
    degree_sign = '\u00B0'
    return degree_sign,


@app.cell
def __(mo):
    # Add a title to the app using markdown title
    mo.md("#Solar Designer")
    return


@app.cell
def __(locations_files, mo):
    # Create a dropdown to select the location
    location=mo.ui.dropdown(
               options=locations_files,
            value=list(locations_files.keys())[0],
          label='Location' 
        )
    location
    return location,


@app.cell
def __(mo):
    # Add a markdown cell to provide information about the app
    mo.md("Configure one or more solar plants and add them to the calculation. You can add multiple plants if you for instance have various roof sections with differing tilt and or orientation.")
    return


@app.cell
def __(degree_sign, location, mo, on_change):
    # Make this cell dependent on the location dropdown
    location
    # Create a form to add solar plants
    form = mo.md('''
        **Add Solar Plant**

        {azimuth}
        {tilt}    
        {peak_power}
        {num_panels}

    ''').batch(
        azimuth=mo.ui.slider(label=f"Compass Direction ({degree_sign})", start=0, stop=355, step=5, value=180),
        tilt=mo.ui.slider(label=f"Tilt Angle ({degree_sign})", start=0, stop=90, step=5, value=30),
        peak_power=mo.ui.slider(label="Peak power pr. Panel (W)", start=25, stop=400, step=5, value=330),
        num_panels=mo.ui.number(label="Number of panels", start=0, stop=1000, step=1, value=20)
        ).form(show_clear_button=False, bordered=False, submit_button_label="Add", on_change=on_change)
    form
    return form,


@app.cell
def __(clear_plants, degree_sign, form, mo, table_systems):
    # Make this cell dependent on the form cell
    form
    # Make this cell dependent on the clear button
    clear_plants

    # Create a table to display the solar plants
    table_data = table_systems.copy()

    # Add a totals row to the table
    totals_row = {}

    totals_row[f'Compass Orientation - South = 180 ({degree_sign})'] = "Total:"
    totals_row[f"Tilt Angle ({degree_sign})"] = ""
    totals_row[f"Panel Peak Power (W)"] = ""
    totals_row[f"Number of Panels"] = sum([system["Number of Panels"] for system in table_systems])
    totals_row["Combined Peak Power (kW)"] = round(sum([system["Combined Peak Power (kW)"] for system in table_systems]),1)
    totals_row["Yearly Prod (MWh)"] = round(sum([system["Yearly Prod (MWh)"] for system in table_systems]),2)

    table_data.append(totals_row)

    # Create the table
    table = mo.ui.table(
      data=table_data,
      label='Solar Plants',
    selection=None

    )
    table
    return table, table_data, totals_row


@app.cell
def __(mo, monthly_prod, table_systems, total_series):
    # Create a method to clear the solar plants
    def clear(event):
        table_systems.clear()
        total_series['total'] = None

        monthly_prod.clear()

    # Create a clear button
    clear_plants = mo.ui.button(
        label='Clear',
        kind='danger',
        on_click=clear
    )
    clear_plants
    return clear, clear_plants


@app.cell
def __():
    # Define the variables to store data accessed by multiple cells
    table_systems = []
    total_series = {'total': None}
    monthly_prod = []
    return monthly_prod, table_systems, total_series


@app.cell
def __(
    calc_solar_output,
    degree_sign,
    location,
    monthly_prod,
    table_systems,
    total_series,
):
    # Create a method to calculate the solar output for the added solar plant
    def on_change(data):

        df = calc_solar_output(location.value, data['tilt'], data['azimuth'], data['peak_power'], data['num_panels'])

        row = {f'Compass Orientation - South = 180 ({degree_sign})': data['azimuth'],
               f'Tilt Angle ({degree_sign})': data['tilt'],
               'Panel Peak Power (W)': data['peak_power'],
               'Number of Panels': data['num_panels'],
                'Combined Peak Power (kW)': data['peak_power']*data['num_panels']/1000,
               'Yearly Prod (MWh)': round(df.sum()/1e6,2)}

        monthly_prod.append((df/1e6).resample('ME').sum())


        if total_series['total'] is None:
            total_series['total'] = df.copy()
        else:
            total_series['total'] += df

        table_systems.append(row)
    return on_change,


@app.cell
def __(clear_plants, go, mo, monthly_prod, table):
    # Make this cell dependent on the clear button and the table
    table
    clear_plants

    # Create a bar chart using Plotly Graph Objects
    fig = go.Figure()
    for i, mp in enumerate(monthly_prod):
        fig.add_trace(
            go.Bar(x=mp.index.month, y=mp, name=f"Plant {i}")
        )

    # Customize the layout
    fig.update_layout(title='Monthly Power Production',
                      xaxis_title='Month',
                      yaxis_title='Energy Production (MWh)',
                      template='plotly_white')

    fig.update_layout(barmode='stack')
    fig.update_layout(
        xaxis = dict(
            tickmode = 'linear',
            tick0 = 1,
            dtick = 1
        )
    )


    # Show the figure in marimo
    mo.ui.plotly(fig)
    return fig, i, mp


@app.cell
def __(mo):
    # Add a markdown cell to provide information selecting the best and worst production days
    mo.md("In the table below you can see the best and worst production days for each month. Select one or more rows to compare the hour-by-hour production between the days in different months.")
    return


@app.cell
def __(mo, pd, table, total_series):
    table


    # Best Day, Worst Day, Average
    # Structure to store the best and worst production days' hourly data
    monthly_best_worst = {}
    if total_series['total'] is not None:
        for group_name, group_df in total_series['total'].groupby(pd.Grouper(freq='ME')):
            daily_sum = group_df.resample('D').sum()


            # Finding the day with the highest production
            best_day = daily_sum.idxmax()
            best_day_data = total_series['total'].loc[best_day.strftime("%Y-%m-%d")]

            # Finding the day with the lowest production
            worst_day = daily_sum.idxmin()
            worst_day_data = total_series['total'].loc[worst_day.strftime("%Y-%m-%d")]

            # Store in the structure, including only the 'power' values for each hour
            monthly_best_worst[group_name.strftime("%m")] = {
                'best_day': {
                    'date': best_day.strftime("%m-%d"),
                    'power_values': best_day_data.tolist()
                },
                'worst_day': {
                    'date': worst_day.strftime("%m-%d"),
                    'power_values': worst_day_data.tolist()
                }
            }

    selected_best_worst = {'selected': []}

    def on_change_best_worst(data):
        selected_best_worst['selected'] = data

    # Create a table to display the best and worst days pr month
    table_b_and_w_days = mo.ui.table(
      data=[{
          'Month': k,
          'Best': str(v['best_day']['date']),
          'Max Energy (kWh)': round(sum(v['best_day']['power_values'])/1000,1),
          'Worst': str(v['worst_day']['date']),
          'Min Energy (kWh)': round(sum(v['worst_day']['power_values'])/1000,1),

            } for k, v in monthly_best_worst.items()],
      label='Best and Worst Days',
        page_size=12,
        on_change=on_change_best_worst
    )

    table_b_and_w_days
    return (
        best_day,
        best_day_data,
        daily_sum,
        group_df,
        group_name,
        monthly_best_worst,
        on_change_best_worst,
        selected_best_worst,
        table_b_and_w_days,
        worst_day,
        worst_day_data,
    )


@app.cell
def __(
    go,
    mo,
    monthly_best_worst,
    selected_best_worst,
    table_b_and_w_days,
):
    table_b_and_w_days

    # Create a figure to display the power production during the best and worst days of the selected months
    fig_best_owth = go.Figure()
    for bw in selected_best_worst['selected']:

        selected_month = monthly_best_worst[bw['Month']]

        fig_best_owth.add_trace(
            go.Scatter(x=[i for i in range(24)], y=selected_month['best_day']['power_values'], name=f"Best Day of {bw['Month']}"))
        fig_best_owth.add_trace(
            go.Scatter(x=[i for i in range(24)], y=selected_month['worst_day']['power_values'], name=f"Worst Day of {bw['Month']}"))



    # Customize the layout
    fig_best_owth.update_layout(title='Power Production the During Day',
                      xaxis_title='Hour of Day',
                      yaxis_title='Power Production (W)',
                      template='plotly_white')
    fig_best_owth.update_layout(
        xaxis = dict(
            tickmode = 'linear',
            tick0 = 1,
            dtick =1
        )
    )

    # Show the figure
    mo.ui.plotly(fig_best_owth)
    return bw, fig_best_owth, selected_month


@app.cell
def __(mo):
    # Add a markdown cell to provide a disclaimer
    disclaimer=mo.accordion({"Disclaimer for Solar Designer": """The calculations and data presented by this app are for informational purposes only. Numerous ApS is not liable for the accuracy, reliability, or completeness of any information provided, or for any decisions made based on such information. Users should verify all data and use their own judgment before making any decisions based on the app's outputs."""})
    disclaimer
    return disclaimer,


if __name__ == "__main__":
    app.run()
