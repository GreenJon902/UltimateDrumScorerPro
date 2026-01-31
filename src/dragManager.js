import {createEvents} from "./managerHelpers.js";
import {ComponentManager} from "./componentManager.js";
import {SelectionManager} from "./selectionManager.js"

const SIGNIFICANT_DISTANCE = 5;  // The totalDelta that is significant enough to suggest a drag is intentional

function distance(x1, y1, x2, y2) {
    // x1, y1, x2, y2: float.
    // returns: float.
    //
    // Calculates the distance between the given coordinates.
    return Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
}

export class DragManager {
    
    static #currentDrag = null;  // If this is non-null then we are currently dragging
                                 // This holds {componentIds: Set<component-id>, totalDeltaX: float, totalDeltaY: float, significant: bool, cardinal: bool}


    static {
        createEvents(this, "Drag", ["Start", "Move", "End"]);
        
        // Remove deleted components from drag. Idk how this would happen, but to be safe we'll listen to this
        ComponentManager.onBeforeComponentRemoved(id => {
            if (this.#currentDrag !== null) {
                this.#currentDrag.componentIds.delete(id);
            }
        });
    }
    
    static startDrag(cardinal, extraId) {
        // cardinal: bool - Should dragging be locked to cardinal directions. True for yes.
        // extraId: component-id - Even if this widget is not selected, it should be dragged anyway.
        //
        // Called when the mouse is pressed down.
        // The current selection will be taken to be dragged.
        // This should only be called if isDragging() returns false.
        
        if (this.#currentDrag !== null) throw "Tried to start drag when drag already in progress";
        
        this.#currentDrag = {
            componentIds: new Set([...SelectionManager.getSelection(), extraId]),  // We don't want this set to be frozen
            totalDeltaX: 0,  // Initial delta is 0
            totalDeltaY: 0,
            significant: false,  // This drag is not significant yet - the mouse has not moved far enough
            cardinal: cardinal
        };
        
        // We don't dispatch DragStart yet, as we don't know if this drag is significant
    }
    
    static moveDrag(deltaX, deltaY) {
        // deltaX: float - The change in X of the mouse from that last time this method was called.
        // deltaY: float - The change in Y of the mouse from that last time this method was called.
        // 
        // Called when the mouse has moved (deltaX, deltaY) from the position that this method was last called with.
        // This should only be called if isDragging() returns true.
        
        if (this.#currentDrag === null) throw "Tried to move drag when no drag in progress";
        
        // Update deltas
        this.#currentDrag.totalDeltaX += deltaX;
        this.#currentDrag.totalDeltaY += deltaY;
        
        // Update significance
        if (!this.#currentDrag.significant) {  // Significance can only change from false to true
            const distanceIsSignificant = distance(0, 0, this.#currentDrag.totalDeltaX, this.#currentDrag.totalDeltaY) > SIGNIFICANT_DISTANCE;  // Is the totalDelta large. We can ignore cardinal for this check
            
            if (distanceIsSignificant) {
                // This drag has become significant so dispatch event and set to significant

                this.#currentDrag.significant = true;
                this.dispatchDragStart(Object.freeze(new Set(this.#currentDrag.componentIds)))  // Clone and freeze array
           }
        }
        
        // Dispatch move event if this is significant
        if (this.#currentDrag.significant) {
            this.dispatchDragMove(Object.freeze(new Set(this.#currentDrag.componentIds)), ...this.#getCardinalAppliedTotalDeltaXY());
        }
    }
    
    static endDrag() {
        // returns: bool - True if this drag was significant (resulted in components being moved).
        //
        // Called when the mouse is released.
        
        if (this.#currentDrag === null) throw "Tried to end drag when no drag in progress";
        
        // Dispatch end event if this is significant
        if (this.#currentDrag.significant) {
            const [totalDeltaX, totalDeltaY] = this.#getCardinalAppliedTotalDeltaXY(); 

            // Inform the component manager of the changes
            this.#currentDrag.componentIds.forEach(id => {
                ComponentManager.setComponentX(id, ComponentManager.getComponentX(id) + totalDeltaX);
                ComponentManager.setComponentY(id, ComponentManager.getComponentY(id) + totalDeltaY);
            })
            
            // Dispatch drag end event
            this.dispatchDragEnd(Object.freeze(new Set(this.#currentDrag.componentIds)));
        }
        
        const wasSig = this.#currentDrag.significant;  // Save this as we need to return it
        this.#currentDrag = null;  // End the current drag
        
        return wasSig;
    }
    
    static setCardinal(cardinal) {
        // cardinal: bool
        // 
        // Updates whether this drag is locked to a cardinal direction or free.
        // This should only be called if isDragging() returns true.
        
        this.#currentDrag.cardinal = cardinal;
        // 
        // Dispatch move event if this is significant
        if (this.#currentDrag.significant) {
            this.dispatchDragMove(Object.freeze(new Set(this.#currentDrag.componentIds)), ...this.#getCardinalAppliedTotalDeltaXY());
        }
    }
    
    static isDragging() {
        // returns: bool - True if there is currently a drag. This ignores if the drag is significant.
        return this.#currentDrag !== null;
    }
    
    static #getCardinalAppliedTotalDeltaXY() {
        // returns: Array<float> - Array holding [x, y].
        // Returns the totalDeltaX and totalDeltaY. However if the cardinal flag is set then the lesser of the values will be 0.
        // 
        // This can only be called if isDragging() returns true.
        
        if (this.#currentDrag === null) throw "Tried to getCardinalAppliedTotalDeltaXY when no drag in progress";
        
        let moveX = this.#currentDrag.totalDeltaX; 
        let moveY = this.#currentDrag.totalDeltaY;
        if (this.#currentDrag.cardinal && moveX >= moveY) {
            moveY = 0;
        } else if (this.#currentDrag.cardinal && moveY > moveX) {
            moveX = 0;
        }
        return [moveX, moveY];
    }
}
