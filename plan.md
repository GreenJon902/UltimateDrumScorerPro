# Class Diagrams
```
ComponentManager - Stores persistant state of entities.
	- Events:
		- Component(Added|Removed) {componentId}
		- BeforeComponentRemoved {componentId}
		- Component(X|Y|TimeSignatureDenomenator|RhythmLengthHint)Changed {componentId, newValue}
		- Component(Left|Right)DecorationChanged {componentId, newId|null}
		- ComponentVertGroupChanged {oldGroup, newGroup} - `oldGroup` and `newGroup` are lists of ids. Corrosponding to a group before and a group after. If either is null, it means the group didn't exist before/after. The set difference can tell you which ids changed.
		- ComponentToggleChanged {componentId, beatI, subdivisionI, toggleId, newValue}
		- ComponentToggleEnabledStateChanged {componentId, toggleId, newValue}
	- Methods:
		- CreateEmptyComponent (typeId) -> componentId
		- RemoveComponent(componentId)
		- DuplicateComponent(componentId) -> newComponentId
		- ToggleComponentToggle(componentId, beatI, subdivisionI, toggleId)
		- ToggleComponentToggleEnabledState(componentId, toggleId)
		- SetComponent(X|Y|TimeSignatureDenomenator|RhythmLengthHint)(componentId, newValue)
		- SetComponent(Left|Right)Decoration(componentId, newId|null)
		- AddVertGroup(...componentIds) - Creates a vertical-group between the given components, any already given components will be removed from those groups.
SelectionManager - Stores temporary state of selection.
	- Events:
		- SelectionStateChanged {componentId, selectionState}
	- Methods:
		- ToggleSelectionState(componentId, multiselect)
		- Select(componentIds...) - Will unselect all other selected components.
		- ClearSelection()
DragManager - Stores temporary state of drag.
	- Events:
		- Drag(Start|End) {componentIds}
		- DragMove {componentIds, delta} - componentIds will remain the same as DragStart until ended.
	- Methods
		- startDrag(componentId, cardinal) - Id is id of component that was clicked. Cardinal is whether to lock movement to cardinal directions, what is passed is initial value.
		- moveDrag(<delta>)
		- endDrag()
		- setCardinal(cardinal) - Cardinal is whether to lock movement to cardinal directions.
```

# Processes
## Loading components
```
1. ComponentManager updates state internally.
2. ComponentManager emits ComponentAdded for each component added.
```
## Adding a <type>-component
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
## Removing a component
```
1. Remove component button pressed for component with id <id>.
	2. ComponentManager.removeComponent(<id>).
		3. ComponentManager emits BeforeComponentRemoved.
			4. SelectionManager internally unselects <id> (if selected).
				5. SelectionManager emits SelectionStateChanged.
					6a. Editor responds accordingly.
					6b. Renderer responds accordingly.
			7. Renderer responds accordingly.
		8. ComponentManager removes component internally and silently drops links.
		9. ComponentManager emits ComponentRemoved.	
```
## Duplicating a component.
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
## Modifying a component
```
1. Toggle pressed on <id>.
	2. State of toggle not changed.
	3. ComponentManager.toggleComponentToggle(<id>, ...).
		4. ComponentManager updates internal state.
		5. ComponentManager emits ComponentToggleChanged.
			6a. Renderer responds accordingly.
			6b. Editor updates toggle state.
```
## Adding/remove a toggle from component in editor
```
1. Component is <componentId>. Toggle is <toggleId>. Click happens in editor.
	2. Toggles shown not changed.
	3. ComponentManager.toggleComponentToggleEnabledState(<compId>, <toggleId>).
		4. ComponentManager adds or removes toggles internally.
		5. ComponentManager emits ComponentToggleEnabledStateChanged.
			6. Editor responds accordingly.
```
## Clicking on a component
```
1. <id> clicked on.
2. Mouse has not moved (much).
3. <shift> is true if shift is pressed.
4. Renderer calls SelectionManager.toggleSelectionState(<id>, multiselect=<shift>)
	5. SelectionManager updates itself internally.
	6. SelectionManager emits SelectionStateChanged as required.
		7a. Renderer responds accordingly.
		7b. Editor responds accordingly.
```
## Dragging a component
```
1. <id> clicked on.
	2. Mouse has moved (much).
	3. <shift> is true if shift is pressed.
	4. Renderer calls DragManager.startDrag(<id>, cardinal=<shift>)
		5. <selected> is set to current SelectionManager.getSelection().
		6. DragManager emits DragStart {<selection>}.
			7. Renderer adds "translate" to each of <selection>'s style.
8a. Mouse moves by <delta>mm.
	9. Renderer calls DragManager.moveDrag(<delta>)
		10. DragManager updates state internally.
		11. DragManager emits DragMove {<selected>, <delta>}.
			12. Renderer responds accordingly.
8b. Shift pressed/unpressed -> <shift>.
	9. Renderer calls DragManager.setCardinal(<shift>)
		10. DragManager calculates <delta>.
		11. DragManager updates state internally.
		12. DragManager emits DragMove {<selected>, <delta>}.
			13. Renderer responds accordingly.
14. Mouse relased.
	14. Renderer calls DragManager.endDrag()
		15. DragManager updates state internally.
		16. DragManager calls ComponentManager.set(X|Y)(...).
			17. ComponentManager updates state internally.
			18. ComponentManager emits Component(X|Y)Changed.
				19. Renderer responds accordingly.
		20. DragManager emits DragEnd {<selected>}.
			21. Renderer removes "translate" from selected components styles.
```
## Linking components
```
1. <ids> are selected.
2. Linked pressed in editor.
	3. ComponentManager.AddVertGroup(<ids>)
		4. ComponentManager internally removes any <ids> from any pre-existing groups, and destroys length 1 or 0 groups.
		5. ComponentManager emits ComponentVertGroupChanged for any changed groups.
			6. Renderer responds accordingly.
		7. ComponentManager internally adds a group for <ids>.
		8. ComponentManager emits ComponentVertGroupChanged for created group.
			9. Renderer responds accordingly.
```

