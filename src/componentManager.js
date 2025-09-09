import {createEvents, createEvent} from "./managerHelpers.js";

let CURRENT_PROJECT;  // Stores the raw form of the data (as JSON).
/*
 * JSON Format V4-1.0-SNAPSHOT.
 *
 * <Root>: {
 *     "version": "V4-1.0-SNAPSHOT",                 * This is added when we serialize the JSON, and is removed when we deserialize it.
 *     "components": {component-id: <Component>},
 *     "vertGroups": [<VertGroup>]
 * }
 *
 * <Component>: {
 *     "component-type": "text-component",
 *     "text": str,
 *     "font-size": positive real,  // TODO: Document what this font size actually means
 *     "x": real,  // TODO: Document what these coordinates actually mean
 *     "y": real
 * }
 *
 * <Component>: {
 *     "component-type": "score-component",
 *     "x": real,
 *     "y": real,
 *     "left-decoration": Nullable<left-decoration-id>,
 *     "right-decoration": Nullable<right-decoration-id>,
 *     "time-signature-denomenator": positive int,
 *     "rhythm-length-hint": non-negative real,
 *     "score-content": [<Beat>],                    * Must not be empty.
 *     "enabled-symbols": [symbol-id]                * Ids must be distinct.
 * }
 * <Beat>: [<Subdivision>]                           * Must not be empty.
 * <Subdivision>: [symbol-id]                        * Ids must be distinct.
 * 
 * <VertGroup>: [component-id]                       * Ids must be score-components. An ID may only be used once and in only one VertGroup.
 */

export class ComponentManager {
    // See src/README.md for overview of events and methods.
    // All getters and setters should be validated.

    // Serialization / Deserialization -------------------------------------------------------------------------
    static loadEmptyProject() {
        // Loads an empty project into memory.
        // This overwrites what was previously in there.
        
        CURRENT_PROJECT = {
            "components": {},
            "vertGroups": []
        }
    }
    
    // TODO: Serializing and deserializing the project - we need to add and remove the version. Also verify data is formatted correctly and consistant
    
    // Events --------------------------------------------------------------------------------------------------
    static {
        createEvents(this, "Component", ["Added", "Removed"]);
        createEvent(this, "BeforeComponentRemoved");
        createEvents(this, "Component", ["X", "Y", "TimeSignatureDenomenator", "RhythmLengthHint", "Text", "FontSize"], "Changed");
        createEvents(this, "Component", ["Left", "Right"], "DecorationChanged");
        createEvent(this, "ComponentVertGroupChanged");
        createEvent(this, "ComponentSymbolToggled");
        createEvent(this, "ComponentSymbolEnabledStateChanged");
        createEvents(this, "Component", ["Beats", "Subdivisions"], ["Added", "Removed"]);
    }

