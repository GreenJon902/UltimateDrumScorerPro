import {getScoreComponentEnabledDrums, setScoreComponentTimeSignatureNumerator, getScoreComponentEnabledDecoration, setScoreComponentEnabledDecoration, linkScoreComponents, setScoreComponentTimeSignatureDenominator, getScoreComponentTimeSignatureDenominator, getScoreComponentEnabledDrum, setScoreComponentEnabledDrum, getScoreComponentTimeSignatureNumerator, getScoreComponentBeatSubdivisionCount, setScoreComponentBeatSubdivisionCount, getScoreComponentBeatSubdivisionDrum, setScoreComponentBeatSubdivisionDrum, getTextComponentFontSize, setTextComponentFontSize, setTextComponentTextContent, getTextComponentTextContent, getScoreComponentRhythmLengthHint, setScoreComponentRhythmLengthHint, getScoreComponentEnabledDecorations, getScoreComponentBeatSubdivisionDecoration, setScoreComponentBeatSubdivisionDecoration, getScoreComponentBeatSubdivisionDecorations, getScoreComponentBeatSubdivisionDrums, getScoreComponentLeftDecoration, setScoreComponentLeftDecoration, getScoreComponentRightDecoration, setScoreComponentRightDecoration, removeScoreComponent, duplicateScoreComponent, setComponentX, getComponentX, setComponentY, getComponentY, isScoreComponentLinked, removeScoreComponentFromLink, getLinkedToScoreComponent} from "./files.js";
import {addCurrentSelected, getCurrentSelected, getSvgNodes, renderComponent, setCurrentSelected, unRenderComponent} from "./rendered.js";

function clearEditorPane() {
    // Removes all nodes from the "editor-pane".
    let editor = document.getElementById("editor-pane");
    while (editor.children.length > 0) {
        editor.removeChild(editor.children[0]);
    }
}

export function setEditComponent(componentType, componentID, doSetCurrentSelected=true) {
    // Set the component editing pane to be editing the given component.
    // This will call rendered.js/setCurrentSelected if doSetCurrentSelected is true, and expects the component to have been rendered.
    // If both args are "" then the editor will be cleared, setCurrentSelected called (if doSetCurrentSelected is true) with ("", ""),  and then the function will return.
    
    // First clear the old data
    clearEditorPane();
    
    // Tell the renderer to display the given component as selected (if needed)
    if (doSetCurrentSelected) setCurrentSelected(componentType, componentID);
    
    // Special case: if componentType, componentID == "" then just exit
    if (componentType === "" && componentID === "") {
        return;
    }

    // Render new editor
    const editFunc = {
        "score-component": editScoreComponent,
        "text-component": editTextComponent
    }[componentType];

    if (editFunc === undefined) throw "Not Implemented";
    editFunc(componentID);
}

export function setEditComponents(components) {
    // Set up the editing pane for the given componentIDs, or clear it if there is an invalid combination.
    // components should be of the form [{componentType, componentID}].
    
    clearEditorPane();
    
    // At the moment the only valid option is setting up a link
    if (components.filter(c => c.componentType === "score-component").length != components.length) {  // Check if all given components are score-components
        return;
    }
    // Create UI:
    document.getElementById("editor-pane").appendChild(createButton(
        "Link Vertically",
        () => {
            linkScoreComponents(components.map(c => c.componentID));  // This may affect any other score components that used to be linked to a current selected, so re-render all next
            renderComponent("score-component", components[0].componentID);  // This will trigger the re-rendering of them all
        }
    ));
}

function editTextComponent(componentID) {
    // Set up the editor to be editing the given component.
    let editor = document.getElementById("editor-pane");
    
    // Text-component options
    const div = document.createElement("div");
    createNumberBoxesWithText(div, "text-component", componentID, {text: "Font Size:&nbsp", getter: getTextComponentFontSize, setter: setTextComponentFontSize, min: 1, size: 1});
    editor.appendChild(div);
    
    // Duplicate / delete controls
    div.appendChild(document.createElement("br"))
    createComponentDelDupButtons(div, "text-component", componentID);


    // Actual text content
    const text = document.createElement("textarea");
    text.classList.add("text-component-text-content");
    text.oninput = function () {
        setTextComponentTextContent(componentID, text.value);
        renderComponent("text-component", componentID);
    }
    text.value = getTextComponentTextContent(componentID);
    editor.appendChild(text);
}
    
