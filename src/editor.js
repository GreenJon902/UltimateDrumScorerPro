import {getScoreComponentBaseSubdivisions, getScoreComponentEnabledDecorations, getScoreComponentEnabledDrums, setScoreComponentTimeSignatureNumerator, setScoreComponentTimeSignatureDenominator, getScoreComponentFurtherSubdivisionCount, getScoreComponentFurtherSubdivisionDecoration, getScoreComponentFurtherSubdivisionDrum, getScoreComponentTimeSignatureDenominator, getScoreComponentTimeSignatureNumerator, setScoreComponentFurtherSubdivisionCount, setScoreComponentFurtherSubdivisionDecoration, setScoreComponentFurtherSubdivisionDrum, setScoreComponentBaseSubdivisions} from "./files.js";
import {renderComponent} from "./rendered.js";

export function setEditComponent(componentType, componentID) {
    // Set the component editing pane to be editing the given component.
    
    // First clear the old data
    let editor = document.getElementById("editor-pane");
    while (editor.children.length > 0) {
        editor.removeChild(editor.children[0]);
    }

    if (componentType !== "score-component") throw "Not Implemented";
    
    // Score-component options
    const div = document.createElement("div");
    createNumberBoxesWithText(div, componentID, 
        {text: "Time Signature:&nbsp;", getter: getScoreComponentTimeSignatureNumerator, setter: setScoreComponentTimeSignatureNumerator, min: 1, size: 2}, 
        {text: "&nbsp;/&nbsp;", getter: getScoreComponentTimeSignatureDenominator, setter: setScoreComponentTimeSignatureDenominator, min: 1, size: 2}
    );
    createNumberBoxesWithText(div, componentID, {text: "Base Subdivisions:&nbsp;", getter: getScoreComponentBaseSubdivisions, setter: setScoreComponentBaseSubdivisions, min: 1, size: 2});
    editor.appendChild(div);
    

    // Sequencer ----
    // We'll display the sequencer as a table and add it to the editor.
    const table = document.createElement("table");
    table.classList.add("editor-sequencer-table");
    table.appendChild(scoreEditorCreateSequencerFurtherSubdivisionControlsTr(componentID));
    createSpacingTableRow(table, ["editor-sequencer-subdivision-decoration-divider"]);
    scoreEditorAddSequencerContents(table, componentID, getScoreComponentEnabledDecorations, getScoreComponentFurtherSubdivisionDecoration, setScoreComponentFurtherSubdivisionDecoration, ["editor-sequencer-toggle", "editor-sequencer-toggle-decoration"]);
    createSpacingTableRow(table, ["editor-sequencer-decoration-drum-divider"]);
    scoreEditorAddSequencerContents(table, componentID, getScoreComponentEnabledDrums, getScoreComponentFurtherSubdivisionDrum, setScoreComponentFurtherSubdivisionDrum, ["editor-sequencer-toggle", "editor-sequencer-toggle-drum"]);
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


function createNumberBoxesWithText(div, componentID, ...boxes) {
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
        const input = document.createElement("input");
        input.classList.add("score-sequencer-option-box");
        input.value = boxes[i].getter(componentID);
        input.inputMode = "numeric";
        input.min = boxes[i].min;
        input.size = boxes[i].size;
        // Bind the update event to call the functions and do validation
        input.oninput = () => {
            input.value = input.value.replace(/[^0-9]/g, '');  // Ensure only number characters
            if (parseInt(input.value) < boxes[i].min) {  // If below min 
                input.value = boxes[i].min;
            }
        }
        input.onchange = () => {
            if (input.value == '') {  // If empty then set to min
                input.value = boxes[i].min;
            }
            boxes[i].setter(componentID, parseInt(input.value))
            setEditComponent("score-component", componentID);  // Redraw the editor
            renderComponent("score-component", componentID);  // Re-render it in the rendered-pane
        };

        // Add to container
        container.appendChild(span);
        container.appendChild(input);
    }

    // Add container to the div
    div.appendChild(container);
}


function scoreEditorCreateSequencerFurtherSubdivisionControlsTr(componentID) {
    // Creates a table row containing the controls for managing further-subdivisions.
    // It will create a text box for each base-subdivision, with colspan being set to the number of further-subdivisions for formatting.
    // This will then return the table row.
    const tableRow = document.createElement("tr");
    tableRow.append(document.createElement("th"));  // The first column is just descriptors of each drum

    const baseSubdivisions = getScoreComponentBaseSubdivisions(componentID);
    const numberOfBaseSubdivisions = getScoreComponentTimeSignatureNumerator(componentID) * baseSubdivisions;
    for (let baseSubdivisionIndex = 0; baseSubdivisionIndex < numberOfBaseSubdivisions; baseSubdivisionIndex++) {
        const tableData = document.createElement("td");
        const furtherSubdivisionCount = getScoreComponentFurtherSubdivisionCount(componentID, baseSubdivisionIndex);
        tableData.colSpan = furtherSubdivisionCount;  // Because we have a column of sequencer toggles for each further subdivision
        tableData.classList.add("editor-sequencer-further-subdivision-control");
        const textBox = document.createElement("input");
        textBox.classList.add("editor-sequencer-further-subdivision-control");
        textBox.type = "number";
        textBox.min = 1;
        textBox.value = furtherSubdivisionCount;
        textBox.onchange = () => {
            setScoreComponentFurtherSubdivisionCount(componentID, baseSubdivisionIndex, parseInt(textBox.value));  // Save the new value
            setEditComponent("score-component", componentID);  // Redraw the editor
            renderComponent("score-component", componentID);  // Re-render it in the rendered-pane
        };
        tableData.appendChild(textBox);
        tableRow.appendChild(tableData);

        // Add spacing if required
        if ((baseSubdivisionIndex + 1) % baseSubdivisions == 0 && baseSubdivisionIndex + 1 != numberOfBaseSubdivisions) {  // If end of beat but not after very last beat
            createSpacingTableData(tableRow, "editor-sequencer-beat-divider");
        }
    }

    return tableRow;
}

