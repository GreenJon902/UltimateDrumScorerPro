import {ComponentManager} from "./componentManager.js";
import {SelectionManager} from "./selectionManager.js";

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
    
    // Add bindings to COmponentManager to make sure that content in selectors is always representative of the manager's storage
    ["Text", "FontSize", "TimeSignatureDenomenator", "RhythmLengthHint", "LeftDecoration", "RightDecoration"].forEach(field => {
        ComponentManager["onComponent" + field + "Changed"]((componentId, newValue) => componentFieldChanged(editorPane, field, componentId, newValue));
    });
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

function changeWithComponentManager(node, componentId, fieldName) {
    // Marks the given node as needing to be updated when a given component's field is updated.
    // Related to componentFIeldChanged.
    node.dataset.componentManagerBinding = componentId + "_" + fieldName;  // This makes them easily identifiable for the event bindings to update values
}

function componentFieldChanged(editorPane, fieldName, componentId, newValue) {
    // Called when ComponentManager fires an event and we may need to update an option in the editor.
    // Related to changeWithComponentManager.
    editorPane.querySelectorAll("*[data-component-manager-binding=\"" + componentId + "_" + fieldName + "\"]").forEach(node => { node.value = newValue; });
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
    createEditorTextOption(div, componentId, "Font Size", "FontSize", ...POSITIVE_REAL);
    createBreak(div);
    createEditorDeleteDuplicate(div, componentId);
    editorPane.appendChild(div);
    return div;
}

function createEditorDeleteDuplicate(container, componentId) {
    // Creates the delete and duplicate buttons for the given component inside the given container.
    createEditorButton(container, "Delete", () => ComponentManager.removeComponent(componentId));
    createEditorButton(container, "Duplicate", () => {
        const newId = ComponentManager.duplicateComponent(componentId);
        SelectionManager.select(newId);
    });
}

function createEditorButton(container, text, callback) {
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

function createEditorTextOption(container, componentId, label, optionName, cleaner, caster) {
    // Creates and adds nodes to the container for the given option. Label will be displayed to the user. 
    // User input will be passed through the cleaner - func(str) => str. This should, for example, remove all non-numeric characters. But can allow invalid values (like empty or too small values).
    // User input will be passed through the caster before being stored. func(str) => T/undefined. T is the type the ComponentManager takes, or undefined if you want to go back to what it was before.
    // This expects ComponentManager.(get|set)Component<OptionName> and ComponentManager-Component<optionName>Changed to exist.
    // The created node will also be returned.
    
    
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
    changeWithComponentManager(input, componentId, optionName);
    
    // Cerate action option structure
    const inputId = getUniqueId();
    const div = document.createElement("div");
    createEditorOptionLabel(div, label, inputId);
    div.appendChild(input);
    container.appendChild(div);
    return div;
}

function createEditorSelectOption(container, componentId, label, optionName, options) {
    // See createEditorTextOption. This works on <select> nodes though.
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
    changeWithComponentManager(select, componentId, optionName);
    
    // Cerate action option structure
    const inputId = getUniqueId();
    const div = document.createElement("div");
    createEditorOptionLabel(div, label, inputId);
    div.appendChild(select);
    container.appendChild(div);
    return div;
}

function createEditorOptionLabel(container, labelText, id) {
    // Adds a label for the given id.
    
    const label = document.createElement("label");
    label.innerText = labelText + ": ";
    label.for = id;
    container.appendChild(label);
    
    return label;
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
    createEditorTextOption(div, componentId, "Time Signature Denomenator", "TimeSignatureDenomenator", ...POSITIVE_REAL);
    createEditorTextOption(div, componentId, "Rhythm Length Hint", "RhythmLengthHint", ...POSITIVE_REAL);
    createEditorSelectOption(div, componentId, "Left Decoration", "LeftDecoration", ["start", "repeat-start", "option-start"]);  // Get options for a proper source
    createEditorSelectOption(div, componentId, "Right Decoration", "RightDecoration", ["end", "repeat-end", "option-end", "bar-end"]);  // Get options for a proper source
    createBreak(div);
    createEditorDeleteDuplicate(div, componentId);
    container.appendChild(div);
    return div;
}

function getUniqueId() {
    // Gets a unique html id.

    let n = 0;
    while (true) {
        const id = "editor-" + n;
        if (document.getElementById(id) === null) return id;
        n++;
    }
}


