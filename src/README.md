# Rendering
A diagram of the algorithm for the beaming and rhythm stuff:
![image](https://github.com/user-attachments/assets/3cbde333-0225-4733-9cd5-972c669230fe)

# Data flow / event processing
## "Class diagrams" for managers
Events are bound using on\<EventName\>(some function), and dispatched using dispatch\<EventName\>(your, args).
```
ComponentManager - Stores persistant state of entities.
	- Events:
		- Component(Added|Removed) {componentId}
		- BeforeComponentRemoved {componentId}
		- Component(X|Y|TimeSignatureDenomenator|RhythmLengthHint|Text|FontSize)Changed {componentId, newValue}
		- Component(Left|Right)DecorationChanged {componentId, newId|null}
		- ComponentVertGroupChanged {oldGroup, newGroup} - `oldGroup` and `newGroup` are lists of ids. Corrosponding to a group before and a group after. If either is null, it means the group didn't exist before/after. The set difference can tell you which ids changed.
		- ComponentToggleChanged {componentId, beatI, subdivisionI, toggleId, newValue}
		- ComponentToggleEnabledStateChanged {componentId, toggleId, newValue}
	- Methods:
		- CreateEmptyComponent (typeId) -> componentId
		- ComponentExists(componentId) -> bool
		- GetComponentType(componentId) -> component-type
		- RemoveComponent(componentId)
		- DuplicateComponent(componentId) -> newComponentId
		- ToggleComponentToggle(componentId, beatI, subdivisionI, toggleId)
		- ToggleComponentToggleEnabledState(componentId, toggleId)
		- SetComponent(X|Y|TimeSignatureDenomenator|RhythmLengthHint|Text|FontSize)(componentId, newValue)
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

## Processes
### Loading components
```
1. ComponentManager updates state internally.
2. ComponentManager emits ComponentAdded for each component added.
```
### Adding a <type>-component
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
		8. ComponentManager removes component internally and silently drops links.
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
	3. ComponentManager.toggleComponentToggle(<id>, ...).
		4. ComponentManager updates internal state.
		5. ComponentManager emits ComponentToggleChanged.
			6a. Renderer responds accordingly.
			6b. Editor updates toggle state.
```
### Adding/remove a toggle from component in editor
```
1. Component is <componentId>. Toggle is <toggleId>. Click happens in editor.
	2. Toggles shown not changed.
	3. ComponentManager.toggleComponentToggleEnabledState(<compId>, <toggleId>).
		4. ComponentManager adds or removes toggles internally.
		5. ComponentManager emits ComponentToggleEnabledStateChanged.
			6. Editor responds accordingly.
```
### Clicking on a component
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
### Dragging a component
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
### Linking components
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
