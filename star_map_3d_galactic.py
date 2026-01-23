"""
Interactive 3D Star Map Visualization
Stars visible from Sol in 3D space
Using HYG vv4.2 stellar database
"""
import numpy as np
import plotly.graph_objects as go
import pandas as pd
import os


DIST_MAX = 750  # in parsecs
MAG_MIN = 5.5  # apparent magnitude
APPARENT_MAG = True  # size by apparent magnitude if True, else absolute magnitude
GLOBE_MAX = 20 # max plot size
GLOBE_MIN = 1.5 # min plot size
CONSTELLATION = None  # show constellations
#  Ref https://astronexus.com/projects/hyg-details

def download_star_data():
    """Load the HYG stellar database"""
    filename = 'hyg_v42.csv'
    
    if os.path.exists(filename):
        # Check if existing file is valid
        try:
            test_df = pd.read_csv(filename, nrows=5)
            if len(test_df) > 0:
                print(f"Using existing {filename}")
                return filename
        except:
            print("Existing file is corrupted")
            os.remove(filename)

def cartesian_coords(distance, ra, dec):
    """
    Convert astronomical coordinates to 3D Cartesian coordinates
    distance: in parsecs
    ra: right ascension in degrees
    dec: declination in degrees
    """
    ra_rad = np.radians(ra)
    dec_rad = np.radians(dec)
    
    x = distance * np.cos(dec_rad) * np.cos(ra_rad)
    y = distance * np.cos(dec_rad) * np.sin(ra_rad)
    z = distance * np.sin(dec_rad)
    
    return x, y, z

def get_star_color(bv_color):
    """
    Convert B-V color index to approximate RGB color
    B-V ranges from about -0.4 (blue) to +2.0 (red)
    """
    if pd.isna(bv_color):
        return 'white'
    
    # Clamp values
    bv = max(-0.4, min(2.0, bv_color))
    
    # Simple color mapping
    if bv < -0.2:
        return 'lightskyblue'
    elif bv < 0:
        return 'lightsteelblue'
    elif bv < 0.3:
        return 'aliceblue'
    elif bv < 0.6:
        return 'ivory'
    elif bv < 1.0:
        return 'cornsilk'
    elif bv < 1.5:
        return 'navajowhite'
    elif bv < 1.8:
        return 'lightsalmon'
    else:
        return 'darksalmon'

