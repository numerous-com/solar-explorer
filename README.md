# Solar Explorer App

## Description

The Solar Plant Explorer is a tool designed to facilitate the investigation and optimization of various solar plant configurations. Utilizing the power of pvlib, it enables users to predict the annual energy output based on different system setups, including panel orientation, tilt, and location. This project integrates with Marimo for an interactive application experience, allowing for dynamic configuration and visualization of solar energy production.

Feel free to clone the code or visit https://www.numerous.com/app/public/b9bb6d9ab9414297a4603355fb020f4e to use the directly from Numerous Public gallery.

## Features

- Load and process weather data from EPW files to simulate climate conditions.
- Calculate solar output considering specific plant configurations, including tilt, azimuth, and number of modules.
- Visualize monthly energy production and identify best and worst production days with detailed hour-by-hour analysis.
- Interactive web application powered by Marimo for an enhanced user experience.

## Getting Started

### Prerequisites

- Python 3.11
- One or more .epw climate files located in the project directory. Climate files can be downloaded via https://www.equaonline.com/ice4user/new_index.html.

### Installation

1. Clone the repository:
```shell
git clone https://github.com/numerous-team/solar-designer.git
```

2. Install the required Python libraries:
```shell
pip install -r requirements.txt
```

3. Run the app in development mode:
```shell
marimo edit app.py
```

### Deploying and Sharing
The Numerous package is a tool that can help you deploy Python applications easily. Before you can initialize a project with Numerous, you first need to install the Numerous CLI (Command Line Interface) tool:

```shell
pip install numerous
```

Then run the init command and follow the wizard. After you have initialized the app you can push it to Numerous and deploy it using:

```shell
numerous init
numerous push
```

When you have pushed the app you will get a shareable link which you can use to view the app in your browser.

### Usage
Start by selecting a location from the dropdown menu to load the corresponding climate data.
Configure one or more solar plants by specifying the compass direction, tilt angle, peak power per panel, and the number of panels.
Add the configured plants to the calculation to see the combined annual energy production.
Explore the monthly energy production and detailed analysis of the best and worst production days.

## Contributing
Contributions are welcome! Please feel free to submit pull requests or open issues to propose features or report bugs.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer
The calculations and data presented by this app are for informational purposes only. Users should verify all data and use their own judgment before making any decisions based on the app's outputs.

## Credits
Developed using the pvlib library for solar energy system simulation and marimo for interactive web applications.