function editScoreComponent(componentID) {
    // Set up the editor to be editing the given component.
    let editor = document.getElementById("editor-pane");

    // Score-component options
    const div = document.createElement("div");
    createNumberBoxesWithText(div, "score-component", componentID, 
        {text: "Time Signature:&nbsp;", getter: getScoreComponentTimeSignatureNumerator, setter: setScoreComponentTimeSignatureNumerator, min: 1, size: 2}, 
        {text: "&nbsp;/&nbsp;", getter: getScoreComponentTimeSignatureDenominator, setter: setScoreComponentTimeSignatureDenominator, min: 1, size: 2}
    );
    createNumberBoxesWithText(div, "score-component", componentID, 
        {text: "Rhythm Length Hint:&nbsp;", getter: getScoreComponentRhythmLengthHint, setter: setScoreComponentRhythmLengthHint, min: 0, size: 2}, 
    );
    
    // Score-component side-decorations
    addSideDecorationSelectors(div, componentID);
    
    // Duplicate / delete controls
    div.appendChild(document.createElement("br"))
    createComponentDelDupButtons(div, "score-component", componentID);
    
    // Link controls
    if (isScoreComponentLinked(componentID)) {  // We only need these if it's linked
        div.appendChild(document.createElement("br"))
        
        // Add a button to remove from link, and button to select all in current link group
        div.appendChild(createButton("Remove From Link", () => {
            removeScoreComponentFromLink(componentID);  // Remove from file manager
            setEditComponent("score-component", componentID);  // Update the edit pane
            renderComponent("score-component", componentID);  // This will trigger the re-rendering of them all in the old group
        }));
        div.appendChild(createButton("Select All In Link", () => {
            setCurrentSelected("", "");  // Remove all current selected
            getLinkedToScoreComponent(componentID).forEach(id => addCurrentSelected("score-component", id));  // Add each item that should be selected
            setEditComponents(getCurrentSelected()); // Update editor. There must be multiple selected right now
        }));
    }

    // Selectors for which drums and decorations are enabled
    div.appendChild(document.createElement("br"));
    const selectorsText = document.createElement("span");
    selectorsText.innerHTML = "Enabled Decorations/Drums:";
    div.appendChild(selectorsText);
    
    const selectorsDiv = document.createElement("div");
    selectorsDiv.classList.add("editor-selectors-container");
    const decorationIDs = getSvgNodes("decorations").array.map(node => node.id);
    selectorsDiv.appendChild(createIDSelector(componentID, decorationIDs, id => getScoreComponentEnabledDecoration(componentID, id), (id, value) => setScoreComponentEnabledDecoration(componentID, id, value)));

    const drumIDs = getSvgNodes("drums").array.map(node => node.id);
    selectorsDiv.appendChild(createIDSelector(componentID, drumIDs, id => getScoreComponentEnabledDrum(componentID, id), (id, value) => setScoreComponentEnabledDrum(componentID, id, value)));


    div.appendChild(selectorsDiv);
    
    // Add div of controls to editor
    editor.appendChild(div);

    // Sequencer ----
    // We'll display the sequencer as a table and add it to the editor.
    const table = document.createElement("table");
    table.classList.add("editor-sequencer-table");
    table.appendChild(scoreEditorCreateSequencerBeatSubdivisionControlsTr(componentID));
    createSpacingTableRow(table, ["editor-sequencer-subdivision-decoration-divider"]);
    scoreEditorAddSequencerContents(table, componentID, (componentID) => {
        const enabledIDs = getScoreComponentEnabledDecorations(componentID);
        return getSvgNodes("decorations").array  // Filter and map this so are ordered correctly
            .map(node => node.id)
            .filter(id => enabledIDs.includes(id));
    }, getScoreComponentBeatSubdivisionDecoration, setScoreComponentBeatSubdivisionDecoration, ["editor-sequencer-toggle", "editor-sequencer-toggle-decoration"], (componentID, beatIndex, subdivisionIndex, decorationID) => (getScoreComponentBeatSubdivisionDrums(componentID, beatIndex, subdivisionIndex).length === 0));
    createSpacingTableRow(table, ["editor-sequencer-decoration-drum-divider"]);
    scoreEditorAddSequencerContents(table, componentID, (componentID) => {
        const enabledIDs = getScoreComponentEnabledDrums(componentID);
        return getSvgNodes("drums").array  // Filter and map this so are ordered correctly
            .map(node => node.id)
            .filter(id => enabledIDs.includes(id));
    }, getScoreComponentBeatSubdivisionDrum, (componentID, beatIndex, subdivisionIndex, drumID, checked) => {
        const currentUsedDecorations = getScoreComponentBeatSubdivisionDecorations(componentID, beatIndex, subdivisionIndex);  // Save for if we need it
        const wereDecorationsRemoved = setScoreComponentBeatSubdivisionDrum(componentID, beatIndex, subdivisionIndex, drumID, checked);  // Actually set the value
        
        // If no drums are being used on this subdivison then we're not allowed any subdivisions
        if (wereDecorationsRemoved) {
            // Decorations were removed in the file manager so we need to update the buttons
            for (let i=0; i<currentUsedDecorations.length; i++) {
                document.getElementById(sequencerToggleID(beatIndex, subdivisionIndex, currentUsedDecorations[i])).checked = false;
            }
        }
        
        // Disable or enable the buttons as required
        const shouldBeDisabled = getScoreComponentBeatSubdivisionDrums(componentID, beatIndex, subdivisionIndex).length === 0;
        const enabledDecorations = getScoreComponentEnabledDecorations(componentID);
        for (let i=0; i<enabledDecorations.length; i++) {
            document.getElementById(sequencerToggleID(beatIndex, subdivisionIndex, enabledDecorations[i])).disabled = shouldBeDisabled;
        }
    }, ["editor-sequencer-toggle", "editor-sequencer-toggle-drum"], (componentID, beatIndex, subdivisionIndex, drumID) => false);  
    editor.appendChild(table);
}

