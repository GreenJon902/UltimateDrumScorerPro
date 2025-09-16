import {createEvents} from "./managerHelpers.js";
import {ComponentManager} from "./componentManager.js";


export class SelectionManager {
    // See src/README.md for overview of events and methods.
    
    static #currentSelection = new Set();
    
    static {
        createEvents(this, "SelectionStateChanged");
    }
    
    static {
        // Deselect selected components when they are being removed
        ComponentManager.onBeforeComponentRemoved(id => {
            if (this.isSelected(id)) this.toggleSelectionState(id, true);
        })
    }

    static toggleSelectionState(componentId, multiselect) {
        // Toggles(ish) whether the given component is selected. 
        // If multiselect is true then the rest of the selection will be unaffected.
        // If multiselect is false then the rest of the selection will be removed, but if there were other things selected then the given component will always be selected afterwards.
        
        if (multiselect) {
            // Toggle just componentId and ignore rest
            if (this.#currentSelection.has(componentId)) {
                this.#currentSelection.delete(componentId);
            } else {
                this.#currentSelection.add(componentId);
            }
            this.dispatchSelectionStateChanged(componentId, this.isSelected(componentId));
            
        } else {
            if (this.#currentSelection.size !== 1) {  // If others are selected then always select componentId (and deselect others). If nothing is selected then select componentId.
                this.select(componentId);  // Handles events
            } else  { // Only 1 is selected
                if (this.isSelected(componentId)) {  
                    // We're toggling the only thing selected so just clear selection
                    this.clearSelection();  // Handles events
                } else {  // Something else is selected
                    // Clear selection and replace it with componentId
                    this.select(componentId);  // Handles events
                }
            }
        }
    }

    static select(...componentIds) {
        // Unselects all selected components and selects the given components.
        // If componentIds is empty then this is the same as clearSelection().

        const lastSelection = this.#currentSelection;  // Save current selection for events
        this.#currentSelection = new Set(componentIds);  // Clear current selection
        
        // Dispatch events to components whose states changed
        lastSelection.difference(this.#currentSelection).forEach(id => this.dispatchSelectionStateChanged(id, false));
        this.#currentSelection.difference(lastSelection).forEach(id => this.dispatchSelectionStateChanged(id, true));
    }

    static clearSelection() {
        // Unselects all selected components.
        this.select();  // Selects none
    }
    
    static isSelected(componentId) {
        // Returns true if the given component is currently selected.
        return this.#currentSelection.has(componentId);
    }
    
    static getSelection() {
        // Returns a frozen set of all selected componentIds.
        return Object.freeze(new Set(this.#currentSelection));
    }
}
