import {getScoreComponentBaseSubdivisions, getScoreComponentEnabledDecorations, getScoreComponentEnabledDrums, getScoreComponentFurtherSubdivisionCount, getScoreComponentFurtherSubdivisionDecoration, getScoreComponentFurtherSubdivisionDrum, getScoreComponentTimeSignatureNumerator, setScoreComponentFurtherSubdivisionCount, setScoreComponentFurtherSubdivisionDecoration, setScoreComponentFurtherSubdivisionDrum} from "./files.js";

export function setEditComponent(componentType, componentID) {
    // Set the component editing pane to be editing the given component.
    
    // First clear the old data
    let editor = document.getElementById("editor-pane");
    while (editor.children.length > 0) {
        editor.removeChild(editor.children[0]);
    }

    if (componentType !== "score-component") throw "Not Implemented";
    
    // We'll display the sequencer as a table and add it to the editor.
    const table = document.createElement("table");
    table.appendChild(scoreEditorCreateSequencerFurtherSubdivisionControlsTr(componentID));
    table.appendChild(document.createElement("tr"));  // Spacer
    scoreEditorAddSequencerContents(table, componentID, getScoreComponentEnabledDecorations, getScoreComponentFurtherSubdivisionDecoration, setScoreComponentFurtherSubdivisionDecoration, ["editor-sequencer-toggle", "editor-sequencer-toggle-decoration"]);
    table.appendChild(document.createElement("tr"));  // Spacer
    scoreEditorAddSequencerContents(table, componentID, getScoreComponentEnabledDrums, getScoreComponentFurtherSubdivisionDrum, setScoreComponentFurtherSubdivisionDrum, ["editor-sequencer-toggle", "editor-sequencer-toggle-drum"]);
    editor.appendChild(table);
}

function scoreEditorCreateSequencerFurtherSubdivisionControlsTr(componentID) {
    // Creates a table row containing the controls for managing further-subdivisions.
    // It will create a text box for each base-subdivision, with colspan being set to the number of further-subdivisions for formatting.
    // This will then return the table row.
    const tableRow = document.createElement("tr");
    tableRow.append(document.createElement("td"));  // The first column is just descriptors of each drum

    const numberOfBaseSubdivisions = getScoreComponentTimeSignatureNumerator(componentID) * getScoreComponentBaseSubdivisions(componentID);
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
        };
        tableData.appendChild(textBox);
        tableRow.appendChild(tableData);
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
    const numberOfBaseSubdivisions = getScoreComponentTimeSignatureNumerator(componentID) * getScoreComponentBaseSubdivisions(componentID);
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
    };
    tableData.style.width = (3 / furtherSubdivisionCount) + 'em';
    tableData.appendChild(toggleButton);
    return tableData;
}
