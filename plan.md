# Event Design
## Classes-ish
### StateManager
```
StateManager
	- loadComponentsFromJson(json)
	- createEmptyComponent(select)
	- setToggleState(beatI, subdivisionI, toggleId, state)
	- setSelected(componentId...)
	- drag(dx, dy)
```

`StateManager#createEmptyComponent` - `select` is whether it's selected by default (will deselect others).  
`StateManager#setSelected` - Pass no arguments to select nothing.  
`StateManager#drag` - Positions are relative to last position of the mouse.  

### Handler
```
Handler
	- addComponent(componentId)
	- removeComponent(componentId)
	- getComponentHandler(componentId) -> (S)ComponentHandler
EditorHandler
	- addComponent(componentId)
	- removeComponent(componentId)
	- getComponentHandler(componentId) -> (S)ComponentHandler
ComponentHandler
	- setSelected(isSelected)
TextComponentHandler : ComponentHandler
	- setText(text)
	- setFontSize(fontSize)
ScoreComponentHandler : ComponentHandler
	- addBeat(beatI, [linkId])
	- removeBeat(beatI, [linkId])
	- addToggles(toggleId, [linkId])
	- removeToggles(toggleId, [linkId])
	- setX(x, [linkId])
	- setY(y, [linkId])
	- setTimeSignatureDenomenator(timeSignatureDenomenator, [linkId])
	- setRhythmLengthHint(rhythmLengthHit, [linkId])
	- setLeftDecoration(leftDecorationId, [linkId])
	- setRightDecoration(rightDecorationId, [linkId])
	- addLink(linkId)
	- removeLink(linkId)
	- getToggleHandler(beatI, subdivisionI, toggleId) -> ScoreComponentToggleHandler
ScoreComponentToggleHandler
	- setState(state)
```

`Handler#addComponent` - Creates an empty component.  
`Handler#addComponent` - Apart from the following, the initial values for a component are [undefined](## "Their values don't matter, as they will be overwritten before the next frame."). Components: selected is false. Score-components: `"enabled-toggles"` is empty, `"score-content"` is empty.  
`ScoreComponentHandler#addBeat` - The given index is the position that the new beat will be in the list.  
`ScoreComponentHandler#addBeat`, `ScoreComponentHandler#addToggles` - The initial states for any toggles is [undefined](## "The value doesn't matter, as it will be overwritten before the next frame.").  
`ScoreComponentHandler#setLeftDecoration`, `ScoreComponent#setRightDecoration` - The argument can be null for none.  
`ScoreComponentHandler#addBeat`, `ScoreComponentHandler#removeBeat`, `ScoreComponentHandler#addToggles`, `ScoreComponentHandler#removeToggles`, `ScoreComponentHandler#setX`, `ScoreComponentHandler#setY`, `ScoreComponentHandler#setTimeSignatureDenomenator`, `ScoreComponentHandler#setRhythmLengthHintsetLeftDecoration`, `ScoreComponentHandler#setRightDecoration` - The optional `linkId` is null for this event was done to this component, or is a local id of the component that this was done to. The refered to `linkId` will always have first been added through `ScoreComponentHandler#addLink`.   
`ScoreComponentHandler#addLink` - This should create a new local component with the same initial values as it would have from `Handler#addComponent`.  
`ScoreComponentHandler#addLink`, `ScoreComponentHandler#addBeat`, `ScoreComponentHandler#removeBeat`, `ScoreComponentHandler#addToggles`, `ScoreComponentHandler#removeToggles`, `ScoreComponentHandler#setX`, `ScoreComponentHandler#setY`, `ScoreComponentHandler#setTimeSignatureDenomenator`, `ScoreComponentHandler#setRhythmLengthHintsetLeftDecoration`, `ScoreComponentHandler#setRightDecoration` - The copy of this component should be stored locally. The linkId is arbitary, and may not be a real id, however it will be kept constant for between being added and removed for a given `ScoreComponentHandler`.  

## Some general rules
Component's handlers are expected to keep track of all the data that they need. This means they should store their own copy (either in JS or in HTML) of the current data. Component's handlers should not communicate with oneanother, but should act only on the data that they themselves store.  
The handlers event functions will be called in an order that the changes are made. A handler's internal state should be consistant with itself before and after an event function is called, however during the call it may be inconsistant. When a frame is drawn, the handler's should have got everything consistant with the `StateManager`.  
When the user tells the editor to update a component, the editor should not yet make any changes. Instead it tells the `StateManager` what it wants done. The `StateManager` can then tell the editor and render the changes that have been made.  

## Examples so you can understand better
### Project loading process:
1.
```
index.html:
  Creates `StateManager` with functions to create `Handler`s from `renderer.js` and `editor.js`.
StateManager:
	Calls functions to create given handlers, with self as only arg.
	Saves these into itself.
```
2.
```
index.html:
StateManager:
	For each component:
		Calls `Handler#addComponent`.
		If component is a text-component:
			Call `setText` and `setFontSize` on `Handler#getComponentHandler(...)`.
		If component is a score-component:
			Call `addBeat` and `addToggles` on `Handler#getComponentHandler(...)` for each beat and toggle-type respectively.
			Call `setX`, `setY`, `setTimeSignatureDenomenator`, `setRhythmLengthHint` and `setLeftDecoration`, `setRightDecoration` on `Handler#getComponentHandler(...)`.
			For each subdivision and toggle-type:
				Call `Handler#getComponentHandler(...).getToggleHandler(...).setState`.
		For each score-component:
			For each score-component that is linked to the first:
				Call `Handler#getComponentHandler(...).getToggleHandler(...).addLink` with some arbitary id.
				Call all the setters to make this local copy of the component consistant with what it should be.
renderer.js, editor.js:
	Caches or handles events as they come through.
	Handling can mean building a local copy of the component data, or drawing it, or disgarding the event if we don't need it.
```
3.
```renderer.js, editor.js:
	Just before the frame is drawn, handle any cached events. Some events may be able to consume others (if their outcome is the same then only run one, etc.).
```

### Score-component addition process:
1.
```
index.html:
	This calls `StateManager#createEmptyComponent` with select true.
```
2.
```
StateManager:
	Creates an empty component of the corrent type internally. StateManager decides most default values.
	Calls `Handler#addComponent`.
	Call the setters functions with the default values.
	Call `ScoreComponentHandler#setSelect` on other selected components to deselect them.
	Call `ScoreComponentHandler#setSelect` on this to select it.
```

### Score-component deletion process:
1.
```
index.html:
	This calls `StateManager#removeComponent`.
```
2.
```
StateManager:
	Call `ScoreComponentHandler#removeLink` on all linked score-components.
	Remove links internally.
	If it is selected:
		Call `ScoreComponentHandler#setSelect` to deselect it.
	Call `Handler#removeComponent`.
	Remove the component internally.
```

### Score-component score-content modification process:
1.
```
ScoreComponentToggleHandler:
	This calls `StateManager#setToggleState` with the beatI, subdivisionI, toggleId and the desired state.
	This does not update its state.
```
2.
```
StateManager:
	Update state internally.
	Call `ScoreComponentToggleHandler#setState`.
	Call `ScoreComponentToggleHandler#setState` on all linked score-components.
```

## Key
`(S)` - Some subclass.
`someArg...` - Vararg.
