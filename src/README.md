# Rendering
A diagram of the algorithm for the beaming and rhythm stuff:
![image](https://github.com/user-attachments/assets/3cbde333-0225-4733-9cd5-972c669230fe)
  
The renderering of the components in the component container should be managed by rendered.js (which recieves events from the Managers).  
However the actual renderering (of the svg contents, the actual svg node is instantiated in rendered.js) is done by the (score,text)ComponentSvgRenderer.js files.

# Symbols
A symbol-id represents a specific drum (a cymbal counts as a drum) (e.g. kick, flam_snare, hi-hat) or a specific decoration (e.g. repeat-end). It consists of two parts - a base-id and zero or more modifier-ids - separated by an underscore. The base-id and modifier-id are both symbol-id-parts. These must be unique (so any pair of decorations, drums, groups, or parts cannot have the same symbol-id-parts). The modifier-ids will always be stored in alphabetical order internally.  
A symbol-id-part is a lowercase string containing only alphabetical characters and dashes  (these can technically be an empty string). 
The base-id is what it actually is - e.g. snare. The modifier-id is how it has been changed - e.g. ghost, flam. Together this makes snare\_ghost_flam.  
A drum-id is a symbol-id that refers to a symbol that is a drum. This can be any symbol-id.  
A decoration-id is a symbol-id that refers to a symbol that is a decoration. This can only be a symbol-id-part (i.e. it cannot be modified).  
A part-id is a symbol-id that refers to a reusable component that can be used inside drums or decorations, This can only be a symbol-id-part (i.e. it cannot be modified).  
A group-id refers to a group of symbol-ids. This can only be a symbol-id-part (i.e. it cannot be modified).  
  
`new,drum,<id: base-id>,<size-left: float>,<size-up: float>,<size-right: float>,<size-down: float>,<instructions...: list<instruction...>>,<groups...: list<group-id>>`  
Adds a new base-symbol for a drum with the given id. The id must not be taken.  
The sizes are the distance from the anchor (the location where the symbol attaches to the stem) that this symbol takes up. These sizes should not account for stroke-width.  
<img src="/docImages/drumSizing.jpeg" alt="image" width="200"/>

`new,decoration,<id: base-id>,<width: float>,<min-height: float>,<min-below-drums: optional<float>>,<min-above-drums: optional<float>>,<min-above-beams: optional<float>>,<min-above-contracts>,<side: union<"left","right">>,<instructions...: list<instruction...>>`  
Adds a new base-symbol for a decoration with the given id. The id must not be taken.  
The side can be "left" or "right", and is used to decide which side of the bar the decoration goes on.  
The decoration instructions are relative to the right side of the decoration, and centre-y of the decoration.  
The given sizes should not account for stroke-width. The min-below and min-above quantities will not be adjusted for stroke width.  

If specified, `min-below-drums`, `min-above-drums`, `min-above-beams`, `min-above-contracts` require the appropriate edge to be the given distance below or above the drums (depending on the implementation - if it makes sense - this may also take rests into account). These can be negative, but positive values work in the direction away from the centre.  
The height of the decoration will always be at least `min-height`.  
![image](/docImages/decorationSizing.jpeg)
*(Note that `min-above-contracts` is ommitted here, but that height would be taken from the top of the three (3))*

1:   If no "min-..." parameters are given, then the anchor-y is taken to be `drum-center-y` and the height is taken to be `min-height`.  
2:   If only "above" or only "below" "min-..." parameters are given, then the anchor-y is taken to be `min-height/2` towards the centre from the furthest given parameter, and the height to be `min-height`.  
3,4: If both an "above" and a "below" "min-..." parameter is given, then the anchor-y is taken centred between them. If the distance between these points is less than `min-height` then the height is set to `min-height` (centred on the same anchor-y).  
In all cases, the anchor is on the right edge and vertically centred.  

![image](/docImages/decorationCases.jpg)
  
`new,part,<id: part-id>,<instructions...: list<instruction...>>`  
Adds a new part symbol with the given id. The id must not be taken.  
`modifier,drum,explicit,<id: drum-id>,<size-left: float>,<size-up: float>,<size-right: float>,<size-down: float>,<instructions...: list<instruction...>>,<groups...: list<group-id>>`  
Adds a new symbol for a drum with the given id. The id must not be taken, however the modifier itself can have already been used. The id must be modified at least once, and the base-id must be taken.  
The sizes are the distance from the anchor (the location where the symbol attaches to the stem) that this symbol takes up.  
This will not inherit instructions or groups from the base-ids or any related symbol-ids. You must specify these yourself.  
The given sizes should not account for stroke-width.  

`modifier,drum,auto,<modifier-id: modifier_id>,<pattern...: list<pattern-part>>,(+<parent-detla|~<base-detla|\><min)size-left: float>,(+<parent-detla|~<base-detla\><min)size-up: float>,(+<parent-detla|~<base-detla\><min)size-right: float>,(+<parent-detla|~<base-delta|\><min)size-down: float>,<min-width: float>,<min-height: float>,<instructions...: list<instruction...>>,<groups...: list<group-id>>`  
Adds new symbols for each drum who's id matches the pattern (non-drum matches will throw an exception). At least one id must match the pattern. The modifier can have been used already, but if the combined ids may not be taken.  
The created drum's ids are the old id with the modifier added onto the end.  
For each of the size-(left,right,up,down), you can specificy whether it is a parent-delta, base-delta or a minimum. The delta is added on to the parent or base's size. The minimum means we take the maximum of the given minimum and the old size. In case it still isn't clear, you specify which you want using + and > and ~ (e.g. ...,+5,+1,>3,+2,...). To specifify no change, you can pass `0`.  
The min-width and min-height are extra options to say we want at least this width and this height centered around the centre of the parent. So if we have the size-right=0 and size-left=5 and min-width=10, size-left of the new drum will be 7.5, and the size-right of the new drum will be 2.5. A maximum will be taken between sizes computed this way and sized computed from deltas/mins.  
The created drum will inherit instructions and groups from the drum it was created from, and will have the new instructions and groups appended to the end.  
The given sizes should not account for stroke-width.  
  
`constraint,drum,<top-id: union<drum-id,group-id>>,<bottom-id: union<drum-id,group-id>>,<distance: float>`  
Adds a constraint to say a given drum/group must be above another drum/group. The given ids must exist.  
If a group id is used, then it refers to every single drum in that group. Any non-drum symbol will be ignored.  
The distance is the minimum distance an item on top may be drawn from an item on the bottom. Any desired indirect distances must be specified directly.   
- E.g. if a is 0 above b and b is 5 above c, then if only a and c are drawn then a will b 0 above c. If you want to keep the five constraint between a and c then you must add that constraint with another constraint or by using a group.  
  
`list<i...: T>`: `<number-of-elements>,` + elements separated by commas.  
The elements themselves may be constructed of multiple pieces of data that are also separated by commas.
  
`instruction...`: `<instruction-name>,<instruction-args...>`
The instruction arguements depend on the name. These are the instructions:  
* `path,<path-string: string>` - Draws a path. Given string is as per the SVG spec.  
* `circle,<cx>,<cy>,<r>` - Draws a unfilled-circle with centre `(cx, cy)` and radius `r`.  
* `use,<symbol-id>` - Uses adds the instructions for another symbol in this location. This could be a drum, decoration or part. This ID must exist.  
* `push-transform,<transform-string>` - Pushes a transformation. The given string is as per the SVG spec.  
* `pop-transform` - Pops a transformation.  

Inside these instructions (apart from `use`), we can specify 'format_values' by writing `${expression}`.  
This expression can use `+`, `-`, `*`, `/`, `(` and `)` and can work on variables and float-literals. Unary operations are supported for `+` and `-`.  
There are two types of variables, local and global. Local apply only to that instruction, and do not carry through to bases or through 'use' calls. Global variables will.
Variables can only store floats.
| Identifier                                                                     | __L__ocal/__G__lobal | D__r__ums/D__e__corations | Notes                                                                                       |
|--------------------------------------------------------------------------------|----------------------|---------------------------|---------------------------------------------------------------------------------------------|
| `size_left`, `size_right`, `size_up`, `size_down`                              | G                    | r                         | The size of the final symbol after any modifications are processed.  <br>Relative to the anchor.                         |
| `base_size_left`, `base_size_right`, `base_size_up`, `base_size_down`          | G                    | r                         | The size of the base symbol before any modifications are processed.  <br>Relative to the anchor.                         |
| `parent_size_left`, `parent_size_right` , `parent_size_up`, `parent_size_down` | L                    | r                         | Refer specifically to the direct parent.  <br>Only available for automatically modified drums.   |
| `drum_center_y`                                                                | G                    | e                         | Relative to the (0,0) of the decoration. See the diagram in the `new,decoration` instruction. This does not take rests into account. |
| `width`, `height`                                                              | G                    | e                         |                                                                                               |

`transform-string`: 
This should be the same format as the SVG spec uses for transforms. This should contain no commas, and should not be wrapped with quotes.

`pattern-part` : `<action><id: Union<symbol-id, "*[drums|decorations|parts]">>` (yes, without the comma).  
A pattern refers to a set of symbols (these can be of any type, but the function using these symbols may put limitations on this).  
The pattern is build from pattern-parts, and each pattern-part is an instruction to include or exclude ids.  
The `action` can be `+` or `-`, meaning to add all matching symbols or remove any previously-matched matching symbols respecitvely.  
If the id is a group, then it adds/removes all ids that are in that group.  
If the id is the string literal "\*drums" or "\*decorations" or "\*parts", then it will add every id from the given group.




# Data flow / event processing
## "Class diagrams" for managers
Events are bound using on\<EventName\>(some function), and dispatched using dispatch\<EventName\>(your, args).  
Operations within managers should be atomic.  
```
ComponentManager - Stores persistant state of entities.
	- Events:
		- Component(Added|Removed) {componentId}
		- BeforeComponentRemoved {componentId}
		- Component(X|Y|TimeSignatureDenomenator|RhythmLengthHint|Text|FontSize)Changed {componentId, newValue}
		- Component(Left|Right)DecorationChanged {componentId, newId|null}
		- ComponentVertGroupChanged {oldGroup, newGroup} - `oldGroup` and `newGroup` are lists of ids. Corrosponding to a group before and a group after. If either is null, it means the group didn't exist before/after. The set difference can tell you which ids changed.
		- ComponentDrumToggled {componentId, beatI, subdivisionI, drumId, newValue}
		- ComponentDrumEnabledStateChanged {componentId, drumId, newValue}
		- ComponentBeatsAdded {componentId, numberOfSubdivisions, ...beatIndexes} - The `beatIndexes` will be in ascending order, and were applied in that order.
		- ComponentBeatsRemoved {componentId, ...beatIndexes} - The `beatIndexes` will be in ascending order, and were applied in that order.
		- ComponentSubdivisionsAdded {componentId, beatI, ...subdivisionIndexes} - The `subdivisionIndexes` will be in ascending order, and were applied in that order.
		- ComponentSubdivisionsRemoved {componentId, beatI, ...subdivisionIndexes} - The `subdivisionIndexes` will be in ascending order, and were applied in that order.
	- Methods:
		- CreateEmptyComponent (typeId) -> componentId
		- ComponentExists(componentId) -> bool
		- GetComponentType(componentId) -> component-type
		- RemoveComponent(componentId)
		- DuplicateComponent(componentId) -> newComponentId
		- ToggleComponentDrum(componentId, beatI, subdivisionI, drumId)
		- GetComponentDrumState(componentId, beatI, subdivisionI, drumId) -> bool
		- GetComponentSubdivisonDrums(componentId, beatI, subdivisionI) -> Object.freeze(Set<drum-id>)
		- ToggleComponentDrumEnabledState(componentId, drumId)
		- GetComponentDrumEnabledState(componentId, drumId) -> bool
		- SetComponent(X|Y|TimeSignatureDenomenator|RhythmLengthHint|Text|FontSize)(componentId, newValue)
		- GetComponent(X|Y|TimeSignatureDenomenator|Text|FontSize)(componentId) -> someApplicableType
        - GetComponentRhythmLengthHint(componentId) -> float - The minimum desired width (in mm) for each beat. Padding can be added (where spacing is representative of the rhythmic gap). This is guidline and need not be exactly adhered to; the current implementation only adds padding when the current width is smaller than than it's rythmic value.
		- SetComponent(Left|Right)Decoration(componentId, decoration-id|null)
		- GetComponent(Left|Right)Decoration(componentId) -> decoration-id|null
		- AddVertGroup(...componentIds) - Creates a vertical-group between the given components, any already given components will be removed from those groups.
		- RemoveFromVertGroup(...componentIds) - Any vertGroups of length 1 will be removed.
		- IsInVertGroup(componentId) -> bool
		- GetVertGroup(componentId) -> Object.freeze(Set<component-id>)
		- AddBeats(componentId, numberOfSubdivisions, ...beatIndexes)
		- RemoveBeats(componentId, ...beatIndexes)
		- AddSubdivisions(componentId, beatI, ...subdivisionIndexes)
		- RemoveSubdivisions(componentId, beatI, ...subdivisionIndexes)
		- GetComponentBeatCount(componentId) -> int
		- GetComponentBeatSubdivisionCount(componentId, beatI) -> int
        - GetComponentIds() -> Object.freeze(Set<component-id>)
SelectionManager - Stores temporary state of selection.
	- Events:
		- SelectionStateChanged {componentId, selectionState}
	- Methods:
		- ToggleSelectionState(componentId, multiselect)
		- Select(componentIds...) - Will unselect all other selected components.
		- ClearSelection()
		- IsSelected(componentId) -> bool
		- GetSelection() -> Object.freeze(Set<component-id>)
DragManager - Stores temporary state of drag. Also determines wether the mouse move was significant enough to initiate a drag.
	- Events:
		- Drag(Start|End) {Object.freeze(Set<component-id>)} - Dispatched only when a mouse movement is deemed significant enough.
		- DragMove {Object.freeze(Set<component-id>), totalDeltaX, totalDeltaY} - componentIds will remain the same as DragStart until ended. Delta is relative to start position. Dispatched only when a mouse movement is deemed significant enough.
	- Methods
		- startDrag(cardinal, mainTarget) - Cardinal is whether to lock movement to cardinal directions, what is passed is initial value. MainTarget is the component that was actually clicked
		- moveDrag(deltaX, deltaY) - Delta is relative to last time moveDrag was called.
		- endDrag() -> bool  - Returns true if the drag was significant (and components were actually moved)
		- setCardinal(cardinal) - Cardinal is whether to lock movement to cardinal directions.
        - isDragging() -> bool - Returns true if there is currently a drag. This ignores the significance of the drag.
```

## Processes
The basic thought process is all data flows through the managers. If the editor updates something, it can change the state of itself locally (an error will be thrown if it fails) and send this to the ComponentManger, however the renderer listens to and only to the ComponentManger.
### Loading components
```
1. ComponentManager updates state internally.
2. ComponentManager emits ComponentAdded for each component added.
```
### Adding a \<type\>-component
```
1. Add component button pressed.
	2. ComponentManager.createEmptyComponent(<type>).
		3. ComponentManager creates said component internally with id <id>.
		4. ComponentManager emits ComponentAdded {<id>}.
			5. Renderer renders <id>.
	6. SelectionManager.select(<id>).
		7. SelectionManager updates internally.
		8. SelectionManager emits SelectionStateChanged for all affected components.
			9a. Renderer responds accordingly.
			9b. Editor switches to <id>.
```
### Removing a component
```
1. Remove component button pressed for component with id <id>.
	2. ComponentManager.removeComponent(<id>).
		3. ComponentManager emits BeforeComponentRemoved.
			4. SelectionManager internally unselects <id> (if selected).
				5. SelectionManager emits SelectionStateChanged.
					6a. Editor responds accordingly.
					6b. Renderer responds accordingly.
			7. Renderer responds accordingly.
		8. ComponentManager removes component internally and silently drops groups.
		9. ComponentManager emits ComponentRemoved.	
```
### Duplicating a component.
```
1. Duplicate component button pressed for component with id <id>.
	2. ComponentManager.duplicateComponent(<id>) -> <newId>.
		3. ComponentManager updates state internally.
		4. ComponentManager emits ComponentAdded {<id>}.
			5. Renderer responds accordingly.
	5. SelectionManager.select(<newId>)
		6. SelectionManager updates internally.
		7. SelectionManager emits SelectionStateChanged for all affected components.
			8a. Renderer responds accordingly.
			8b. Editor switches to <id>.
```
### Modifying a component
```
1. Toggle pressed on <id>.
	2. State of toggle not changed.
	3. ComponentManager.toggleComponentDrum(<id>, ...).
		4. ComponentManager updates internal state.
		5. ComponentManager emits ComponentDrumToggled.
			6a. Renderer responds accordingly.
			6b. Editor updates toggle state.
```
### Adding/remove a drum from component in editor
```
1. Component is <componentId>. Drum is <drumId>. Click happens in editor.
	2. Drums shown not changed.
	3. ComponentManager.toggleComponentDrumEnabledState(<compId>, <drumId>).
		4. ComponentManager adds or removes drums internally (without emitting any events).
		5. ComponentManager emits ComponentDrumEnabledStateChanged.
			6. Editor responds accordingly.
```
### Clicking on/dragging a component
These two are so intertwined that we will descript this with one flow.
All drag events go to the drag manager. The manager decides internally whether the drag is significant enough to actually be a drag rather than a click. 
It will only drag when a component is the start-point / where the mouse-down occured.
```
1. <id> clicked on.
	3. <shift> is true if shift is pressed.
	4. index.html calls DragManager.startDrag(cardinal=<shift>, targetId=<id>)
		5a. If <targetId> is currently selected, then <selected> is set to current SelectionManager.getSelection().
		5b. If <targetId> is not currently selected, so <selected> is set to <targetId>.
[      	6. DragManager emits DragStart {<selection>}.                     ]  // This may be done late when drag significance is determined
[			7. Renderer adds "translate" to each of <selection>'s style.  ]
8a. Mouse moves by <delta>mm.
	9. index.html calls DragManager.moveDrag(<delta>)
		10. DragManager updates state internally.               
[		11. DragManager emits DragMove {<selected>, <delta>}.   ]  // This may be done late when drag significance is determined
[			12. Renderer responds accordingly.                  ]
8b. Shift pressed/unpressed -> <shift>.
	9. index.html calls DragManager.setCardinal(<shift>)
		10. DragManager calculates <delta>.
		11. DragManager updates state internally.
[		12. DragManager emits DragMove {<selected>, <delta>}.   ]  // This may be done late when drag significance is determined
[			13. Renderer responds accordingly.                  ]
14. Mouse relased.
	14. index.html calls DragManager.endDrag()
		15. DragManager updates state internally.
[		16. DragManager calls ComponentManager.set(X|Y)(...).                  ]  // This may not be done, depending on drag significance
[			17. ComponentManager updates state internally.                     ]
[			18. ComponentManager emits Component(X|Y)Changed.                  ]
[				19. Renderer responds accordingly.                             ]
[		20. DragManager emits DragEnd {<selected>}.                            ]
[			21. Renderer removes "translate" from selected components styles.  ]
    15. if DragManager.endDrag() returns False then a click is processed.
        16. <id> clicked on.
        17. Mouse has not moved (much).
        18. <shift> is true if shift is pressed.
        19. Renderer calls SelectionManager.toggleSelectionState(<id>, multiselect=<shift>)
	        20. SelectionManager updates itself internally.
	        21. SelectionManager emits SelectionStateChanged as required.
	        	22a. Renderer responds accordingly.
		        22b. Editor responds accordingly.
```
### Vertically grouping components
```
1. <ids> are selected.
2. Group pressed in editor.
	3. ComponentManager.AddVertGroup(<ids>)
		4. ComponentManager internally removes any <ids> from any pre-existing groups, and destroys length 1 or 0 groups.
		5. ComponentManager emits ComponentVertGroupChanged for any changed groups.
			6. Renderer responds accordingly.
		7. ComponentManager internally adds a group for <ids>.
		8. ComponentManager emits ComponentVertGroupChanged for created group.
			9. Renderer responds accordingly.
```
### Adding a beat (/subdivision)
```
1. Editor calls ComponentManager.addBeats(<id>, <nos>, 4, 1, 4)
	2. ComponentManager adds them internally (and sorts and updates beat indecies to be in ascending order, such that the outcome would be the same if beats were added using the old or new indicies).
	3. ComponentManager dispatches ComponentBeatsAdded {<nos>, 4, 1, 4}
		4. Editor and Renderer respond accordingly.
```

# Current Architecture
I have this diagram, I like diagram.
![image](/docImages/v4-stage2-architecture.jpeg)
Just wait for Stage2-V3 it get's worse.
