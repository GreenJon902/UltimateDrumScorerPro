export class SelectionManager {
    // See src/README.md for overview of events and methods.
    
    static {
        createEvents(this, "SelectionStateChanged");
    }

    static toggleSelectionState(componentId, multiselect) {
        // Toggles whether the given component is selected. 
        // If multiselect is false then this will deselect all other components.

        // TODO: This
    }

    static select(...componentIds) {
        // Unselects all selected components and selects the given components.
        // If componentIds is empty then this is the same as clearSelection().

        // TODO: This
    }

    static clearSelection() {
        // Unselects all selected components.
        
        // TODO: This
    }
    
    static isSelected(componentId) {
        // Returns true if the given component is currently selected.

        // TODO: This
    }
}
