# What does this do?
ScoreSectionRenderer renders a section of notes and other parts that are of actual musical value.

# Component Information
### Creators
Anything returning a tuple of an InstructionGroup, float and float will probably mean width and height.

### StemCreator
Returns just the width since height is determined by everything else.

### BarCreator
Returned width is minimum width as it will size to fit section section.

### HeadCreator
Along with width and height, returns a third value which is the y level and note id of the lowest note.

### DecorationCreator
Instead of height, it returns the minimum height. When height is updated, these may scale to be the full height or can
ignore it (rests don't increase in height, but a bracket may).

### NormalDecorationCreator
The first draw of decorations is at min_height, this is then updated later in the update function.

### ComponentOrganiser
Some functions may return new instructions for the ScoreSectionRenderer to process (like resizing bar now we know 
correct width).  
These may be update_bar_width(bar_group, width), update_stem_height(stem_group, overall_height, index), or 
set_size(width, height)

### NormalComponentOrganiser
It structures the group like this:
```
group
    - PushMatrix
    - InstructionGroup - Repeats for each section section
        - InstructionGroup - Decorations
        - PushMatrix
        - Translate - Position Heads
        - InstructionGroup - Heads
        - Translate - Position Dots
        - InstructionGroup - Dots
        - PopMatrix
        - PushMatrix
        - Translate - Position Stem
        - PushMatrix
        - Translate - Position Stem
        - InstructionGroup - Stem
        - PopMatrix
        - Translate - Position Bars
        - InstructionGroup - Bars
        - PopMatrix
        - Translate - Prepare for next group
    ...
    - PopMatrix
```
Note that bars are updated to have the width + the stem width to ensure there are no artifacts where two lines join. 
To make sure it fits, bars are then transformed by 1/2 of a stem width, so it is halfway inside the stem.
