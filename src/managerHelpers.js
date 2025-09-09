export function createEvents(object, ...nameParts) {
    // Creates mutliple events for the object using createEvent.
    // The parts can be string or arrays. When arrays are used, this means create an event for each element. E.g. "A", ["B", C], "D" => ABD, ACD. You may not use nested arrays.
    if (nameParts.length === 0) {
        throw "Cannot create event with no name";
    }
    
    // The algo needs the first item to be a string, so if it isn't then add an empty one
    if (Array.isArray(nameParts[0])) nameParts.splice(0, 0, "");
    
    if (nameParts.length === 1) {  // Has to be string, as if array then we'd have added an empty string
        createEvent(object, nameParts[0]);  // One name so just create an event
        
    } else {
        // Multiple name parts so join them:
        if (Array.isArray(nameParts[1])) {
            // nameParts[0] is a string, but nameParts[1] is an array, so join 0 to each of 1 and call reccursively
            for (let i=0; i<nameParts[1].length; i++) {
                createEvents(object, nameParts[0] + nameParts[1][i], ...nameParts.slice(2));
            }

        } else {
            // nameParts[0] and nameParts[1] are both strings so join them, and handle the rest of the array in a reccursive call
            createEvents(object, nameParts[0] + nameParts[1], ...nameParts.slice(2));
        }
    }
}

export function createEvent(object, name) {
    // Creates an event for the object with the given name.
    // They will be applied to the given object, so that should be a class if you want static method, and an instance if you want instancemethod.
    
    // Create dispatch function
    object["dispatch" + name] = (...args) => {
        console.info(ComponentManager.name + "." + name + " dispatched with (" + args.join() + ")");
    }
}
