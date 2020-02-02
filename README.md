# ReaperAudicaTools
These are python scripts to help author Audica maps with REAPER

All these tools require python 3, and python must be actived in REAPER's Reascript settings.

These tools also use the project RPP for various stuff, so you will have to use them on a saved project, they will not work properly if the project never has been saved. In the case of audica_maker.py, you will want a recent save.

# audica_maker.py
This will make an audica file. Assumes you are using the template rpp. If you want to use your own template, for now you can edit the track names in the script. I may add a way to edit this in the GUI in the future.

This script requires ogg2mogg.exe.

# cues_export.py
This script will ask you which difficulty to export and then will write a cues file ready for Audica or NotReaper. Supports all 4 difficulties and the "community" difficulty.

# cues_import.py
This script will ask you which difficulty you want to import a cues file into.
