import {ComponentManager} from "./componentManager.js";
import {SelectionManager} from "./selectionManager.js";
import {Symbols} from "./symbols.js";

const POSITIVE_REAL = [
    x => { 
        // CLEANER
        x = x.replace(/[^0-9\.]/g, "");  // Remove non-number characers 
        return x;
    },
    x => {
        // CASTER
        x = x.replace(/[^0-9\.]/g, "");  // Remove non-number characers 
        return (x > 0) ? parseFloat(x) : undefined;  // Check positive and not empty
    }
];
const NON_NEG_REAL = [
    x => { 
        // CLEANER
        x = x.replace(/[^0-9\.]/g, "");  // Remove non-number characers 
        return x;
    },
    x => {
        // CASTER
        x = x.replace(/[^0-9\.]/g, "");  // Remove non-number characers 
        return (x >= 0 && x !== "") ? parseFloat(x) : undefined;  // Check non-neg and not empty
    }
];
const POSITIVE_INT = [
    x => { 
        // CLEANER
        x = x.replace(/[^0-9]/g, "");  // Remove non-number characers 
        return x;
    },
    x => {
        // CASTER
        x = x.replace(/[^0-9]/g, "");  // Remove non-number characers 
        return (x > 0) ? parseInt(x) : undefined;  // Check positive and not empty
    }
];

export function attachEditor(editorPane) {
    // Sets up bindings for the given editorPane to connect it to the various managers.
    // The editorPane should a div and only be used for this.
    
    selectionStateChanged(editorPane);  // Triggers a full redraw, regardless of current state
    
    SelectionManager.onSelectionStateChanged(() => selectionStateChanged(editorPane));
    
    // Add bindings to ComponentManager to make sure that content in selectors is always representative of the manager's storage
    ["Text", "FontSize", "TimeSignatureDenomenator", "RhythmLengthHint", "LeftDecoration", "RightDecoration"].forEach(field => {
        ComponentManager["onComponent" + field + "Changed"]((componentId, newValue) => linkFromComponentManagerCalled(editorPane, "basic", componentId, field, newValue));
    });
    ComponentManager.onComponentVertGroupChanged((before, after) => linkFromComponentManagerCalled(editorPane, "vertGroup", before, after));
    ComponentManager.onComponentDrumEnabledStateChanged((componentId, symbolId, newValue) => linkFromComponentManagerCalled(editorPane, "enabledState", componentId, symbolId, newValue));
    ComponentManager.onComponentDrumEnabledStateChanged((componentId, symbolId, newValue) => linkFromComponentManagerCalled(editorPane, "enabledState", componentId, symbolId, newValue));
    ComponentManager.onComponentDrumToggled((componentId, bi, si, symbolId, newValue) => linkFromComponentManagerCalled(editorPane, "toggle", componentId, bi, si, symbolId, newValue));
    ComponentManager.onComponentDrumEnabledStateChanged((componentId, ..._) => linkFromComponentManagerCalled(editorPane, "redrawSequencer", componentId));
    ComponentManager.onComponentBeatsAdded((componentId, ..._) => linkFromComponentManagerCalled(editorPane, "redrawSequencer", componentId));
    ComponentManager.onComponentBeatsRemoved((componentId, ..._) => linkFromComponentManagerCalled(editorPane, "redrawSequencer", componentId));
    ComponentManager.onComponentSubdivisionsAdded((componentId, ..._) => linkFromComponentManagerCalled(editorPane, "redrawSequencer", componentId));
    ComponentManager.onComponentSubdivisionsRemoved((componentId, ..._) => linkFromComponentManagerCalled(editorPane, "redrawSequencer", componentId));
}

function selectionStateChanged(editorPane, ..._) {
    // Listens to SelectionManager-SelectionStateChanged.
    // This method takes the editorPane node, and ignores any other arguements given.
    
    const currentSelection = SelectionManager.getSelection();

    // Completely redraw the editorPane
    editorPane.innerHTML = "";  // Clear children
    if (currentSelection.size === 0) {
        // No children so leave editor empty
    } else if (currentSelection.size === 1) {
        // 1 child so choose specific editor
        const theComponentId = currentSelection.values().next().value; // Get first value
        const _ = {
            "text-component": createFullTextComponentEditor,
            "score-component": createFullScoreComponentEditor
        }[ComponentManager.getComponentType(theComponentId)](editorPane, theComponentId);
    } else {
        throw "Not implemented"
    }
}

