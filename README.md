# timestampToVideo

This script was made hand to hand with Gemini AI.

The objective of this script is to add and old-video look-alike timestamp to mp4 videos. The context is that my video recorder (an old sony one) saves .mp4 and .xml files separately, and the official software to put the timestamp and download them is no longer available.

To use it, load all the .mp4 files and .xml files to the inputs directory. The .xml should be named {respectiveVideoName}M01.XML, that format was chosen because it is the default format by the Sony camera.

The script will go through the /inputs and save the edited video in the /outputs directory.