    // Component General ---------------------------------------------------------------------------------------
    static #getUniqueComponentId() {
        // Creates and returns a unique id that can be used for a new component.
        let n = 0;
        while (true) {  // Find first n such that component-n does not exist.
            const newId = "component-" + n;
            if (!this.componentExists(newId)) return newId;
            n++;
        }
    }

    static createEmptyComponent(componentType) {
        // Creates a new component of the given type, returns the id of that component.
        
        // Get default data for the given componentType
        let componentData;
        if (componentType === "score-component") {
            componentData = {
                "component-type": "score-component",
                "x": 0,
                "y": 0,
                "left-decoration": null,
                "right-decoration": null,
                "time-signature-denomenator": 4,
                "rhythm-length-hint": 0,
                "score-content": [[[], []], [[], []], [[], []], [[], []]],
                "enabled-symbols": []
            }
        } else if (componentType === "text-component") {
            componentData = {
                "component-type": "text-component",
                "x": 0,
                "y": 0,
                "text": "Hello World!",
                "font-size": 10
            }
        } else {
            throw "Unknown componentType " + componentType;
        }
        
        // Add the component to the project under a new id
        const newId = this.#getUniqueComponentId();
        CURRENT_PROJECT["components"][newId] = componentData;
        this.dispatchComponentAdded(newId);
    }
    
    static componentExists(componentId) {
        // Returns true if the given component exists, and false otherwise.
        return componentId in CURRENT_PROJECT["components"];
    }
    
    static getComponentType(componentId) {
        // Returns the type of the given component.
        // Throws an error if it doesn't exist.

        if (!this.componentExists(componentId)) throw "Component " + componentId + " does not exist";
        return CURRENT_PROJECT["components"][componentId]["component-type"];
    }
    
    static removeComponent(componentId) {
        // Removes the given component.
        // If this component does not exist then an error is thrown.
        // This will silently drop this components membership from a VertGroup (if necessary).

        if (!this.componentExists(componentId)) throw "Component " + componentId + " does not exist";
        this.dispatchBeforeComponentRemoved(componentId);
        delete CURRENT_PROJECT["components"][componentId];
        // TODO: Handle vert groups
        this.dispatchComponentRemoved(componentId);
    }

    static duplicateComponent(componentId) {
        // Duplicates the given component and returns the id of the new component.
        // If the given component does not exist then an error is thrown.
        
        if (!this.componentExists(componentId)) throw "Component " + componentId + " does not exist";
        
        const newId = this.#getUniqueComponentId();
        CURRENT_PROJECT["components"][newId] = JSON.parse(JSON.stringify(CURRENT_PROJECT["components"][componentId]));  // Deep copy component by serializing and then deserializing it
        this.dispatchComponentAdded(newId);
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
    
    static toggleComponentSymbol(componentId, beatI, subdivisionI, symbolId) {
        // Toggles whether the given symbol is used at the given subdivision of the given beat of the given component.
        // Errors are thrown if the componentId, beatI, subdivisionI, or symbolId are invalid.
        // Only symbolIds which are currently enabled by toggleComponentSymbolEnabledState are allowed to be used.
        // TODO: Handle this and events and validation
        // Validate args
        if (!this.componentExists(componentId) || this.getComponentType(componentId) !== "score-component") throw `Component ${componentId} does not exist or is not a score-component`;
    }
    
    static getComponentSymbolState(componentId, beatI, subdivisionI, symbolId) {
        // Gets whether the given symbol is being used in the given subdivision in the given beat on the given component.
        // Errors are thrown if the componentId, beatI, subdivisionI, or symbolId are invalid.
        // Only symbolIds which are currently enabled by toggleComponentSymbolEnabledState are allowed to be queried.
        // TODO: Handle this and validation
    }
    
    static getComponentSubdivisonSymbols(componentId, beatI, subdivisionI) {
        // Returns an immutable set of the symbolIds which are enabled on the given subdivison of the given beat of this given component.
        // TODO: Handle this and validation and Object.freeze
    }
    
    static toggleComponentSymbolEnabledState(componentId, symbolId) {
        // Toggles whether the given symbol can be enabled for this component.
        // This determins whether it is shown in the editor.
        // If this is disabled, then all enabled beats and subdivisions for this symbol are silently disabled.
        // TODO: Handle this and events and validation
    }
    
    static getComponentSymbolEnabledState(componentId, symbolId) {
        // Gets whether the given symbol can be used in the given component.
        // See toggleComponentSymbolEnabledState for more detail.
        // TODO: Handle this and validation
    }
    
    static addVertGroup(...componentIds) {
        // Creates a vert group for the given components.
        // Any already grouped (from the componentIds) will be removed from those groups.

        // TODO: Handle this and dispatch events and validate ids
    }
    
    static addBeats(componentId, numberOfSubdivisions, ...beatIndexes) {
        // Adds beats at the given indexes to the given component.
        // Each of the new beats will be empty, but have the given number of subdivisions.
        // The beats will be inserted at the given indexes in the order that they come.
        //      E.g. If we have 2 3 4 5 and we insert addBeats(id, 1, 1, 2) then we'd get 2 1 1 3 4 5.
        //      A single event is dispatched after all beats have been added internally.
        
        // TODO: Handle this and dispatch events and validate args
    }
    
    static removeBeats(componentId, ...beatIndex) {
        // Removes beats at the given indexes from the given component.
        // The beats will be removed at the given indexes in the order that they come.
        //      E.g. If we have 2 3 4 5 and we remove removeBeats(id, 1, 2) then we'd get 2 4.
        //      A single event is dispatched after all beats have been removed internally.
        
        // TODO: Handle this and dispatch events and validate args
        // TODO: Validate that will have at least one beat
    }
    
    static addSubdivisions(componentId, beatI, ...subdivisionIndexes) {
        // Adds subdivisions at the given indexes to the given beat of the given component.
        // Each of the new subdivisions will be empty.
        // These are added in the same order as addBeats.
        
        // TODO: Handle this and dispatch events and validate args
    }
    
    static removeSubdivisons(componentId, beatI, ...subdivisionIndexes) {
        // Removes subdivisions at the given indexes from the given beat of the given component.
        // These are removed in the same order as removeBeats.
        
        // TODO: Handle this and dispatch events and validate args
        // TODO: Validate that will have at least one subdivision
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
    
    const dispatchFuncName = "dispatchComponent" + fieldName + "Changed";
    const getterFuncName = "getComponent" + fieldName;
    const setterFuncName = "setComponent" + fieldName;
    
    // Ensure everything that should/shouldn't exist is correct
    if (getterFuncName in object || setterFuncName in object) throw "Getter or setter already exists for " + fieldName;
    if (!(dispatchFuncName in object)) throw "No dispatch function for " + fieldName;
    
    // Create getter
    object[getterFuncName] = (componentId) => {
        // Validate args
        if (!object.componentExists(componentId) || (componentType !== null && object.getComponentType(componentId) !== componentType)) throw "Component does not exist or is wrong type";
        
        // Return
        return CURRENT_PROJECT["components"][componentId][fieldName];
    }
    
    // Create setter
    object[setterFuncName] = (componentId, newValue) => {
        // Validate args
        if (!object.componentExists(componentId) || (componentType !== null && object.getComponentType(componentId) !== componentType)) throw "Component does not exist or is wrong type";
        if (!validator(newValue)) throw "Validation failed for " + fieldName + " on " + componentId + ", value " + newValue;
        
        // Set and dispatch event
        CURRENT_PROJECT["components"][componentId][fieldName] = newValue;
        object[dispatchFuncName](componentId, newValue);
    }
}

