# Usage
ScoreSectionRenderer renders a section of notes and other parts that are of actual musical value.

# Component APIs
- Head Creators
  - .create(note_ids) -> tuple\[InstructionGroup, int, int\] - Creates an instruction group from the note ids, translate should be on right hand side and not popped. Also returns the width and height.  
<br>
- Decoration Creators
  - .create(decoration_id) -> tuple\[InstructionGroup, int, int\] - Creates an instruction group from the decoration id, translate should be on right hand side and not popped. Also returns the width and height.  
<br>
- Bar Creators
  - .create(full_bars, before_half_bars, after_half_bars) -> tuple\[InstructionGroup, int, int\] - Creates an instruction group from the amounts of bars, translate should be on right hand side and not popped. Also returns the width and height.  
<br>
- Dot Creators
  - .create(dots) -> tuple\[InstructionGroup, int, int\] - Creates an instruction group from the amounts of dots, translate should be on right hand side and not popped. Also returns the width and height.

# TODO:
API doc for organiser
Stem Creator