function createLinkFromComponentManager(node, componentId, method, ...args) {
    // Marks the given node to be updated after a certain event from the component manager.
    // These links will only be ran for the given componentId.
    // There are multiple ways (method) the given node can be updated:
    //     "basic": Updates the node's value field with the newValue from the event. Args: FieldName.
    //     "enabledState": Updates the node's checked field depending if this node is in a vertGroup.  Args: SymbolId.
    //     "vertGroup": Adds/removes "display: none;" from the node's style depending whether the symbol is enabled or not. Args:.
    //     "toggle": Updates the node's checked field depending whether that toggle is selected. Args: beatIndex, subdivisionIndex, symbolId
    //     "redrawSequencer": Just redraws the whole sequencer. Args:.
    
    node.dataset.cmLink = "true";
    node.dataset.cmMethod = method;
    node.dataset.cmComponentId = componentId;

    if (method === "basic") {
        node.dataset.cmFieldName = args[0];
    } else if (method === "vertGroup") {
        // No args
    } else if (method === "enabledState") {
        node.dataset.cmSymbolId = args[0]; 
    } else if (method === "toggle") {
        node.dataset.cmBeatIndex = args[0];
        node.dataset.cmSubdivisionIndex = args[1];
        node.dataset.cmSymbolId = args[2];
    } else if (method === "redrawSequencer") {
        // No args
    } else {
        throw "Unknown method"
    }
}

function linkFromComponentManagerCalled(editorPane, method, ...args) {
    // The counterpart for createLinkFromComponentManager - this is what changes the nodes after we recieve an event.
    // Methods:
    //     "basic": Args: componentId, fieldName, newValue.
    //     "vertGroup": Args: oldGroup, newGroup.
    //     "enabledState": Args: componentId, symbolId, newValue.
    //     "toggle": Args: componentId, beatIndex, subdivisionIndex, beatI, newValue.
    //     "redrawSequencer": Args: componentId.
    
    const baseQuery = "*[data-cm-link=\"true\"][data-cm-method=\"" + method + "\"]";

    if (method === "basic") {
        editorPane.querySelectorAll(baseQuery + "[data-cm-component-id=\"" + args[0] + "\"][data-cm-field-name=\"" + args[1] + "\"]").forEach(node => {
            node.value = args[2];
        });
    } else if (method === "vertGroup") {
        const oldS = (args[0] === null) ? new Set() : args[0];
        const newS = (args[1] === null) ? new Set() : args[1];
        oldS.difference(newS).forEach(id => editorPane.querySelectorAll(baseQuery + "[data-cm-component-id=\"" + id + "\"]").forEach(node => node.style.setProperty("display", "none")));
        newS.difference(oldS).forEach(id => editorPane.querySelectorAll(baseQuery + "[data-cm-component-id=\"" + id + "\"]").forEach(node => node.style.removeProperty("display")));
    } else if (method === "enabledState") {
        editorPane.querySelectorAll(baseQuery + "[data-cm-component-id=\"" + args[0] + "\"][data-cm-symbol-id=\"" + args[1] + "\"]").forEach(node => {
            node.checked = args[2];
        });
    } else if (method === "toggle") {
        editorPane.querySelectorAll(baseQuery + "[data-cm-component-id=\"" + args[0] + "\"][data-cm-beat-index=\"" + args[1] + "\"][data-cm-subdivision-index=\"" + args[2] + "\"][data-cm-symbol-id=\"" + args[3] + "\"]").forEach(node => {
            node.dataset.toggleEnabled = args[4];
        })
    } else if (method === "redrawSequencer") {
        editorPane.querySelectorAll(baseQuery + "[data-cm-component-id=\"" + args[0] + "\"]").forEach(node => updateSequencerTableContents(node, args[0]));
    } else {
        throw "Unknown method";
    }
}

function createFullTextComponentEditor(editorPane, componentId) {
    // Creates the editor for the given text component.
    // This assumes the given editorPane is empty.

    createTextEditorOptions(editorPane, componentId);
    createTextEditorTextBox(editorPane, componentId);
}

function createTextEditorTextBox(editorPane, componentId) {
    // Creates the textbox for the given component.
    // This returns the created node as well as adding it to the editorPane.
    
    const textarea = document.createElement("textarea");
    textarea.value = ComponentManager.getComponentText(componentId);
    textarea.onchange = () => {
        ComponentManager.setComponentText(componentId, textarea.value);
    }
    createLinkFromComponentManager(textarea, componentId, "basic", "Text");
    editorPane.appendChild(textarea);
    return textarea;
}

