import {ComponentManager} from "./componentManager.js";
import {SelectionManager} from "./selectionManager.js";
import {DragManager} from "./dragManager.js";
import {createSvgText, updateSvgText} from "./textComponentSvgRenderer.js";
import {compileScoreComponent} from "./scoreComponentUtils/compile.js";
import {calculateScoreComponentSpacing} from "./scoreComponentUtils/decode.js";
import {renderScoreComponentFromInstructionsAndSpacing} from "./scoreComponentUtils/execute.js";
import {bindAll} from "./managerHelpers.js";

function partial(func, ...args) {
    // Returns the functions with the given arguements already passed before any new arguements.
    return (...args2) => func(...args, ...args2);
}

export function attachRendered(componentContainer) {
    // Sets up bindings for the given componentContainer to connect it ot he various managers.
    // The componentContainer should be a div and only be used for this.
    // 
    // This will not handle zooming and panning, that should be done externally.
    
    // When a component is removed, we need to redraw any components that were vertically grouped with it
    // When we recieve onBeforeComponentRemoved (when we still know what is in this group), we save the linked components
    // Then when we reciept onComponentRemoved (when this component has been (silently) dropped from its group), we can update the linked components
    // This may contain the id of the removed component
    const scoreComponentsToBeUpdatedOnComponentRemoved = new Set();
    
    // Add components that already exist
    ComponentManager.getComponentIds().forEach(componentId => createInitialGenericComponent(componentContainer, componentId));
    
    const pusc = partial(updateScoreComponent, componentContainer);
    bindAll(ComponentManager, {
        // Bind component addition / removal events
        onComponentAdded: partial(createInitialGenericComponent, componentContainer),
        onBeforeComponentRemoved: id => {
            // Save all ids of components in the group that the given component is in (if applicable)
            if (ComponentManager.isInVertGroup(id)) 
                new Array(...ComponentManager.getVertGroup(id)).forEach(linkedId => scoreComponentsToBeUpdatedOnComponentRemoved.add(linkedId));
        },
        onComponentRemoved: id => {
            // Remove component
            removeComponent(componentContainer, id);
            // Update components that were linked to the deleted component
            new Array(...scoreComponentsToBeUpdatedOnComponentRemoved)
                .filter(linkedId => ComponentManager.componentExists(linkedId))  // Drop components that no-longer exist
                .forEach(linkedId => pusc(linkedId));
        },
        // Bind events for generic component changes
        onComponentXChanged: partial(updateComponentX, componentContainer),
        onComponentYChanged: partial(updateComponentY, componentContainer),
        // Bind events for text-components changes
        onComponentTextChanged: partial(updateTextComponent, componentContainer, "text"),
        onComponentFontSizeChanged: partial(updateTextComponent, componentContainer, "fontSize"),
        // Bind events for score-components changes
        onComponentDrumToggled: pusc,
        onComponentTimeSignatureDenomenatorChanged: null,  // This has no effect at the moment  // TODO: This
        onComponentRhythmLengthHintChanged: pusc,  
        onComponentLeftDecorationChanged: pusc,
        onComponentRightDecorationChanged: pusc,
        onComponentVertGroupChanged: (before, after) => 
            new Array(...new Set([...(before === null) ? [] : before, ...(after === null) ? [] : after]))  // Get array of unique component ids involved in this change
                .forEach(id => pusc(id)), 
        onComponentDrumToggled: pusc,
        onComponentDrumEnabledStateChanged: pusc,  // This may remove some toggled drums without triggering onComponentDrumToggled
        onComponentBeatsAdded: pusc,
        onComponentBeatsRemoved: pusc,
        onComponentSubdivisionsAdded: pusc,
        onComponentSubdivisionsRemoved: pusc
    });


    
    
    // Bind selection events
    SelectionManager.onSelectionStateChanged((componentId, selectionState) => updateSelectionState(componentContainer, componentId, selectionState));
    
    // Bind drag events
    DragManager.onDragStart((componentIds) => prepDrag(componentContainer, componentIds));
    DragManager.onDragMove((componentIds, totalDeltaX, totalDeltaY) => updateDrag(componentContainer, componentIds, totalDeltaX, totalDeltaY));
    DragManager.onDragEnd((componentIds) => removeDrag(componentContainer, componentIds));
}

function prepDrag(componentContainer, componentIds) {
    // Prepares the given components to be dragged.
    
    // Give each component a "translate" to its style
    componentIds.forEach(id => {
        const comp = getSvgFor(componentContainer, id);
        comp.style.setProperty("translate", "0mm, 0mm");
    });
}

function updateDrag(componentContainer, componentIds, totalDeltaX, totalDeltaY) {
    // Updates the amount the given components are dragged/translated by.
    
    // Update the translate css for each component
    componentIds.forEach(id => {
        const comp = getSvgFor(componentContainer, id);
        comp.style.setProperty("translate", `${totalDeltaX}mm ${totalDeltaY}mm`);
    });
}

function removeDrag(componentContainer, componentIds) {
    // Finishes the drag for the given components, so removes the translate css.
    
    // Remove the "translate" for each component
    componentIds.forEach(id => {
        const comp = getSvgFor(componentContainer, id);
        comp.style.removeProperty("translate");
    });
}

function updateComponentX(componentContainer, componentId, x) {
    // Update the given components x coordinate.
    getSvgFor(componentContainer, componentId).style.setProperty("left", `${x}mm`);
}
function updateComponentY(componentContainer, componentId, y) {
    // Update the given components y coordinate.
    getSvgFor(componentContainer, componentId).style.setProperty("top", `${y}mm`);
}