function createButton(text, click) {
    // Creates and returns a div containing a button with the given text with the given function (which takes no args) put in .onclick.
    // It returns a div so that buttons will stack on top of eachother.
    const div = document.createElement("div");
    const button = document.createElement("button");
    button.innerHTML = text;
    button.onclick = click;
    div.appendChild(button);
    return div;
}

function createComponentDelDupButtons(div, componentType, componentID) {
    // Adds the duplicate and delete buttons to the given div
    div.appendChild(createButton("Delete", () => {
        setEditComponent("", "");
        unRenderComponent(componentType, componentID);
        removeScoreComponent(componentType, componentID);  // Has to be after unRender as per doc
        
    }));
    div.appendChild(createButton("Duplicate", () => {
        const newID = duplicateScoreComponent(componentType, componentID);
        // Translate the new one a little so we can see it
        setComponentX(componentType, newID, getComponentX(componentType, newID) + 0.1);
        setComponentY(componentType, newID, getComponentY(componentType, newID) + 0.1);
        // Render it
        renderComponent(componentType, newID);
        setEditComponent(componentType, newID);
    }));

}

function addSideDecorationSelectors(div, componentID) {
    // Add the side-decoration selectors for the given component to the given div. 
    div.appendChild(createSideDecorationSelector("left", 
        () => getScoreComponentLeftDecoration(componentID), 
        (value) => {
            setScoreComponentLeftDecoration(componentID, value);
            renderComponent("score-component", componentID);
        }
    ));
    div.appendChild(createSideDecorationSelector("right", 
        () => getScoreComponentRightDecoration(componentID), 
        (value) => {
            setScoreComponentRightDecoration(componentID, value);
            renderComponent("score-component", componentID);
        }
    ));
}

