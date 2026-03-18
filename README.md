## Interactive 3D Star Map
Plots the local stellar neighborhood based on distance and apparent magnitude from the sun using Plotly for visualation.

![Screenshot](<Screenshot 2026-02-28 205245.png>)

### Details
- Uses star data from the [HYG 4.2 database](https://astronexus.com/downloads/catalogs/hygdata_v42.csv.gz), available from astronexus.com.
- Converts right ascension (ra), declination (dec), and estimated distance (dis in parsecs) into Cartesian coordinates (X, Y, Z).
- Plot variables include:
  - DIST_MAX      - maximum distance from the sun in parsecs
  - MAG_MIN       - minimum magnitude i.e. brightness of the star in the sky (defaults to apparent magnitude)
  - GLOBE_MAX     - Plotted size of the brightest star*
  - GLOBE_MIN     - Plotted size of the dimmest star*
  - CONSTELLATION - Optionally can plot stars based on constellation
    *_Plotted size variation follows a log scale_
- Each star's plot color is based on its approximate B-V color.
- Optionally plots the galactic plane and orientation to the galactic center.

### Future Options
- [ ] Plot stars' apparent magnitudes using a new reference star:
  - With each star's cartesian coordinates, the distance of the star to any reference point can be calculated
  - Then taking each star's absolute magnitude, apparent magnitude, and distance from sol, the star's apparent magnitude at the new reference point can be calculated
- [ ] Augment or replace the HYG stellar catalog with some subset of the Gaia catalog (how large of a set depends on my next computer)
