import {createEvents, createEvent} from "./managerHelpers.js";


// TODO: Combined logic of AddBeats, RemoveBeats, AddSubdivision and RemoveSubdivision
// TODO: Validate that indexes are actually integers


let CURRENT_PROJECT;  // Stores the raw form of the data (as JSON).
/*
 * JSON Format V4-1.0-SNAPSHOT.
 *
 * <Root>: {
 *     "version": "V4-1.0-SNAPSHOT",                 * This is added when we serialize the JSON, and is removed when we deserialize it.
 *     "components": {component-id: <Component>},
 *     "vert-groups": [<VertGroup>]
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
 *     "enabled-drums": [drum-id]                    * Ids must be distinct.
 * }
 * <Beat>: [<Subdivision>]                           * Must not be empty.
 * <Subdivision>: [drum-id]                          * Ids must be distinct.
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
            "vert-groups": []
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
        createEvent(this, "ComponentDrumToggled");
        createEvent(this, "ComponentDrumEnabledStateChanged");
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
                "enabled-drums": []
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
        
        return newId;
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
    
    static getComponentIds() {
        // Returns a frozen set of the IDs of all components.
        return Object.freeze(new Set(Object.keys(CURRENT_PROJECT["components"])))
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
        
        return newId;
    }
    
    static {
        createBasicComponentGetterSetter(this, null, "X", "x", v => typeof v === "number");
        createBasicComponentGetterSetter(this, null, "Y", "y", v => typeof v === "number");
    }
    
    // Component Score -----------------------------------------------------------------------------------------
    static {
        createBasicComponentGetterSetter(this, "score-component", "TimeSignatureDenomenator", "time-signature-denomenator", v => typeof v === "number" && v % 1 === 0 && v > 0);  // Positive integer
        createBasicComponentGetterSetter(this, "score-component", "RhythmLengthHint", "rhythm-length-hint", v => typeof v === "number" && v > 0);  // Positive real
        createBasicComponentGetterSetter(this, "score-component", "LeftDecoration", "left-decoration", v => typeof v === "string");  // TODO: Validate id
        createBasicComponentGetterSetter(this, "score-component", "RightDecoration", "right-decoration", v => typeof v === "string");  // TODO: Validate id
    }
    
    static toggleComponentDrum(componentId, beatI, subdivisionI, drumId) {
        // Toggles whether the given drum is used at the given subdivision of the given beat of the given component.
        // Errors are thrown if the componentId, beatI, subdivisionI, or drumId are invalid.
        // Only drumIds which are currently enabled by toggleComponentDrumEnabledState are allowed to be used.
        
        // Validate args
        if (!this.componentExists(componentId) || this.getComponentType(componentId) !== "score-component") throw `Component ${componentId} does not exist or is not a score-component`;
        if (!(0 <= beatI && beatI < this.getComponentBeatCount(componentId))) throw "BeatI out of range";
        if (!(0 <= subdivisionI && subdivisionI < this.getComponentBeatSubdivisionCount(componentId, beatI))) throw "SubdivisionI out of range";
        // TODO: Validate drumId is valid
        if (!this.getComponentDrumEnabledState(componentId, drumId)) throw "Tried to use toggle on disabled drumId";
        
        // Handle toggle
        toggleArrayItem(CURRENT_PROJECT["components"][componentId]["score-content"][beatI][subdivisionI], drumId);  // Updates array in-place
        this.dispatchComponentDrumToggled(componentId, beatI, subdivisionI, drumId, this.getComponentDrumState(componentId, beatI, subdivisionI, drumId));
    }
    
    static getComponentDrumState(componentId, beatI, subdivisionI, drumId) {
        // Gets whether the given drum is being used in the given subdivision in the given beat on the given component.
        // Errors are thrown if the componentId, beatI, subdivisionI, or drumId are invalid.
        // Only drumIds which are currently enabled by toggleComponentDrumEnabledState are allowed to be queried.
        
        // Validate args
        if (!this.componentExists(componentId) || this.getComponentType(componentId) !== "score-component") throw `Component ${componentId} does not exist or is not a score-component`;
        if (!(0 <= beatI && beatI < this.getComponentBeatCount(componentId))) throw "BeatI out of range";
        if (!(0 <= subdivisionI && subdivisionI < this.getComponentBeatSubdivisionCount(componentId, beatI))) throw "SubdivisionI out of range";
        // TODO: Validate drumId is valid
        if (!this.getComponentDrumEnabledState(componentId, drumId)) throw "Tried to use toggle on disabled drumId";
        
        return CURRENT_PROJECT["components"][componentId]["score-content"][beatI][subdivisionI].includes(drumId);
    }
    
    static getComponentSubdivisionDrums(componentId, beatI, subdivisionI) {
        // Returns an immutable set of the drumIds which are enabled on the given subdivison of the given beat of this given component.
        
        // Validate args
        if (!this.componentExists(componentId) || this.getComponentType(componentId) !== "score-component") throw `Component ${componentId} does not exist or is not a score-component`;
        if (!(0 <= beatI && beatI < this.getComponentBeatCount(componentId))) throw "BeatI out of range";
        if (!(0 <= subdivisionI && subdivisionI < this.getComponentBeatSubdivisionCount(componentId, beatI))) throw "SubdivisionI out of range";
        
        return Object.freeze(new Set(CURRENT_PROJECT["components"][componentId]["score-content"][beatI][subdivisionI]));
    }
    
    static toggleComponentDrumEnabledState(componentId, drumId) {
        // Toggles whether the given drum can be enabled for this component.
        // This determins whether it is shown in the editor.
        // If this is disabled, then all enabled beats and subdivisions for this drum are silently disabled.
        
        // Validate args
        if (!this.componentExists(componentId) || this.getComponentType(componentId) !== "score-component") throw `Component ${componentId} does not exist or is not a score-component`;
        // TODO: Validate drum id
        
        // Silently drop any removed drums from the score if we're removing a drumId
        if (this.getComponentDrumEnabledState(componentId, drumId)) {
            for (let bi=0; bi<this.getComponentBeatCount(componentId); bi++) {
                for (let si=0; si<this.getComponentBeatSubdivisionCount(componentId, bi); si++) {
                    if (this.getComponentDrumState(componentId, bi, si, drumId)) {
                        const array = CURRENT_PROJECT["components"][componentId]["score-content"][bi][si];  // Do action on array so no events are dispatched
                        array.splice(array.indexOf(drumId), 1);
                    }
                }
            }
        }

        // Handle toggle
        toggleArrayItem(CURRENT_PROJECT["components"][componentId]["enabled-drums"], drumId);  // Updates array in place
        this.dispatchComponentDrumEnabledStateChanged(componentId, drumId, this.getComponentDrumEnabledState(componentId, drumId));
    }
    
    static getComponentDrumEnabledState(componentId, drumId) {
        // Gets whether the given drum can be used in the given component.
        // See toggleComponentDrumEnabledState for more detail.
         
        // Validate args
        if (!this.componentExists(componentId) || this.getComponentType(componentId) !== "score-component") throw `Component ${componentId} does not exist or is not a score-component`;
        // TODO: Validate drum id
        
        return CURRENT_PROJECT["components"][componentId]["enabled-drums"].includes(drumId);
    }
    
    static addVertGroup(...componentIds) {
        // Creates a vert group for the given components.
        // Any already grouped (from the componentIds) will be removed from those groups.
        // Note: This method is not properly atomic, if the dispatched remove events fail then the add events will not be called.

        // Validate componentIds
        componentIds.forEach(id => {if (!this.componentExists(id) || this.getComponentType(id) !== "score-component") throw "Component does not exist or is not score-component"; })
        
        // Remove any componentIds that are already grouped
        this.removeFromVertGroup(false, ...componentIds);
        
        // Add new group
        componentIds = Array.from(new Set(componentIds));
        CURRENT_PROJECT["vert-groups"].push(componentIds);  // Remove duplicates. We need an array (and not a set) in the JSON
        this.dispatchComponentVertGroupChanged(null, Object.freeze(new Set(componentIds)));
    }
    
    static removeFromVertGroup(...args) {
        // Removes the given components from any vert groups. If a resulting vert group has length 1 then it will be removed.
        // If a componentId is not in a vert group and the requireInGroup flag is set then an error is thrown.
        // 
        // The args are either (requireInGroup: boolean, ...componentIds) or (...componentIds)
        
        // Handle args
        args = new Array(...args);  // Duplicate as we edit
        const requireInGroup = (args.length > 0 && typeof args[0] === "boolean") ? args.shift() : true; 
        const componentIds = args;
        
        // Validate componentIds exist and are score components
        componentIds.forEach(id => { if (!this.componentExists(id) || this.getComponentType(id) !== "score-component") throw "Component does not exist or is not score-component"; });
        // Validate components are already in vert groups (if flag is set)
        if (requireInGroup) componentIds.forEach(id => { if (!this.isInVertGroup(id)) throw "Component not in vertGroup"; });
        
        // Copy vert-groups so this method is atomic
        const newVertGroups = JSON.parse(JSON.stringify(CURRENT_PROJECT["vert-groups"]));  // Need to deep copy
        
        // We need to track which groups have changed (for the events)
        const modifiedBefore = new Array();  // Index of before corrosponds to index of after
        const modifiedAfter = new Array();
        
        // Remove from vertGroup
        for (let vgi=0; vgi<newVertGroups.length; vgi++) {
            // Remove any as needed
            const vgBefore = new Set(newVertGroups[vgi]);
            const vgAfter = vgBefore.difference(new Set(componentIds));  // Remove all of the given componentIds from vgBefore   
            
            // If any were removed then handle that
            if (vgAfter.size === 1) {  // Destroy group
                newVertGroups.splice(vgi, 1);
                vgi--;  // We removed the current vgi so we don't need to change the index
                modifiedBefore.push(Object.freeze(vgBefore));
                modifiedAfter.push(null);
            
            } else if (vgBefore.size !== vgAfter.size) {  // Replace group
                newVertGroups[vgi] = vgAfter;
                modifiedBefore.push(Object.freeze(vgBefore));
                modifiedAfter.push(Object.freeze(new Set(vgAfter)));  // Duplicate set object as we store vgAfter (in CURRENT_PROJECT) and don't want the one we store frozen
            }
        }
        
        // Commit changes
        CURRENT_PROJECT["vert-groups"] = newVertGroups;
        for (let i=0; i<modifiedBefore.length; i++) {
            this.dispatchComponentVertGroupChanged(modifiedBefore[i], modifiedAfter[i]);
        }
    }
    
    static isInVertGroup(componentId) {
        // Checks whether the given componentId is in a vertGroup.
        
        // Validate
        if (!this.componentExists(componentId) || this.getComponentType(componentId) !== "score-component") throw "Component does not exist or is of wrong type";
        
        // Check if any vertGroup contains the component
        return [false, ...CURRENT_PROJECT["vert-groups"].map(g => g.includes(componentId))].reduce((a, b) => a || b);
    }

    static getVertGroup(componentId) {
        // Returns a frozen set of the componentIds that are in a vert group with the given componentId.
        // If componentId is not in a vert group then an error is thrown.
        
        // Validate
        if (!this.componentExists(componentId) || this.getComponentType(componentId) !== "score-component") throw "Component does not exist or is of wrong type";
        if (!this.isInVertGroup(componentId)) throw "Given component not in vertGroup";
        
        // Find the group
        return Object.freeze(new Set(CURRENT_PROJECT["vert-groups"].filter(g => g.includes(componentId))[0]));
    }
    
    static addBeats(componentId, numberOfSubdivisions, ...beatIndexes) {
        // Adds beats at the given indexes to the given component.
        // Each of the new beats will be empty, but have the given number of subdivisions.
        // The beats will be inserted at the given indexes in the order that they come.
        //      E.g. If we have 2 3 4 5 and we insert addBeats(id, 1, 1, 2) then we'd get 2 1 1 3 4 5.
        //      A single event is dispatched after all beats have been added internally.
        
        // Validate componentId and numberOfSubdivisions
        if (!this.componentExists(componentId) || this.getComponentType(componentId) !== "score-component") throw `Component ${componentId} does not exist or is not a score-component`;
        if (numberOfSubdivisions <= 0) throw "NumberOfSubdivisions must be above 0";
        
        // Copy beats array so action is atomic (incase validation fails in middle)
        const newBeats = new Array(...CURRENT_PROJECT["components"][componentId]["score-content"]);  // Only needs to be a shallow copy
        
        // Add beats
        for (let i=0; i<beatIndexes.length; i++) {
            let bi = beatIndexes[i];
            
            // Validate beat index
            if (!(0 <= bi && bi <= newBeats.length)) throw "BeatI out of range";  // <= on upper bound as we might want to add such that it's the last item
            
            // Create the new beat's content. Do this each time so each is it's own object
            let newContent = new Array();
            for (let j=0; j<numberOfSubdivisions; j++) newContent.push(new Array());
            
            // Add beat
            newBeats.splice(bi, 0, newContent)
        }
        
        // Finalise action
        CURRENT_PROJECT["components"][componentId]["score-content"] = newBeats;
        this.dispatchComponentBeatsAdded(componentId, numberOfSubdivisions, Object.freeze(new Array(beatIndexes)));
    }
    
    static removeBeats(componentId, ...beatIndexes) {
        // Removes beats at the given indexes from the given component.
        // The beats will be removed at the given indexes in the order that they come.
        //      E.g. If we have 2 3 4 5 and we remove removeBeats(id, 1, 2) then we'd get 2 4.
        //      A single event is dispatched after all beats have been removed internally.
        
        // Validate componentId
        if (!this.componentExists(componentId) || this.getComponentType(componentId) !== "score-component") throw `Component ${componentId} does not exist or is not a score-component`;
        
        // Copy beats array so action is atomic (incase validation fails in middle)
        const newBeats = new Array(...CURRENT_PROJECT["components"][componentId]["score-content"]);  // Only needs to be a shallow copy
        
        // Remove beats
        for (let i=0; i<beatIndexes.length; i++) {
            let bi = beatIndexes[i];
            
            // Validate beat index and ensure component won't be empty afterwards
            if (!(0 <= bi && bi < newBeats.length)) throw "BeatI out of range";
            if (newBeats.length === 1) throw "There must be at least one beat in a component";
            
            // Remove beat
            newBeats.splice(bi, 1);
        }
        
        // Finalise action
        CURRENT_PROJECT["components"][componentId]["score-content"] = newBeats;
        this.dispatchComponentBeatsRemoved(componentId, Object.freeze(new Array(beatIndexes)));
    }
    
    static addSubdivisions(componentId, beatI, ...subdivisionIndexes) {
        // Adds subdivisions at the given indexes to the given beat of the given component.
        // Each of the new subdivisions will be empty.
        // These are added in the same order as addBeats.
        
        // Validate componentId and beatI
        if (!this.componentExists(componentId) || this.getComponentType(componentId) !== "score-component") throw `Component ${componentId} does not exist or is not a score-component`;
        if (!(0 <= beatI && beatI < this.getComponentBeatCount(componentId))) throw "BeatI out of range";  
        
        // Copy subdivisions array so action is atomic (incase validation fails in middle)
        const newSubdivisions = new Array(...CURRENT_PROJECT["components"][componentId]["score-content"][beatI]);  // Only needs to be a shallow copy
        
        // Add beats
        for (let i=0; i<subdivisionIndexes.length; i++) {
            let si = subdivisionIndexes[i];
            
            // Validate subdivision index
            if (!(0 <= si && si <= newSubdivisions.length)) throw "SubdivisionI out of range";  // <= on upper bound as we might want to add such that it's the last item
            
            // Add subdivison
            newSubdivisions.splice(si, 0, new Array());
        }
        
        // Finalise action
        CURRENT_PROJECT["components"][componentId]["score-content"][beatI] = newSubdivisions;
        this.dispatchComponentSubdivisionsAdded(componentId, beatI, Object.freeze(new Array(subdivisionIndexes)));
    }
    
    static removeSubdivisons(componentId, beatI, ...subdivisionIndexes) {
        // Removes subdivisions at the given indexes from the given beat of the given component.
        // These are removed in the same order as removeBeats.
        
        // Validate componentId and beatI
        if (!this.componentExists(componentId) || this.getComponentType(componentId) !== "score-component") throw `Component ${componentId} does not exist or is not a score-component`;
        if (!(0 <= beatI && beatI < this.getComponentBeatCount(componentId))) throw "BeatI out of range";  
        
        // Copy subdivisions array so action is atomic (incase validation fails in middle)
        const newSubdivisions = new Array(...CURRENT_PROJECT["components"][componentId]["score-content"][beatI]);  // Only needs to be a shallow copy
        
        // Remove beats
        for (let i=0; i<subdivisionIndexes.length; i++) {
            let si = subdivisionIndexes[i];
            
            // Validate subdivision index and beat won't be empty afterwards
            if (!(0 <= si && si < newSubdivisions.length)) throw "SubdivisionI out of range";  
            if (newSubdivisions.length === 1) throw "There must be at least one subdivision in a beat";
            
            // Remove subdivison
            newSubdivisions.splice(si, 1);
        }
        
        // Finalise action
        CURRENT_PROJECT["components"][componentId]["score-content"][beatI] = newSubdivisions;
        this.dispatchComponentSubdivisionsRemoved(componentId, beatI, Object.freeze(new Array(subdivisionIndexes)));
    }
    
    static getComponentBeatCount(componentId) {
        // Get's the number of beats - the timeSignatureNumerator - of the given component.

        if (!this.componentExists(componentId) || this.getComponentType(componentId) !== "score-component") throw "Component does not exist or is wrong type";
        return CURRENT_PROJECT["components"][componentId]["score-content"].length;
    }
    
    static getComponentBeatSubdivisionCount(componentId, beatI) {
        // Get's the number of subdivisions in the given beat of the given component.

        // Validate args
        if (!this.componentExists(componentId) || this.getComponentType(componentId) !== "score-component") throw "Component does not exist or is wrong type";
        if (!(0 <= beatI && beatI < this.getComponentBeatCount(componentId))) throw "BeatI out of range";

        return CURRENT_PROJECT["components"][componentId]["score-content"][beatI].length;
    }
    
    // Component Text ------------------------------------------------------------------------------------------
    static {
        createBasicComponentGetterSetter(this, "text-component", "Text", "text", v => typeof v === "string");  // Some string
        createBasicComponentGetterSetter(this, "text-component", "FontSize", "font-size", v => typeof v === "number" && v > 0);  // Positive real
    }
}

function createBasicComponentGetterSetter(object, componentType, fieldName, jsonFieldName, validator) {
    // Creates a getter and a setter on the object for the given fieldName. If componentType is given (not null) then it will only work for that componentType.
    // The validator is called on the setter value, and an error is thrown if it returns false.
    // The getter is called getComponent<FieldName>(componentId), the setter is called setComponent<FieldName>(componentId, newValue), the called is dispatchComponent<FieldName>Changed(componentId, newValue).
    // The jsonFieldName is the key to use when storing and getting from CURRENT_PROJECT.
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
        return CURRENT_PROJECT["components"][componentId][jsonFieldName];
    }
    
    // Create setter
    object[setterFuncName] = (componentId, newValue) => {
        // Validate args
        if (!object.componentExists(componentId) || (componentType !== null && object.getComponentType(componentId) !== componentType)) throw "Component does not exist or is wrong type";
        if (!validator(newValue)) throw "Validation failed for " + fieldName + " on " + componentId + ", value " + newValue;
        
        // Set and dispatch event
        CURRENT_PROJECT["components"][componentId][jsonFieldName] = newValue;
        object[dispatchFuncName](componentId, newValue);
    }
}

function toggleArrayItem(array, item) {
    // If item is already in array then (all instances of) it is(/are) removed, otherwise it is added.
    // This is done to the given array object.

    if (array.includes(item)) {
        // Already there so remove
        while (array.includes(item)) {  // While loop to remove all occurances
            array.splice(array.indexOf(item), 1);
        }
    } else {
        // Not there so add
        array.push(item);
    }
}