function createSideDecorationSelector(side, getter, setter) {
    // Creates and returns a div with a fully working option selector for a given side's decorations.
    // The from getSvgNodes("side-decorations") should have a data-side="left" or "right".
    // The getter takes no arguements and returns the string id of the decoration. The setter takes the arguement of the id of the new decoration.

    const options = getSvgNodes("side-decorations");
    const currentSelected = getter();
    
    // Create and add nodes
    const div = document.createElement("div");
    const text = document.createElement("span");
    text.innerHTML = side + " Decoration: ";
    const select = document.createElement("select");
    ["",  // Insert a 'none-selected' option at the start
        ...options.array
            .filter(node => node.dataset.side === side)
            .map(node => node.id)
    ]          .forEach(optionName => {  // Add nodes for each option
            const option = document.createElement("option");
            option.value = optionName;
            option.innerHTML = optionName;
            option.selected = currentSelected === optionName;
            select.appendChild(option);
    });
    div.appendChild(text);
    div.appendChild(select);

    // Attach bindings
    select.onchange = () => setter(select.value);
    
    // Return div
    return div;
}

function createIDSelector(componentID, idList, getter, setter) {
    // Creates a bunch of check boxes labled with the given IDs. It uses the getter and setter to see/set if they are enabled.
    //  idList: [string].
    //  getter(id: str) -> boolean.
    //  setter(id: str, value: boolean).
    // Returns a container table.
    
    const container = document.createElement("table");
    for (let i=0; i<idList.length; i++) {
        // Create the text to go beforehand
        const span = document.createElement("span");
        span.innerHTML = idList[i];
        span.style.textWrap = "nowrap";
        
        // Create the checkbox
        const input = document.createElement("input");
        input.type = "checkbox";
        input.checked = getter(idList[i]);
        input.onclick = function () {
            setter(idList[i], input.checked);
            setEditComponent("score-component", componentID);  // Redraw editor
            renderComponent("score-component", componentID);  // Because disabling a line may have removed (e.g.) a drum that was played on that line so the score has changed
        }
        
        // Create row and add to container
        const row = document.createElement("tr");
        const td1 = document.createElement("td");
        const td2 = document.createElement("td");
        td1.appendChild(span);
        td2.appendChild(input);
        row.appendChild(td1);
        row.appendChild(td2);
        container.appendChild(row);
    }
    
    return container;
}

function sequencerToggleID(beatIndex, subdivisionIndex, ID) {
    // Returns the ID to give to the input node for a given drum / decoration with the given ID.
    return `editor-sequencer-toggle-${beatIndex}-${subdivisionIndex}-${ID}`;
}

function createSpacingTableRow(table, classNames) {
    // Create an row with the given CSS classes and add it to the table.
    // The given classNames should be an array of strings.
    const tr = document.createElement("tr");
    tr.classList.add(...classNames);
    table.appendChild(tr);
}

function createSpacingTableData(row, classNames) {
    // Create a data node with the given CSS classes and add it to the row.
    // The given classNames should be an array of strings.
    const td = document.createElement("td");
    td.classList.add(...classNames);
    row.appendChild(td);
}


function createNumberBoxesWithText(div, componentType, componentID, ...boxes) {  // TODO: Only redraw if we have to
    // Creates a (or multiple) input fields that have some text beforehand.
    // These will validate to only allow numbers above a certain value to be entered. When calling the setter, this will have already parsed the integer.
    // The boxes should be objects with this format {text: String, type: String, getter: Callable<componentID>, setter: Callable<componentID, value: int>, min: int, size: int}.
    //      Text is what to display before the box.
    //      Type should be "text" or "number".
    //      The getter and setters should be functions that take the arguements as described, the getter returning the initial value to put in the box.
    //      Min is the minimum value.
    //      Size is width to draw the text box
    // Boxes drawn at the same time will all be put on the same line, contained within a div which will be added to the end of the given div.
    // Boxes are given the class css class score-sequencer-option-box.
    
    // Contain within a flex-div so it's all on one line 
    const container = document.createElement("div");
    container.style.display = "flex";

    // Create all the boxes and add them to the container 
    for (let i=0; i<boxes.length; i++) {
        // Create the text to go beforehand
        const span = document.createElement("span");
        span.innerHTML = boxes[i].text;
        span.style.textWrap = "nowrap";
        
        // Create the input field
        const input = createValidatedIntegerInput(() => {
            return boxes[i].getter(componentID);
        }, (value) => {
            boxes[i].setter(componentID, value);
            setEditComponent(componentType, componentID);  // Redraw the editor
            renderComponent(componentType, componentID);  // Re-render it in the rendered-pane

        }, ["score-sequencer-option-box"], boxes[i].min, boxes[i].size);

        // Add to container
        container.appendChild(span);
        container.appendChild(input);
    }

    // Add container to the div
    div.appendChild(container);
}