def create_star_map(DIST_MAX, MAG_MIN):
    """
    Create interactive 3D star map with constellation selector
    DIST_MAX: maximum distance in parsecs (default 100 pc ≈ 326 light-years)
    DIST_MIN: minimum distance in parsecs (default 0 pc - Sol) <-- if used
    MAG_MIN: faintest apparent magnitude to show (default 6.5 - visible to naked eye)
    """
    # Download and load data
    filename = download_star_data()
    print("\nLoading star data...")
    stars = pd.read_csv(filename)
    
    print(f"Total stars in database: {len(stars)}")

    # Import galactic plane function
    filename_plane = 'galactic_plane.csv'
    galactic_plane = pd.read_csv(filename_plane)

    # Filter stars: visible from Earth and within distance limit
    # (Remove stars with no distance data)
    stars = stars[stars['dist'].notna()]
    stars = stars[stars['dist'] > 0]
    
    # Filter by distance and magnitude
    stars = stars[stars['dist'] <= DIST_MAX]
    stars = stars[stars['mag'] <= MAG_MIN]
    
    # Get list of unique constellations
    constellations = sorted(stars['con'].dropna().unique().tolist())
    print(f"Found {len(constellations)} constellations")
    
    # Create sphere mesh for boundary
    u = np.linspace(0, 2 * np.pi, 50)
    v = np.linspace(0, np.pi, 50)
    radius = 1.33*DIST_MAX # Sphere radius

    x_sphere = radius * np.outer(np.cos(u), np.sin(v))
    y_sphere = radius * np.outer(np.sin(u), np.sin(v))
    z_sphere = radius * np.outer(np.ones(np.size(u)), np.cos(v))

    x_plane, y_plane, z_plane = cartesian_coords(
        radius,
        galactic_plane['ra'].values * 15,
        galactic_plane['dec'].values
    )

    # Initialize figure with empty data
    fig = go.Figure()
    
    # Add sphere boundary (always visible)
    fig.add_trace(go.Surface(
        x=x_sphere, y=y_sphere, z=z_sphere,
        opacity=0.075,
        showscale=False,
        colorscale=[[0, 'aliceblue'], [1, 'aliceblue']],
        hoverinfo='skip',
        name='Boundary'
    ))
    
    # Add Sol at origin
    fig.add_trace(go.Scatter3d(
        x=[0], y=[0], z=[0],
        mode='markers',
        marker=dict(
            size=5,
            color='yellow',
            symbol='circle',
            line=dict(color='orange', width=2)
        ),
        text='<b>Sol</b>',
        hoverinfo='text',
        name='Sol'
    ))
    
    # Add extra data points
    fig.add_trace(go.Scatter3d(
        x=x_plane,
        y=y_plane,
        z=z_plane,
        mode='lines+markers',
        marker=dict(
            size=1,
            color='gray',
            opacity=0.75
        ),
        name='Galactic Plane',
        hoverinfo='skip'
    ))

    fig.add_trace(go.Mesh3d(
        x=x_plane,
        y=y_plane,
        z=z_plane,
        opacity=0.4,
        name='Surface'
    ))

    # Create traces for each constellation + "All"
    constellation_options = ['All'] + constellations
    
    for constellation in constellation_options:
        # Filter data for this constellation
        if constellation == 'All':
            stars_con = stars
        else:
            stars_con = stars[stars['con'] == constellation]
        
        if len(stars_con) == 0:
            continue
            
        # Convert to Cartesian coordinates
        x, y, z = cartesian_coords(stars_con['dist'].values, 
                                   stars_con['ra'].values * 15,  # convert RA to degrees
                                   stars_con['dec'].values)
        
        # Prepare hover text
        hover_text = []
        for _, star in stars_con.iterrows():
            name = star['proper'] if pd.notna(star['proper']) else f"HIP {star['hip']}" if pd.notna(star['hip']) else "Unknown"
            text = f"<b>{name}</b><br>"
            text += f"Constellation: {star['con']}<br>" if pd.notna(star['con']) else ""
            text += f"Distance: {star['dist']:.2f} pc ({star['dist']*3.26:.1f} ly)<br>"
            text += f"Apparent Magnitude: {star['mag']:.2f}<br>"
            text += f"Absolute Magnitude: {star['absmag']:.2f}<br>"
            text += f"Spectral Type: {star['spect'] if pd.notna(star['spect']) else 'Unknown'}"
            hover_text.append(text)
        
        # # Size stars by apparent magnitude
        mag_min = stars_con['mag'].min()
        mag_max = stars_con['mag'].max()

        # Size stars by magnitude (apparent or absolute) using natural log
        if (APPARENT_MAG):
            sizes = GLOBE_MAX * np.exp(-0.26 * (stars_con['mag'].values + 2))
        else:
            sizes = GLOBE_MAX * np.exp(-0.26 * (stars_con['absmag'].values + 8) * .6)
        sizes = np.clip(sizes, GLOBE_MIN, GLOBE_MAX)
        
        # Color stars by B-V color index
        colors = [get_star_color(bv) for bv in stars_con['ci'].values]
        
        # Add 3D stars trace
        visible = (constellation == 'All' and CONSTELLATION is None) or (constellation == CONSTELLATION)
        fig.add_trace(go.Scatter3d(
            x=x, y=y, z=z,
            mode='markers',
            marker=dict(
                size=sizes,
                color=colors,
                opacity=0.8,
                line=dict(width=0)
            ),
            text=hover_text,
            hoverinfo='text',
            name=f'Stars - {constellation}',
            visible=visible
        ))
        
        # Project stars onto sphere
        distances = np.sqrt(x**2 + y**2 + z**2)
        x_projected = (x / distances) * radius
        y_projected = (y / distances) * radius
        z_projected = (z / distances) * radius
        
        # Add projected stars trace
        fig.add_trace(go.Scatter3d(
            x=x_projected, y=y_projected, z=z_projected,
            mode='markers',
            marker=dict(
                size=sizes * 0.7,
                color='lightgray',
                opacity=0.5,
                line=dict(width=0)
            ),
            text=hover_text,
            hoverinfo='text',
            name=f'Projected - {constellation}',
            visible=visible
        ))
    
    # Create dropdown menu buttons
    buttons = []
    for i, constellation in enumerate(constellation_options):
        # Each constellation has 2 traces (3D + projected) starting after sphere and Sol (2 traces)
        visible_array = [True, True]  # Sphere and Sol always visible
        
        for j in range(len(constellation_options)):
            if j == i:
                visible_array.extend([True, True])  # Show both 3D and projected
            else:
                visible_array.extend([False, False])  # Hide both traces
        
        button = dict(
            label=constellation,
            method='update',
            args=[
                {'visible': visible_array},
                {'title.text': f'Interactive 3D Star Map from Sol<br><sub>Showing {len(stars)} stars brighter than {MAG_MIN} apparent magnitude<br>Within {DIST_MAX} parsecs ({DIST_MAX*3.26:.0f} light-years) of Sol<br>Constellation: {CONSTELLATION if CONSTELLATION else "All stars"}</sub>'}
            ]
        )
        buttons.append(button)
    
    # Update layout with dropdown menu
    fig.update_layout(
        updatemenus=[
            dict(
                buttons=buttons,
                direction="down",
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.01,
                xanchor="left",
                y=0.99,
                yanchor="top",
                bgcolor="rgba(255, 255, 255, 0.8)",
                font=dict(color="black")
            )
        ],
        title=dict(
            text=f'Interactive 3D Star Map from Sol<br><sub>Showing {len(stars)} stars brighter than {MAG_MIN} apparent magnitude<br>Within {DIST_MAX} parsecs ({DIST_MAX*3.26:.0f} light-years) of Sol<br>Constellation: {CONSTELLATION if CONSTELLATION else "All stars"}</sub>',
            x=0.5,
            xanchor='center'
        ),
        scene=dict(
            xaxis=dict(title='X (parsecs)', backgroundcolor="black", gridcolor="gray"),
            yaxis=dict(title='Y (parsecs)', backgroundcolor="black", gridcolor="gray"),
            zaxis=dict(title='Z (parsecs)', backgroundcolor="black", gridcolor="gray"),
            bgcolor="black",
            aspectmode='cube',
        ),
        paper_bgcolor="black",
        plot_bgcolor="black",
        font=dict(color="white"),
        showlegend=True,
        height=1200
    )
    
    return fig

if __name__ == "__main__":
    print("="*70)
    print("3D STAR MAP VISUALIZATION - Real HYG Database")
    print("="*70)
    print()
    
    try:
        # Create the visualization
        print("Creating 3D star map...")
        fig = create_star_map(DIST_MAX, MAG_MIN)
        
        print()
        print("="*70)
        print("Opening interactive visualization in browser...")
        print("="*70)
        fig.show()
        
        # Save to HTML file
        output_file = "star_map_3d.html"
        fig.write_html(output_file)
        print(f"\n✓ Saved to {output_file}")
        print("  You can open this HTML file in any browser anytime!")
        
    except FileNotFoundError as e:
        print(f"\n{e}")
        print("\nTIP: If manual download is needed, you can also use the")
        print("     'star_map_demo.py' script which works without downloading!")