function createTextEditorOptions(editorPane, componentId) {
    // Creates the options for the editor for the given text component.
    // This adds a new child to the given editorPane, and also returns the added child.
    
    const div = document.createElement("div");
    createBasicTextOption(div, componentId, "Font Size", "FontSize", ...POSITIVE_REAL);
    createBreak(div);
    createDeleteDuplicate(div, componentId);
    editorPane.appendChild(div);
    return div;
}

function createDeleteDuplicate(container, componentId) {
    // Creates the delete and duplicate buttons for the given component inside the given container.
    createButton(container, "Delete", () => ComponentManager.removeComponent(componentId));
    createButton(container, "Duplicate", () => {
        const newId = ComponentManager.duplicateComponent(componentId);
        SelectionManager.select(newId);
    });
}

function createVertGroupControls(container, componentId) {
    // Creates the buttons to control an individual components vertical group.
    // This should be called for every score-component, regardless of whether it is currently grouped.
    // This will add the buttons to the container.
    // This will add the args data-only-when-grouped = "componentId", and will have `display: none` set if componentId is not grouped. 
    
    // Create buttons
    const removeButton = createButton(container, "Remove From VertGroup", () => ComponentManager.removeFromVertGroup(componentId));
    const showButton = createButton(container, "Select All In VertGroup", () => SelectionManager.select(...ComponentManager.getVertGroup(componentId)));
    // Add links to component manager
    createLinkFromComponentManager(removeButton, componentId, "vertGroup");
    createLinkFromComponentManager(showButton, componentId, "vertGroup");
    // Hide if necessary
    if (!ComponentManager.isInVertGroup(componentId)) {
        removeButton.style.display = "none";
        showButton.style.display = "none";
    }
}

function createButton(container, text, callback) {
    // Creates a button in container with the given text that calls the given callback.
    // This also returns the button.
    const button = document.createElement("button");
    button.innerText = text;
    button.onclick = callback;
    container.appendChild(button);
    return button
}

function createBreak(container) {
    // Adds a break element to the end of the given node.
    // Also returns the break element.
    const break_ = document.createElement("br");
    container.appendChild(break_);
    return break_;
}

function createBasicTextOption(container, componentId, label, optionName, cleaner, caster) {
    // Creates a text field with a label that corrosponds to a 'first-level' field in a component. E.g. RhythmLengthHint
    //
    // User input will be passed through the cleaner - func(str) => str. This should, for example, remove all non-numeric characters. But can allow invalid values (like empty or too small values).
    // User input will be passed through the caster before being stored. func(str) => T/undefined. T is the type the ComponentManager takes, or undefined if you want to go back to what it was before.
    // This expects ComponentManager.(get|set)Component<OptionName> and ComponentManager-Component<optionName>Changed to exist.
    // The created node will be added, as well as being returned.
    
    
    // Create the input
    const input = document.createElement("input");
    input.size = 2;
    input.value = ComponentManager["getComponent" + optionName](componentId);
    // Event for when user types or removes a character
    input.oninput = () => {
        const cleanedValue = cleaner(input.value);
        input.value = cleanedValue;
    };
    // Event for saving value
    input.onchange = () => {
        let castValue = caster(input.value);
        if (castValue === undefined) {
            castValue = ComponentManager["getComponent" + optionName](componentId);  // Get what it used to be
        }
        input.value = castValue; // Make sure data is consistant
        ComponentManager["setComponent" + optionName](componentId, castValue);
    }
    createLinkFromComponentManager(input, componentId, "basic", optionName);
    
    // Cerate action option structure
    const inputId = getUniqueId();
    input.id = inputId;
    const div = document.createElement("div");
    createOptionLabel(div, label, inputId);
    div.appendChild(input);
    container.appendChild(div);
    return div;
}

