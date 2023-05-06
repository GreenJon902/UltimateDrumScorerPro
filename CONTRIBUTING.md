# Contributing to UDSP
Hi there! I doubt anyone will but if you want to contribute then great. Please keep the codebase nice. Apart from that here are some notes on the internals and the general structure of the project.

# Notes on Internals
### Project Structure
├─ **_.github_, _images_, README.md, CONTRIBUTING.md** - Stuff for GitHub  
├─ **UDSP.spec** - For PYInstaller - compilation to executables  
└─ **_src_** - For PYInstaller - compilation to executables  
&emsp;&ensp;├─ **UltimateDrumScorerPro.py** - The main entrance script  
&emsp;&ensp;├─ **_images_** - Contains any and all images used by the program  
&emsp;&ensp;├─ **_kv_** - Loads kv lang, all .kv go in here  
&emsp;&ensp;├─ **_renderer_** - Tools to render the forms of a score items  
&emsp;&ensp;│ &ensp;└─ **_component_**  - The renders for parts of score items  
&emsp;&ensp;└─ **_tests_**  - Scripts to test various widgets and UIs.


### Rests
A crotchet rest is called a rest1, a quaver rest is called a rest2, a semi-quaver rest is called a rest4, etc. (The number is the denominator of a fraction of a beat, e.g. 1/1, 1/2, 1/4)