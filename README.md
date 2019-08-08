# Welcome to the Big Red Ball PiScope!

The goal of this project is to replace jScope for looking at BRB plasma data.  This is obviously a work in progress,
but is definitely usable!

## Screenshots
![Main Window Gif](/source/images/piscope_animation.gif)*PiScope in Action looking at PCX Data*

A simple demonstration of the PiScope app looking at data from the Plasma Couette Experiment.

![Main Window](/source/images/main_window.png)*The main window for BRB PiScope.*

The main window is set up with rows and columns.  Currently, I do not allow a different number of rows in each column
which is a feature of jScope.  Under File, you will find everything you need regarding opening, editing, and saving
configuration files.  Under Options, you will find Auto Update, Share X-Axis, and Edit Downsampling.


- Auto Update
    - This is for auto updating the shot number when the specified MDSplus Event is caught.  This feature will only
    work if you are on the WiPPL private network hosted by the server skywalker.
- Share X-Axis
    - This will toggle if the different axes will share the same x-axis.  A zoom or reset of home is required for the
    axes to update with the shared x-axis.
- Edit Downsampling
    - A built-in feature of jScope and BRB PiScope is not all of the data is plotted at once.  It is decimated for
    speed of plotting because we have a lot of data!  However, you can change the number of points displayed for each
    signal by clicking this option and changing the number in the dialog box.


![New Configuration Window](/source/images/new_configuration.png)*New configuration dialog box
accessed by clicking on File -> New Configuration*

You can create a new configuration by clicking File -> New Configuration.  Here, you can edit these attributes:

- Server Address
    - Address for the MDSplus server
- MDSplus Event Name
    - Name for the MDSplus event you want to catch for auto-updating.  This will only work inside the WiPAL private
    network.
- For each column (up to 6), you can specify the number of plots (up to 6).

![Edit Global Configuration Window](/source/images/edit_global_configuration.png)*Edit global configuration dialog box
accessed by clicking on Edit -> Edit Global Settings

If you want to change the tree name or server address, you can change them by clicking on Edit -> Edit Global Settings
to change them.

![Edit Configuration Window](/source/images/edit_configuration.png)*Edit configuration dialog box
accessed by clicking on Edit -> Edit Configuration

Here you have access to changing the following attributes for a given plot/axis:

- X Label
- Y Label
- X Axis Limits (or allow matplotlib to decide)
- Y Axis Limits (or allow matplotlib to decide)
- Signal Attributes
    - Signal Name
    - X axis data location in wipal tree
    - Y axis data location in wipal tree
    - Color (by using the Select a Color Dialog Button)

Changes do not take affect unless you apply them and exit the dialog with OK.

![Picking a Color for a Signal](/source/images/pick_color_edit_configuration.png)*Inside the edit
configuration dialog box, you can pick a color for each plotted signal.*

You can pick any color you can imagine for your signals.  In the custom colors, you will see the 10 default colors
for matplotlib versions > 2.0.  The color is stored as a hex value which is sort of problematic for users that want to
pick their colors while writing a configuration file by hand.

Note: You do not need to specify a color in the config file.  One will be picked automatically if it is not there.

![Edit Downsampling Number of Points](/source/images/edit_downsampling.png)

The default number of points to be displayed per signal is 1000.  This can be changed by going to Options ->
Edit Downsampling and entering a new value and clicking OK.  This is not stored in a configuration file at this time.