function createBasicSelectOption(container, componentId, label, optionName, options) {
    // Creates a <select> field with a label that corrosponds to a 'first-level' field in a component. E.g. RhythmLengthHint
    // 
    // See createBasicTextOption. This works on <select> nodes though.
    // This will add another option for no-selection, which will be null.

    // Create the select
    const select = document.createElement("select");
    ["", ...options].forEach(name => {
        const option = document.createElement("option");
        option.value = name;
        option.innerText = name;
        select.appendChild(option);
    });
    select.value = ComponentManager["getComponent" + optionName](componentId);
    // Event saving value
    select.onchange = () => ComponentManager["setComponent" + optionName](componentId, select.value);
    createLinkFromComponentManager(select, componentId, "basic", optionName);
    
    // Cerate action option structure
    const inputId = getUniqueId();
    select.id = inputId;
    const div = document.createElement("div");
    createOptionLabel(div, label, inputId);
    div.appendChild(select);
    container.appendChild(div);
    return div;
}

function createOptionLabel(container, labelText, id) {
    // Adds a label for the given id. Also returns it.
    
    const label = document.createElement("label");
    label.innerText = labelText + ": ";
    label.htmlFor = id;
    container.appendChild(label);
    
    return label;
}

function createSpan(container, spanText) {
    // Adds a span. Also returns it.
    const span = document.createElement("span");
    span.innerText = spanText;
    container.appendChild(span);
    return span;
}

function createFullScoreComponentEditor(editorPane, componentId) {
    // Creates the options for the editor for the given score component.
    // This adds the widgets to the editorPane, and assumes it is already free of children.
    
    createScoreEditorOptions(editorPane, componentId);
    createScoreEditorSequencer(editorPane, componentId);
}

function createScoreEditorSequencer(container, componentId) {
    // Creates the sequencer for a score-component editor and adds it to the given container. This returns the created node.
    
    const table = document.createElement("table");
    updateSequencerTableContents(table, componentId);
    container.appendChild(table);
    return table;
}

function updateSequencerTableContents(table, componentId) {
    // Recreates the DOM for the given table to be correct for the given componentId.

    const beatCount = ComponentManager.getComponentBeatCount(componentId);

    // Clear all children
    table.innerHTML = "";
    
    // Add row for subdivisions
    {
        const tr = document.createElement("tr");
        tr.appendChild(document.createElement("td"));  // We need an empty top left corner (over symbol names)

        for (let i=0; i<beatCount; i++) {  // i is beatI
            // Create subdivision text box
            const input = document.createElement("input");
            input.value = ComponentManager.getComponentBeatSubdivisionCount(componentId, i);
            input.oninput = () => {
                // Clean input whenever typed
                input.value = POSITIVE_INT[0](input.value);
            }
            const bi = i;  // So doesn't change in lambda.
            input.onchange = () => {
                // Send value to componentManger
                let cast = POSITIVE_INT[1](input.value);
                if (cast === undefined) {
                    cast = ComponentManager.getComponentBeatSubdivisionCount(componentId, i);
                }
                input.value = cast;
                setComponentBeatSubdivisionCount(componentId, bi, cast);
            }
            // We don't need to use createLinkFromComponentManager here, as we will just redraw the whole sequencer from scratch if the structure changes
            
            // Create the containing td node
            const td = document.createElement("td");
            td.colSpan = ComponentManager.getComponentBeatSubdivisionCount(componentId, i);
            td.appendChild(input);
            tr.appendChild(td);
            
            // Create dividing column
            if (i === beatCount - 1) continue // We don't need a divider after the last column
            const divider = document.createElement("td");
            tr.appendChild(divider);
        }
        
        table.appendChild(tr);
    }   
    
    // Add a dividing row
    table.appendChild(document.createElement("tr"));
    
    // Add rows for symbols
    const symbolIds = Symbols.getFullDrumVertOrder().filter(id => ComponentManager.getComponentDrumEnabledState(componentId, id));  // Use full order so we add columns in the correct order
    for (let i=0; i<symbolIds.length; i++) {
        const tr = document.createElement("tr");
        const symbolId = symbolIds[i];

        // Create span with symbol name
        {
            const td = document.createElement("td");
            const span = createSpan(td, symbolId); 
            tr.appendChild(td);
        }
        
        // Create toggles for sequencer
        for (let bi=0; bi<beatCount; bi++) {
            const subdivisionCount = ComponentManager.getComponentBeatSubdivisionCount(componentId, bi);
            for (let si=0; si<subdivisionCount; si++) {
                // Create a td. We can attach events to this, and use data tags to allow css to style it
                const td = document.createElement("td");
                td.dataset.toggleEnabled = ComponentManager.getComponentDrumState(componentId, bi, si, symbolId);
                createLinkFromComponentManager(td, componentId, "toggle", bi, si, symbolId);  // We need this so the tds actually change. We don't redraw everything when a toggle changes
                addSequencerToggleEvents(table, td, componentId, bi, si, symbolId);
                td.style.width = 4 / subdivisionCount + "ch";  // So sizes are consistant with duration. CSS rules then have a minimum width
                tr.appendChild(td);
            }
            
            // Create dividing column
            if (bi === beatCount - 1) continue // We don't need a divider after the last column
            const divider = document.createElement("td");
            tr.appendChild(divider);
        }

        
        table.appendChild(tr);
    }
    
    // When table structure changes just redraw whole table
    createLinkFromComponentManager(table, componentId, "redrawSequencer");
}

