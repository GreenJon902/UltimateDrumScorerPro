import {getScoreComponentEnabledDrums, setScoreComponentTimeSignatureNumerator, setScoreComponentTimeSignatureDenominator, getScoreComponentTimeSignatureDenominator, getScoreComponentTimeSignatureNumerator, getScoreComponentBeatSubdivisionCount, setScoreComponentBeatSubdivisionCount, getScoreComponentBeatSubdivisionDrum, setScoreComponentBeatSubdivisionDrum, getTextComponentFontSize, setTextComponentFontSize, setTextComponentTextContent, getTextComponentTextContent} from "./files.js";
import {renderComponent} from "./rendered.js";

export function setEditComponent(componentType, componentID) {
    // Set the component editing pane to be editing the given component.
    
    // First clear the old data
    let editor = document.getElementById("editor-pane");
    while (editor.children.length > 0) {
        editor.removeChild(editor.children[0]);
    }

    const editFunc = {
        "score-component": editScoreComponent,
        "text-component": editTextComponent
    }[componentType];

    if (editFunc === undefined) throw "Not Implemented";
    editFunc(componentID);
}

function editTextComponent(componentID) {
    // Set up the editor to be editing the given component.
    let editor = document.getElementById("editor-pane");
    
    // Text-component options
    const div = document.createElement("div");
    createNumberBoxesWithText(div, "text-component", componentID, {text: "Font Size:&nbsp", getter: getTextComponentFontSize, setter: setTextComponentFontSize, min: 1, size: 1});
    editor.appendChild(div);

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
    editor.appendChild(div);
    

    // Sequencer ----
    // We'll display the sequencer as a table and add it to the editor.
    const table = document.createElement("table");
    table.classList.add("editor-sequencer-table");
    table.appendChild(scoreEditorCreateSequencerBeatSubdivisionControlsTr(componentID));
    createSpacingTableRow(table, ["editor-sequencer-subdivision-decoration-divider"]);
    //scoreEditorAddSequencerContents(table, componentID, getScoreComponentEnabledDecorations, getScoreComponentBeat, setScoreComponentFurtherSubdivisionDecoration, ["editor-sequencer-toggle", "editor-sequencer-toggle-decoration"]);
    //createSpacingTableRow(table, ["editor-sequencer-decoration-drum-divider"]);
    scoreEditorAddSequencerContents(table, componentID, getScoreComponentEnabledDrums, getScoreComponentBeatSubdivisionDrum, setScoreComponentBeatSubdivisionDrum, ["editor-sequencer-toggle", "editor-sequencer-toggle-drum"]);
    editor.appendChild(table);
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

        }, ["score-sequencer-option-box"], 1, boxes[i].size);

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
            createSpacingTableData(tableRow, "editor-sequencer-beat-divider");
        }
    }

    return tableRow;
}

function scoreEditorAddSequencerContents(table, componentID, idGetter, isCheckedGetter, isCheckedSetter, classNames) {
    // Adds the toggle buttons for the sequencer to a table.
    // You supply functions idGetter and isCheckedGetter and isCheckedSetter depending if this is drums or decorations.
    //    idGetter(componentID) -> String list of IDs.
    //    isCheckedGetter(componentID, beatIndex, subdivisionIndex, ID) -> Is this drum / decoration hit on this specific subdivision.  The given ID is the id of the drum / decoration
    //    isCheckedSetter(componentID, beatIndex, subdivisionIndex, ID, checked)    Sets whether or not a given drum / decoration is set on a given subdivision. The id is the id of the drum / decoration.
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
                const tableData = scoreEditorCreateSequencerToggleButtonInTd(numberOfSubdivisions, enabled, classNames, isCheckedSetter, bi, si, ID, componentID);
                tableRow.appendChild(tableData);
            }
            // Add spacing if required
            if (bi + 1 != numerator) {  // If not last beat
                createSpacingTableData(tableRow, "editor-sequencer-beat-divider");
            }
        }

        // Add table row to table
        table.appendChild(tableRow);
    }
}

function scoreEditorCreateSequencerToggleButtonInTd(subdivisionCount, enabled, classNames, isCheckedSetter, beatIndex, subdivisionIndex, ID, componentID) {
    // Create a toggle button to be used in the editor for the actual score (turning drums on and off).
    // This returns a table data element with the correct width based of the subdivisionCount.
    // If enabled is true then it will be checked by default.
    // The classes in classNames will be given to both the input and the td.
    // The function isCheckedSetter(componentID, beatIndex, suubdivisonIndex, ID, checked) is used when we toggle the checkbox. The id is the id of the drum / decoration.
    // The given ID is the ID of the drum / decoration.
    const tableData = document.createElement("td");
    const toggleButton = document.createElement("input");
    toggleButton.type = "checkbox";
    tableData.classList.add(...classNames);
    toggleButton.classList.add(...classNames);
    toggleButton.checked = enabled;
    toggleButton.onclick = () => {
        isCheckedSetter(componentID, beatIndex, subdivisionIndex, ID, toggleButton.checked);  // Save the new value
        renderComponent("score-component", componentID);  // Re-render it in the rendered-pane
    };
    tableData.style.width = (4 / subdivisionCount) + 'ch';
    tableData.appendChild(toggleButton);
    return tableData;
}
