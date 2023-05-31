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

### NormalComponentOrganiser
It structures the group like this:
```
group
    - PushMatrix
    - InstructionGroup - Repeats for each section section
        - PushMatrix
        - PushMatrix
        - Translate - Position Heads
        - InstructionGroup - Heads
        - PopMatrix
        - Translate - Position Dots
        - InstructionGroup - Dots
        - Translate - Position Bars
        - PushMatrix
        - Translate - Position Bars
        - InstructionGroup - Bars
        - PopMatrix
        - PopMatrix
        - Translate - Prepare for next group
    ...
    - PopMatrix
```