function createValidatedIntegerInput(getter, setter, classes, min, size) {
    // Returns an input node
    // Getter is used for the default value, it takes no arguements.
    // Setter is used to set the value, it takes the new value as an integer.
    // Classes are the css classes to add, this should be a string list.
    // Min is the minimum allowed value.
    // Size is an optional value for the width of the box
    
    // Create the input field
    const input = document.createElement("input");
    input.classList.add(...classes);
    input.value = getter();
    input.inputMode = "numeric";
    input.min = min;
    if (size != null) {
        input.size = size;
    }
    // Bind the update event to call the functions and do validation
    input.oninput = () => {
        input.value = input.value.replace(/[^0-9]/g, '');  // Ensure only number characters
        if (parseInt(input.value) < min) {  // If below min 
            input.value = min;
        }
    }
    input.onchange = () => {
        if (input.value == '') {  // If empty then set to min
            input.value = min;
        }
        setter(parseInt(input.value));  // Dispatch event
    };
    
    return input;
}


function scoreEditorCreateSequencerBeatSubdivisionControlsTr(componentID) {
    // Creates a table row containing the controls for managing beat-subdivisions.
    // It will create a text box for each beat, with colspan being set to the number of subdivisions for formatting.
    // This will then return the table row.
    const tableRow = document.createElement("tr");
    tableRow.append(document.createElement("th"));  // The first column is just descriptors of each drum

    const numerator = getScoreComponentTimeSignatureNumerator(componentID);
    for (let bi = 0; bi < numerator; bi++) {  // BI: beatIndex
        const tableData = document.createElement("td");
        const beatSubdivisionCount = getScoreComponentBeatSubdivisionCount(componentID, bi);
        tableData.colSpan = beatSubdivisionCount;  // Because we have a column of sequencer toggles for each beat subdivision
        tableData.classList.add("editor-sequencer-subdivision-control");
        const textBox = createValidatedIntegerInput(() => {
            return beatSubdivisionCount;
        }, (value) => {
            setScoreComponentBeatSubdivisionCount(componentID, bi, value);  // Save the new value
            setEditComponent("score-component", componentID);  // Redraw the editor
            renderComponent("score-component", componentID);  // Re-render it in the rendered-pane

        }, ["editor-sequencer-subdivision-control"], 1, null);
        tableData.appendChild(textBox);
        tableRow.appendChild(tableData);

        // Add spacing if required
        if (bi + 1 != numerator) {  // If not last beat
            createSpacingTableData(tableRow, ["editor-sequencer-beat-divider"]);
        }
    }

    return tableRow;
}