# New note-head/note-decoration system
We store all the info in this string, which can be compiled into svg at the start or something idk.
`action=new_base,base-symbol-id,size-left,size-up,size-right,size-down,number-of-instructions,(instruction-id,(instruction-args,)+)+,number-of-groups,[group-id,]+`  
`action=new_part,part-symbol-id,number-of-instructions,(instruction-id,(instruction-args,)+)+`  
`action=modifier_explicit,base-symbol-id(_modifier-id)+,size-left,size-up,size-right,size-down,number-of-instructions,(instruction-id,(instruction-args,)+)+,number-of-groups,[group-id,]+`  
`action=modifier_auto,modifier-id,pattern_part_number(,pattern_parts)+,(+delta,>min)-size-left,(+delta,>min)-size-up,(+delta,>min)-size-right,(+delta,>min)-size-down,min-width,min-height,number-of-instructions,(instruction-id,(instruction-args,)+)+,number-of-groups,[group-id,]+`  
`action=head_contstraint,(top-group-id|top-symbol-id),(bottom-group-id|bottom-symbol-id),distance`  
A `base-symbol-id` is the name of an unmodified head.  
A `part-symbol-id` is the name of some collection of instructions that can be re-used, but is nothing on it's own.  
A `modifier-id` is the id of a certain modifier, these may be drawn differently for different heads.
A `symbol-id` is the name of a (possibly modified) head, formatted `base-symbol-id[_modifier-id]+`. This does not include `part-symbol-id`s. If a given `symbol-id` is a modified id, then the corresponding `base-id` must also exist. 
A `group-id` refers to multiple different `symbol-id`s.
No duplicate IDs are allowed. This includes `group-id`s being the same as `symbol-id`s.

The `modifier_explicit` is the same as `new_base`, but it has a modified symbol id rather than a base symbol id.

In the `modifier_auto`, the pattern is a collection of include and exclude statements that tells the program what to generate. Later parts take precident. These are the possible options:  
- `*` - take all `symbol-id`s.  
- `*(_modifier-id)+` - take all `symbol-id`s with the given `modifier-id`s.  
- `-` before a statement - to reject all the ones that match.  
- `symbol-id` - match a specific symbol. 
- `group-id` - match a specific group.
- `group-id(_modifier-id)+` - take all `symbol-id`s in the given `group-id` with the given `modifier-id`s. 
The output of the `modifier_auto` is this: for each matched `symbol-id`, create a new symbol `symbol-id_modifier-id` that is the new instructions on top of the instructions from the old symbol.  
The min-width and min-height are centered around the size of the oringonal symbol before we modified it (if this is second modification, then take the size after first modification).
The created symbols inherit the groups from their parents as well as the new groups.

Possible instructions:  
- `path`,`path-string`  
- `circle`,`cx`,`cy`,`r`  
- `use`,`symbol-id`  
- `use`,`part-symbol-id`  
- `push-transform`,`transform-string`  
- `pop-transform`  
Extra instructions for `modifier_auto`:  
- `push-anchored-transform`,(`left`|`middle`|`right`),(`top`|`middle`|`bottom`)  - This is relative to the size of the current symbol after applying the new sizing information.

The `head_contstraint` means the anchor of the top symbol from `bottom-group-id` / the `bottom-symbol-id` must be a minimum of `distance` below the anchor of the bottom symbol from `top-group-id` / the `top-symbol-id`. If no symbols from `top-group-id` are drawn, then take the bottom of the first symbol that would be drawn above the bottom of `top-group-id`.  
If the `head_contstraint` `distance` is 0, the `bottom-group-id` / `bottom-symbol-id` will still all be drawn below `top-group-id` / `top-symbol-id`. If a constraint is not given then the order they are drawn is undefined behavior, however there should be no conflicts between head constraints.  

## Class Diagram
```
Symbols - Loads the symbols from the symbol string and gives the rest of the program access to it.
	getFullOrder() - Returns an array with all symbols ids in the order from top to bottom. This will have no duplicates and will be consistant with isBelow.
	isBelow(symbolId1, symbolId2) - Should symbolId2 be drawn beneath symbolId1? The results of this function will be consistant (with itself and getFullOrder) throughout the run of the program.
	getMinDistanceBetween(symbolId1, symbolId2) - Get's the minimum distance between the anchors of symbolId1 and symbolId2. If symbolId2 should be drawn above symbolId1 then an error is thrown.
	getSymbolNode(symbolId) - Returns an svg node for the given symbol.
	getSymbolSize(Left|Right|Up|Down)(symbolId) - Returns the distance from the stem that this symbol goes. This takes into account the extra information in the modifier.
```
