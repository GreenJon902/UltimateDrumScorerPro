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
    ComponentManager.onComponentSymbolEnabledStateChanged((componentId, symbolId, newValue) => linkFromComponentManagerCalled(editorPane, "enabledState", componentId, symbolId, newValue));
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
    
    node.dataset.cmLink = "true";
    node.dataset.cmMethod = method;
    node.dataset.cmComponentId = componentId;

    if (method === "basic") {
        node.dataset.cmFieldName = args[0];
    } else if (method === "vertGroup") {
        // No args
    } else if (method === "enabledState") {
        node.dataset.cmSymbolId = args[0]; 
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
    changeWithComponentManager(textarea, componentId, "Text");
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
    // This adds a new child to the given editorPane, and also returns the added child.
    
    const div = document.createElement("div");
    createScoreEditorOptions(div, componentId);
    editorPane.appendChild(div);
    return div;
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
    createEnabledSymbolsOptions(div, componentId);
    container.appendChild(div);
    return div;
}

function createEnabledSymbolsOptions(container, componentId) {
    // Creates the checkboxes to select which symbols should be enabled.
    // The created node will be returned, as well as added to the container.
    // Checkboxes will have data-symbol-binding="componentId_symbolId".
    
    // Create the table of checkboxes and labels
    const table = document.createElement("table");
    Symbols.getFullOrder().forEach(symbolId => {
        const tr = document.createElement("tr");
        const labelTd = document.createElement("td");
        const boxTd = document.createElement("td");
        const boxId = getUniqueId();
        createOptionLabel(labelTd, symbolId, boxId);
        const box = createCheckboxOption(boxTd, ComponentManager.getComponentSymbolEnabledState(componentId, symbolId), () => ComponentManager.toggleComponentSymbolEnabledState(componentId, symbolId));
        box.id = boxId;
        createLinkFromComponentManager(box, componentId, "enabledState", symbolId);
        
        tr.appendChild(labelTd);
        tr.appendChild(boxTd);
        table.appendChild(tr);
    });
    
    // Construct node heirarchy
    const div = document.createElement("div");
    createSpan(div, "Enabled Symbols:");
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