function scoreEditorAddSequencerContents(table, componentID, idGetter, isCheckedGetter, isCheckedSetter, classNames) {
    // Adds the toggle buttons for the sequencer to a table.
    // You supply functions idGetter and isCheckedGetter and isCheckedSetter depending if this is drums or decorations.
    //    idGetter(componentID) -> String list of IDs.
    //    isCheckedGetter(componentID, baseSubdivisionIndex, furtherSubdivisionIndex, ID) -> Is this drum / decoration hit on this specific subdivision.  The given ID is the id of the drum / decoration
    //    isCheckedSetter(componentID, baseSubdivisionIndex, furtherSubdivisionIndex, ID, checked)    Sets whether or not a given drum / decoration is set on a given subdivision. The id is the id of the drum / decoration.
    // The given classNames will be given to the toggle buttons (and their td containers).
    
    const IDs = idGetter(componentID);
    const baseSubdivisions = getScoreComponentBaseSubdivisions(componentID);
    const numberOfBaseSubdivisions = getScoreComponentTimeSignatureNumerator(componentID) * baseSubdivisions;
    for (let index = 0; index < IDs.length; index++) {
        const ID = IDs[index];

        // Create row and row header
        const tableRow = document.createElement("tr");
        const symbolID = document.createElement("th");
        symbolID.innerText = ID;
        tableRow.appendChild(symbolID);

        // Add the actual buttons
        for (let baseSubdivisionIndex = 0; baseSubdivisionIndex < numberOfBaseSubdivisions; baseSubdivisionIndex++) {
            const numberOfFurtherSubdivisions = getScoreComponentFurtherSubdivisionCount(componentID, baseSubdivisionIndex);
            for (let furtherSubdivisionIndex = 0; furtherSubdivisionIndex < numberOfFurtherSubdivisions; furtherSubdivisionIndex++) {
                // Create the actual button and add it to the table
                const enabled = isCheckedGetter(componentID, baseSubdivisionIndex, furtherSubdivisionIndex, ID);
                const tableData = scoreEditorCreateSequencerToggleButtonInTd(numberOfFurtherSubdivisions, enabled, classNames, isCheckedSetter, baseSubdivisionIndex, furtherSubdivisionIndex, ID, componentID);
                tableRow.appendChild(tableData);
            }
            
            // Add spacing if required
            if ((baseSubdivisionIndex + 1) % baseSubdivisions == 0 && baseSubdivisionIndex + 1 != numberOfBaseSubdivisions) {  // If end of beat but not after very last beat
                createSpacingTableData(tableRow, "editor-sequencer-beat-divider");
            }

        }

        // Add table row to table
        table.appendChild(tableRow);
    }
}

function scoreEditorCreateSequencerToggleButtonInTd(furtherSubdivisionCount, enabled, classNames, isCheckedSetter, baseSubdivisionIndex, furtherSubdivisionIndex, ID, componentID) {
    // Create a toggle button to be used in the editor for the actual score (turning drums on and off).
    // This returns a table data element with the correct width based of the furtherSubdivisionCount.
    // If enabled is true then it will be checked by default.
    // The classes in classNames will be given to both the input and the td.
    // The function isCheckedSetter(componentID, baseSubdivisionIndex, furtherSubdivisionIndex, ID, checked) is used when we toggle the checkbox. The id is the id of the drum / decoration.
    // The given ID is the ID of the drum / decoration.
    const tableData = document.createElement("td");
    const toggleButton = document.createElement("input");
    toggleButton.type = "checkbox";
    tableData.classList.add(...classNames);
    toggleButton.classList.add(...classNames);
    toggleButton.checked = enabled;
    toggleButton.onclick = () => {
        isCheckedSetter(componentID, baseSubdivisionIndex, furtherSubdivisionIndex, ID, toggleButton.checked);  // Save the new value
        renderComponent("score-component", componentID);  // Re-render it in the rendered-pane
    };
    tableData.style.width = (3 / furtherSubdivisionCount) + 'em';
    tableData.appendChild(toggleButton);
    return tableData;
}