function addSequencerToggleEvents(table, td, componentId, bi, si, symbolId) {
    // Adds the events to the given td for the given component where the beat and subdivision indexes are as given, for the given symbolId.
    // The table is used for storing metadata on the click.
    
    // We want to set up events that allow you to drag the mouse over tds to turn them on/off
    // However one drag should only ever turn on or off, not both

    // Toggle first, and figure out if we're toggling on or off
    td.onmousedown = (e) => {
        if (e.buttons !== 1) return;  // Only allow left clicks
        ComponentManager.toggleComponentDrum(componentId, bi, si, symbolId);  // The binding to change the data class is already done
        table.dataset.sequencerCurrentDragNewValue = ComponentManager.getComponentDrumState(componentId, bi, si, symbolId);  // Record this so the rest of the drag only goes to what the first one went to
    }
    // If dragging, update any toggles that are in the incorret state
    td.onmouseenter = (e) => {
        if (e.buttons !== 1) return;  // Only allow left clicks
        const cndv = table.dataset.sequencerCurrentDragNewValue;
        if (cndv !== undefined && ComponentManager.getComponentDrumState(componentId, bi, si, symbolId) !== (cndv === "true")) {
            ComponentManager.toggleComponentDrum(componentId, bi, si, symbolId);  // The binding to change the data class is already done
        }
    }
    // Remove the currentDragNewValue so if the user starts a new drag - from outside the sequencer -, it won't be recorded
    if (!table.hasAttribute("data-drag-mouseup-event-added")) {  // Only add event if this is the first time
        table.setAttribute("data-drag-mouseup-event-added", "");
        document.addEventListener("mouseup", () => {
            table.removeAttribute("data-sequencer-current-drag-new-value");
        });
    }
}


function createScoreEditorOptions(container, componentId) {
    // Creates the options for a score-component editor and adds it to the given container. This returns the created node.
    
    const div = document.createElement("div");
    createTextOption(div, "Time Signature Numerator", POSITIVE_INT[0], ComponentManager.getComponentBeatCount(componentId), value => numeratorBoxChanged(componentId, value)); // TODO: Make link from componentManger to here when number of beats changes
    createBasicTextOption(div, componentId, "Time Signature Denomenator", "TimeSignatureDenomenator", ...POSITIVE_INT);
    createBasicTextOption(div, componentId, "Rhythm Length Hint", "RhythmLengthHint", ...POSITIVE_REAL);
    createTextOption(div, "Set All Subdivisions", POSITIVE_INT[0], "", value => setAllSubdivisionsBoxChanged(componentId, value));
    createBasicSelectOption(div, componentId, "Left Decoration", "LeftDecoration", ["start", "repeat-start", "option-start"]);  // TODO: Get options for a proper source
    createBasicSelectOption(div, componentId, "Right Decoration", "RightDecoration", ["end", "repeat-end", "option-end", "bar-end"]);  // TODO: Get options for a proper source
    createBreak(div);
    createDeleteDuplicate(div, componentId);
    createVertGroupControls(div, componentId);
    createBreak(div);
    createEnabledDrumsOptions(div, componentId);
    container.appendChild(div);
    return div;
}