function createInitialGenericComponent(componentContainer, componentId) {
    // Runs the appropriate createInitialTextComponent/createInitialScoreComponent function.
    const componentType = ComponentManager.getComponentType(componentId);
    if (componentType === "text-component") {
        createInitialTextComponent(componentContainer, componentId);
    } else if (componentType === "score-component") {
        createInitialScoreComponent(componentContainer, componentId);
    } else {
        throw "Not implemented";
    }
}

function removeComponent(componentContainer, componentId) {
    // Removes the given component from the container.
    // This expects it to exist.
    getSvgFor(componentContainer, componentId).remove();
}

function createBaseSvg(componentContainer, componentId) {
    // Creates an svg, adds it to the container, and then returns the node which contents should be added to.
    // This will set the selection state.
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.dataset.componentId = componentId;
    
    // In the svg, 1 unit should be 1mm. We want to keep the svg inisde its bounding box and it's size correct.
    // To do this we can use a mutation observer to ensure it's size is always correct.
    new MutationObserver((mutationList, _) => {
        // If the mutation is the size (because this callback has already been called) then we can ignore it.
        if (mutationList.filter(mut => !(mut.type === "attributes" && ["viewBox", "width", "height"].includes(mut.attributeName))).length === 0) return;

        // When this is called, something in the svg has changed, so we need to re-apply the sizing information
        // TODO: Use a request animation frame for this
        const bbox = svg.getBBox();
        svg.setAttribute("viewBox", `${bbox.x} ${bbox.y} ${bbox.width} ${bbox.height}`);  // So svg content starts at (0,0)
        svg.setAttribute("width", bbox.width + "mm");  // MM so 1px goes to 1mm
        svg.setAttribute("height", bbox.height + "mm");  // MM so 1px goes to 1mm

    }).observe(svg, { attributes: true, characterData: true, subtree: true, childList: true });
    
    // Set the initial selection state
    const selectionState = SelectionManager.isSelected(componentId);
    if (selectionState) {
        // Add data-selected tag
        svg.setAttribute("data-selected", "");
    } else {
        // Remove data-selected tag
        svg.removeAttribute("data-selected");
    }
    
    // Set initial coordinates
    svg.style.setProperty("left", `${ComponentManager.getComponentX(componentId)}mm`);
    svg.style.setProperty("top", `${ComponentManager.getComponentY(componentId)}mm`);

    componentContainer.appendChild(svg);
    return svg;
}

function getSvgFor(componentContainer, componentId) {
    // Gets the svg node for the given component from the componentContainer.
    return componentContainer.querySelector(`[data-component-id=${componentId}]`);
}

function updateSelectionState(componentContainer, componentId, selectionState) {
    // selectionState: bool - True for selected, false for not selected.
    //
    // Update the given components selection state to what was given.
    // This will not affect other components selection state.
    
    const comp = getSvgFor(componentContainer, componentId);
    if (selectionState) {
        // Add data-selected tag
        comp.setAttribute("data-selected", "");
    } else {
        // Remove data-selected tag
        comp.removeAttribute("data-selected")
    }
}

function createInitialTextComponent(componentContainer, componentId) {
    // Creates the initial SVG for the given text component.
    // This requires bindings (via updateTextComponent) to be called whenever component manager changes.
    const svg = createBaseSvg(componentContainer, componentId);
    createSvgText(svg, ComponentManager.getComponentText(componentId), ComponentManager.getComponentFontSize(componentId));
    componentContainer.appendChild(svg);
}

function updateTextComponent(componentContainer, what, componentId, newValue) {
    // Updates the given attribute (what - "text", "fontSize") for the given component to the new value.
    // This works on SVGs created by createInitialTextComponent.
    const svg = getSvgFor(componentContainer, componentId);
    updateSvgText(svg, what, newValue);
}

function createInitialScoreComponent(componentContainer, componentId) {
    // Creates the initial SVG for the given score component.
    // This requires bindings (via updateScoreComponent) to be called whenever component manager changes.
    const svg = createBaseSvg(componentContainer, componentId);
    const instructions = compileScoreComponent(componentId);
    const vertGroupLinkedComponentInstructions = new Set((ComponentManager.isInVertGroup(componentId)) ?
        new Array(...ComponentManager.getVertGroup(componentId).difference(new Set([componentId])))  // Array so we can use for each. We remove componentId as we've already compiled it
            .map(id => compileScoreComponent(id)) : [])
        .add(instructions);  // Add the instructions from this component too
    // TODO: Cache whether a vertGroupLinked component changing affects this compoennt (so whether we actually need to redraw it)
    console.log(instructions);
    console.log(vertGroupLinkedComponentInstructions);
    const spacing = calculateScoreComponentSpacing(instructions, vertGroupLinkedComponentInstructions, ComponentManager.getComponentRhythmLengthHint(componentId));
    console.log(spacing);
    renderScoreComponentFromInstructionsAndSpacing(svg, instructions, spacing);
    componentContainer.appendChild(svg);
}

function updateScoreComponent(componentContainer, componentId) {
    // Re-renders the given score-component, and any components that are vertically-grouped with the given component.
    // This works on the SVGs created by createInitialScoreComponent.
    
    // Collect ids of components that need redrawing
    let redrawIds;
    if (ComponentManager.isInVertGroup(componentId)) {
        redrawIds = new Array(...ComponentManager.getVertGroup(componentId));  // Array so we can use for each
    } else {
        redrawIds = [componentId];
    }

    redrawIds.forEach(id => {
        const svg = getSvgFor(componentContainer, id);
        componentContainer.removeChild(svg);
        createInitialScoreComponent(componentContainer, id);
    });
}