function scoreEditorAddSequencerContents(table, componentID, idGetter, isCheckedGetter, isCheckedSetter, classNames, disabledGetter) {
    // Adds the toggle buttons for the sequencer to a table.
    // You supply functions idGetter and isCheckedGetter and isCheckedSetter depending if this is drums or decorations.
    //    idGetter(componentID) -> String list of IDs.
    //    isCheckedGetter(componentID, beatIndex, subdivisionIndex, ID) -> Is this drum / decoration hit on this specific subdivision.  The given ID is the id of the drum / decoration
    //    isCheckedSetter(componentID, beatIndex, subdivisionIndex, ID, checked)    Sets whether or not a given drum / decoration is set on a given subdivision. The id is the id of the drum / decoration.
    //    disabledGeter(componentID, beatIndex, subdivisionIndex, ID) -> Should the toggle button (input node) be enabled or disabled. True for disabled.
    // The ids will be displayed in the order they are returned from the idGetter.
    // The given classNames will be given to the toggle buttons (and their td containers).
    
    const IDs = idGetter(componentID);
    const numerator = getScoreComponentTimeSignatureNumerator(componentID);
    for (let index = 0; index < IDs.length; index++) {
        const ID = IDs[index];

        // Create row and row header
        const tableRow = document.createElement("tr");
        const symbolID = document.createElement("th");
        symbolID.innerText = ID;
        tableRow.appendChild(symbolID);

        // Add the actual buttons
        for (let bi = 0; bi < numerator; bi++) {  // BI: beatIndex
            const numberOfSubdivisions = getScoreComponentBeatSubdivisionCount(componentID, bi);
            for (let si = 0; si < numberOfSubdivisions; si++) {  // SI: subdivisionIndex
                // Create the actual button and add it to the table
                const enabled = isCheckedGetter(componentID, bi, si, ID);
                const tableData = scoreEditorCreateSequencerToggleButtonInTd(numberOfSubdivisions, enabled, classNames, isCheckedSetter, bi, si, ID, componentID, disabledGetter);
                tableRow.appendChild(tableData);
            }
            // Add spacing if required
            if (bi + 1 != numerator) {  // If not last beat
                createSpacingTableData(tableRow, ["editor-sequencer-beat-divider"]);
            }
        }

        // Add table row to table
        table.appendChild(tableRow);
    }
}

let stateOfLastClickedToggle = null;

function scoreEditorCreateSequencerToggleButtonInTd(subdivisionCount, enabled, classNames, isCheckedSetter, beatIndex, subdivisionIndex, ID, componentID, disabledGetter) {
    // Create a toggle button to be used in the editor for the actual score (turning drums on and off).
    // This returns a table data element with the correct width based of the subdivisionCount.
    // If enabled is true then it will be checked by default.
    // The classes in classNames will be given to both the input and the td.
    // The function isCheckedSetter(componentID, beatIndex, suubdivisonIndex, ID, checked) is used when we toggle the checkbox. The id is the id of the drum / decoration.
    // The given ID is the ID of the drum / decoration.
    // The toggle button (the input node) is given a html id of the form `editor-sequencer-toggle-${beatIndex}-${subdivisionIndex}-${ID}`.
    const tableData = document.createElement("td");
    const toggleButton = document.createElement("input");
    toggleButton.id = sequencerToggleID(beatIndex, subdivisionIndex, ID);
    toggleButton.disabled = disabledGetter(componentID, beatIndex, subdivisionIndex, ID);
    toggleButton.type = "checkbox";
    tableData.classList.add(...classNames);
    toggleButton.classList.add(...classNames);
    toggleButton.checked = enabled;
    
    // We want to set up events such that if I toggle one on then drag the mouse, all the ones I drag over turn on (or are no effect if they are already on)
    function onUpdate() {
        isCheckedSetter(componentID, beatIndex, subdivisionIndex, ID, toggleButton.checked);  // Save the new value
        renderComponent("score-component", componentID);  // Re-render it in the rendered-pane
    }
    toggleButton.onmousedown = (e) => {
        if (e.buttons === 1) {  // So it works for left clicks
            stateOfLastClickedToggle = toggleButton.checked;
            toggleButton.checked = !stateOfLastClickedToggle;
            onUpdate();
        }
    }
    toggleButton.onmouseenter = (e) => {
        if (e.buttons === 1 && stateOfLastClickedToggle !== null) {  // Is left click pressed and did the drag start on a toggle button?
            toggleButton.checked = !stateOfLastClickedToggle;
            onUpdate();
        }
    }
    toggleButton.onclick = (e) => {
        stateOfLastClickedToggle = null; // So drags must originate on a toggle button
        e.preventDefault();  // As we change the state with on-mouse-down, without this the default handler will change the state again
    }
    
    
    
    tableData.style.width = (4 / subdivisionCount) + 'ch';
    tableData.appendChild(toggleButton);
    return tableData;
}