function createEnabledDrumsOptions(container, componentId) {
    // Creates the checkboxes to select which symbols should be enabled.
    // The created node will be returned, as well as added to the container.
    // Checkboxes will have data-symbol-binding="componentId_symbolId".
    
    // Create the table of checkboxes and labels
    const table = document.createElement("table");
    Symbols.getFullDrumVertOrder().forEach(symbolId => {
        const tr = document.createElement("tr");
        const labelTd = document.createElement("td");
        const boxTd = document.createElement("td");
        const boxId = getUniqueId();
        createOptionLabel(labelTd, symbolId, boxId);
        const box = createCheckboxOption(boxTd, ComponentManager.getComponentDrumEnabledState(componentId, symbolId), () => ComponentManager.toggleComponentDrumEnabledState(componentId, symbolId));
        box.id = boxId;
        createLinkFromComponentManager(box, componentId, "enabledState", symbolId);
        
        tr.appendChild(labelTd);
        tr.appendChild(boxTd);
        table.appendChild(tr);
    });
    
    // Construct node heirarchy
    const div = document.createElement("div");
    createSpan(div, "Enabled Drums:");
    div.appendChild(table);
    container.appendChild(div);
    return div;
}

function setAllSubdivisionsBoxChanged(componentId, value) {
    // Called when the user updates the setAllSubdivisions box in the editor.
    // This returns an empty string.
    
    value = POSITIVE_INT[1](value);
    
    for (let i=0; i<ComponentManager.getComponentBeatCount(componentId); i++) {
        setComponentBeatSubdivisionCount(componentId, i, value);
    }
    
    return "";  // Leave box empty / don't save value
}

function setComponentBeatSubdivisionCount(componentId, beatI, value) {
    // Adds or removes subdivisions from the given component on the given beat so that we have the given amount (`value`).

    const currentSubdivisionCount = ComponentManager.getComponentBeatSubdivisionCount(componentId, beatI);
    
    if (value > currentSubdivisionCount) {
        ComponentManager.addSubdivisions(componentId, beatI, ...Array.from({length: value - currentSubdivisionCount}, (e, i) => i + currentSubdivisionCount));  // Just add to end of beat for now.  TODO: Better way of doing this
    } else if (value < currentSubdivisionCount) {
        ComponentManager.removeSubdivisons(componentId, beatI, ...Array.from({length: currentSubdivisionCount - value}, (e, i) => currentSubdivisionCount - 1 - i)); // Just remove from end for now.  TODO: Better combination to remove
    }
        
    return value;
}

function numeratorBoxChanged(componentId, value) {
    // Called when the user updates the timeSignatureNumerator box in the editor.
    // This returns the cleaned value.

    value = POSITIVE_INT[1](value);  // This is the new beat count
    const currentBeatCount = ComponentManager.getComponentBeatCount(componentId);
    if (value === undefined) return currentBeatCount;
    
    if (value > currentBeatCount) {
        ComponentManager.addBeats(componentId, 1, ...Array.from({length: value - currentBeatCount}, (e, i) => i + currentBeatCount));  // Just add to end of beats for now.  TODO: Better way of doing this. TODO: Adding two subidivisions always doesn't make sense
    } else if (value < currentBeatCount) {
        ComponentManager.removeBeats(componentId, ...Array.from({length: currentBeatCount - value}, (e, i) => currentBeatCount - 1 - i)); // Just remove from end for now.  TODO: Better combination to remove
    }
        
    return value;
}

function createTextOption(container, label, cleaner, currentValue, callback) {
    // Creates a text box with the given label, where input is passed through the cleaner (str => str). When the value is to be saved, the callback is used. The return value of the callback is put inside the text box. CurrentValue is used as the intial value.
    // The created node is added to the container, and also returned.
    
    // Create the input
    const input = document.createElement("input");
    input.value = currentValue;
    input.size = 2;
    // Event for when user types or removes a character
    input.oninput = () => {
        const cleanedValue = cleaner(input.value);
        input.value = cleanedValue;
    };
    // Event for saving value
    input.onchange = () => {
        input.value = callback(input.value); 
    }
    
    // Cerate action option structure
    const inputId = getUniqueId();
    input.id = inputId;
    const div = document.createElement("div");
    createOptionLabel(div, label, inputId);
    div.appendChild(input);
    container.appendChild(div);
    return div;
}

function createCheckboxOption(container, alreadyChecked, callback) {
    // Creates a checkbox which calls the callback(boolean) when modified.
    // AlreadyChecked is the default value.
    
    const input = document.createElement("input");
    input.type = "checkbox";
    input.onclick = callback;
    input.checked = alreadyChecked;
    container.appendChild(input);
    return input;
}

let _createdIds = 0;
function getUniqueId() {
    // Gets a unique html id.
    // No other ids should be of the form "editor-unique-<INT>", else this will break.

    const id = "editor-" + _createdIds;
    _createdIds++;
    return id;
}


