import {getScoreComponentBaseSubdivisions, getScoreComponentEnabledDecorations, getScoreComponentEnabledDrums, getScoreComponentFurtherSubdivisionCount, getScoreComponentFurtherSubdivisionDecorations, getScoreComponentFurtherSubdivisionDrums, getScoreComponentTimeSignatureNumerator} from "./files.js";

export function editComponent(componentType, componentID) {
    // Set the component editing pane to be editing the given component.
    
    // First clear the old data
    let editor = document.getElementById("editor-pane");
    while (editor.children.length > 0) {
        editor.removeChild(editor.children[0]);
    }

    if (componentType !== "score-component") throw "Not Implemented";
    
    // We'll display the score editor as a table.
    const table = document.createElement("table");
    scoreEditorAddSequencerContents(table, componentID, getScoreComponentEnabledDecorations, getScoreComponentFurtherSubdivisionDecorations, ["editor-sequencer-toggle", "editor-sequencer-toggle-decoration"]);
    const spacer = document.createElement("tr");
    table.appendChild(spacer);
    scoreEditorAddSequencerContents(table, componentID, getScoreComponentEnabledDrums, getScoreComponentFurtherSubdivisionDrums, ["editor-sequencer-toggle", "editor-sequencer-toggle-drum"]);
    
    // Now add the table to the actual web page
    editor.appendChild(table);
}

function scoreEditorAddSequencerContents(table, componentID, idGetter, isCheckedGetter, classNames) {
    // Adds the toggle buttons for the sequencer to a table.
    // You supply functions idGetter and isCheckedGetter depending if this is drums or decorations.
    //  idGetter(componentID) -> String list of IDs.
    //  isCheckedGetter(componentID, subdivisionIndex, furtherSubdivisionIndex) -> String list of enabled drums / decoratons.
    // The given classNames will be given to the toggle buttons (and their td containers).
    
    const IDs = idGetter(componentID);
    const numberOfSubdivisions = getScoreComponentTimeSignatureNumerator(componentID) * getScoreComponentBaseSubdivisions(componentID);
    for (var index = 0; index < IDs.length; index++) {
        const ID = IDs[index];

        // Create row and row header
        const tableRow = document.createElement("tr");
        const symbolID = document.createElement("th");
        symbolID.innerText = ID;
        tableRow.appendChild(symbolID);

        // Add the actual buttons
        for (var subdivisionIndex = 0; subdivisionIndex < numberOfSubdivisions; subdivisionIndex++) {
            const numberOfFurtherSubdivisions = getScoreComponentFurtherSubdivisionCount(componentID, subdivisionIndex);
            for (var furtherSubdivisionIndex = 0; furtherSubdivisionIndex < numberOfFurtherSubdivisions; furtherSubdivisionIndex++) {
                // Create the actual button and add it to the table
                const enabled = isCheckedGetter(componentID, subdivisionIndex, furtherSubdivisionIndex).includes(ID);
                const tableData = scoreEditorCreateSequencerToggleButtonInTd(numberOfFurtherSubdivisions, enabled, classNames);
                tableRow.appendChild(tableData);
            }
        }

        // Add table row to table
        table.appendChild(tableRow);
    }
}

function scoreEditorCreateSequencerToggleButtonInTd(furtherSubdivisionCount, enabled, classNames) {
    // Create a toggle button to be used in the editor for the actual score (turning drums on and off).
    // This returns a table data element with the correct width based of the furtherSubdivisionCount.
    // If enabled is true then it will be checked by default.
    // The classes in classNames will be given to both the input and the td.
    const tableData = document.createElement("td");
    const toggleButton = document.createElement("input");
    toggleButton.type = "checkbox";
    tableData.classList.add(...classNames);
    toggleButton.classList.add(...classNames);
    toggleButton.checked = enabled;
    tableData.style.width = (3 / furtherSubdivisionCount) + 'em';
    tableData.appendChild(toggleButton);
    return tableData;
}
