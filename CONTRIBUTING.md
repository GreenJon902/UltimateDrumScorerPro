# Contributing to UDSP
Hi there! I doubt anyone will but if you want to contribute then great. Please keep the codebase nice. Apart from that here are some notes on the internals and the general structure of the project.

Please put anything that should be accessible in a \_\_all\_\_.

# Notes on Internals
### Important naming stuff
Item - part of a page (e.g. score section, text)  
Component - part of an item (e.g. a score section has bars and note heads which are separate)  
Score section - Actual drum notation  
Score section section - A point in time for a score section (all the beats that are played at the same time)  
Bar - A full line between score section sections  
Bar - Depending on the context, bar can also mean everything that goes into rythem (bars, half bars, slanted bars, dots) at the same time  
Half bar - The smaller bar that exists when note lengths aren't equal. Can be before or after  
Slanted bar - The bar that is at an angle for score section sections that aren't attached to anything else  
Dots - Same as in music  
Storage - Should be last word, means it's savable and should be in scoreStorage  

###### Abbreviations
nid - Short for note id  
did - Short for decoration id

###### Rests
A crotchet rest is called a rest1, a quaver rest is called a rest2, a semi-quaver rest is called a rest4, etc. (The number is the denominator of a fraction of a beat, e.g. 1/1, 1/2, 1/4)

### Project Structure
Some helpful information on the internals of how this project is played out.  

**_root_**  
├─ **_.github_, _images_, README.md, CONTRIBUTING.md** - Stuff for GitHub  
├─ **UDSP.spec** - For PYInstaller - compilation to executables  
└─ **_src_** - For PYInstaller - compilation to executables  
&emsp;&ensp;├─ **UltimateDrumScorerPro.py** - The main entrance script  
&emsp;&ensp;├─ **_images_** - Contains any and all images used by the program  
&emsp;&ensp;├─ **_designs_** - Contains the default designs for **_notes_** and **_decorations_**. Stored as json and hold what should go in the properties of that design, also hold id in "id" and canvas instructions in "instructions"  
&emsp;&ensp;├─ **_kv_** - Loads kv lang, all .kv go in here  
&emsp;&ensp;├─ **_renderer_** - Tools to render the forms of a score items.  
&emsp;&ensp;│ &ensp;└─ **_(item_type)_**  
&emsp;&ensp;│ &ensp;&emsp;&ensp;└─ **README.md** - Gives information about that specific renderer and the component's APIs.
&emsp;&ensp;│ &ensp;&emsp;&ensp;└─ **\_\_init\_\_.py** - File that links together this item type's components (as there can be multiple compnents for the same part (e.g. correctly rendered bars and bars rendered for editing)). This should still work if a component is missing (set to None)  
&emsp;&ensp;│ &ensp;&emsp;&ensp;└─ **(item_type)_(component_type).py** - These have no concept for scoreStorage, editing, etc. They exist purely to store data and modify it through an api which supplies the needed information  
&emsp;&ensp;│ &ensp;&emsp;&ensp;└─ **(item_type)_(component_type)Base.py** - Like an interface or ABC: it holds a set of functions that other components can implement or override.
&emsp;&ensp;└─ **_tools_** - Scripts to test various widgets and UIs.  
&emsp;&ensp;└─ **_scoreStorage_** - Tools for reading, writing and holding scores  
&emsp;&ensp;└─ **_scoreSectionDesigns_** - Tools for loading and drawing **_notes_** and **_decorations_**  

Whenever needed, kv, notes and decorations should have their check functions called at module level to make sure they
are loaded. E.G.
```python
from notes import notes, check_notes
check_notes()  # Ensures that the notes array has been filled.

def foo():
    notes[0].draw()  # We can now use it.
```

### Other small stuff
TextStorage has do_formatting, so we don't have to recreate the text renderer pipeline, instead it can just toggle off.