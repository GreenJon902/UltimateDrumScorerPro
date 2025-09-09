import {createEvents, createEvent} from "./managerHelpers.js";

class ComponentManager {
    // See src/README.md for overview of events and methods.
    // All getters and setters should be validated.

    // Events --------------------------------------------------------------------------------------------------
    static {
        createEvents(this, "Component", ["Added", "Removed"]);
        createEvent(this, "BeforeComponentRemoved");
        createEvents(this, "Component", ["X", "Y", "TimeSignatureDenomenator", "RhythmLengthHint", "Text", "FontSize"], "Changed");
        createEvents(this, "Component", ["Left", "Right"], "DecorationChanged");
        createEvent(this, "ComponentVertGroupChanged");
        createEvent(this, "ComponentToggleChanged");
        createEvent(this, "ComponentToggleEnabledStateChanged");
    }

    // Component General ---------------------------------------------------------------------------------------
    static createEmptyComponent(componentType) {
        // Creates a new component of the given type, returns the id of that component.
        
        if (componentType === "score-component") {
            // TODO: Handle this
        } else if (componentType === "text-component") {
            // TODO Handle this
        } else {
            throw "Unknown componentType " + componentType;
        }

        this.dispatchComponentAdded(componentId);
    }
    
    static componentExists(componentId) {
        // Returns true if the given component exists, and false otherwise.

        // TODO: Handle this
        return componentExists;
    }
    
    static getComponentType(componentId) {
        // Returns the type of the given component.
        // Throws an error if it doesn't exist.

        if (!this.componentExists(componentId)) throw "Component " + componentId + " does not exist";
        // TODO: Handle this
        return componentType;
    }
    
    static removeComponent(componentId) {
        // Removes the given component.
        // If this component does not exist then an error is thrown.

        if (!this.componentExists(componentId)) throw "Component " + componentId + " does not exist";
        this.dispatchBeforeComponentRemoved(componentId);
        // TODO: Handle this
        this.dispatchComponentRemoved(componentId);
    }

    static duplicateComponent(componentId) {
        // Duplicates the given component and returns the id of the new component.
        // If the given component does not exist then an error is thrown.
        
        if (!this.componentExists(componentId)) throw "Component " + componentId + " does not exist";
        // TODO: Handle this
        this.dispatchComponentAdded(newComponentId);
    }
    
    static {
        createBasicComponentGetterSetter(this, null, "X", v => typeof v === "number");
        createBasicComponentGetterSetter(this, null, "Y", v => typeof v === "number");
    }
    
    // Component Score -----------------------------------------------------------------------------------------
    static {
        createBasicComponentGetterSetter(this, "score-component", "TimeSignatureDenomenator", v => typeof v === "number" && v % 1 === 0 && v > 0);  // Positive integer
        createBasicComponentGetterSetter(this, "score-component", "RhythmLengthHint", v => typeof v === "number" && v > 0);  // Positive real
        createBasicComponentGetterSetter(this, "score-component", "LeftDecoration", v => typeof v === "string");  // TODO: Validate id
        createBasicComponentGetterSetter(this, "score-component", "RightDecoration", v => typeof v === "string");  // TODO: Validate id
    }
    
    static addVertGroup(...componentIds) {
        // Creates a vert group for the given components.
        // Any already grouped (from the componentIds) will be removed from those groups.

        // TODO: Handle this and dispatch events and validate ids
    }
    
    // Component Text ------------------------------------------------------------------------------------------
    static {
        createBasicComponentGetterSetter(this, "text-component", "Text", v => typeof v === "string");  // Some string
        createBasicComponentGetterSetter(this, "text-component", "FontSize", v => typeof v === "number" && v > 0);  // Positive real
    }
}

function createBasicComponentGetterSetter(object, componentType, fieldName, validator) {
    // Creates a getter and a setter on the object for the given fieldName. If componentType is given (not null) then it will only work for that componentType.
    // The validator is called on the setter value, and an error is thrown if it returns false.
    // The getter is called getComponent<FieldName>(componentId), the setter is called setComponent<FieldName>(componentId, newValue), the called is dispatchComponent<FieldName>Changed(componentId, newValue).
    // 
    // This expects the methods componentExists(componentId)->bool and getComponentType(componentId)->componentType to be present in object.
    // 
    // If a getter or setter with these names already exists then an error is thrown. If no dispatch function exists then an error is thrown.
    
    const dispatchFuncName = "dispatch" + fieldName + "Changed";
    const getterFuncName = "getComponent" + fieldName;
    const setterFuncName = "setComponent" + fieldName;
    
    // Ensure everything that should/shouldn't exist is correct
    if (getterFuncName in object || setterFuncName in object) throw "Getter or setter already exists for " + fieldName;
    if (!(dispatchFuncName in object)) throw "No dispatch function for " + fieldName;
    
    // Create getter
    object[getterFuncName] = (componentId) => {
        if (!object.componentExists(componentId) || (componentType !== null && object.getComponentType(componentId) !== componentType)) throw "Component does not exist or is wrong type";
        // TODO: Handle this
        return value;
    }
    
    // Create setter
    object[setterFuncName] = (componentId, newValue) => {
        if (!object.componentExists(componentId) || (componentType !== null && object.getComponentType(componentId) !== componentType)) throw "Component does not exist or is wrong type";
        if (!validator(newValue)) throw "Validation failed for " + fieldName + " on " + componentId + ", value " + newValue;
        // TODO: Handle this
        object[dispatchFuncName](componentId, newValue);
    }
}

