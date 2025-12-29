import {ComponentManager} from "./componentManager.js";
import {createSvgText, updateSvgText} from "./textComponentSvgRenderer.js";
import {compileScoreComponent} from "./scoreComponentUtils/compile.js";
import {calculateScoreComponentSpacing} from "./scoreComponentUtils/decode.js";
import {renderScoreComponentFromInstructionsAndSpacing} from "./scoreComponentUtils/execute.js";

export function attachRendered(componentContainer) {
    // Sets up bindings for the given componentContainer to connect it ot he various managers.
    // The componentContainer should be a div and only be used for this.
    // 
    // This will not handle zooming and panning, that should be done externally.
    
    // Add components that already exist
    ComponentManager.getComponentIds().forEach(componentId => {
        const componentType = ComponentManager.getComponentType(componentId);
        if (componentType === "text-component") {
            createInitialTextComponent(componentContainer, componentId);
        } else if (componentType === "score-component") {
            createInitialScoreComponent(componentContainer, componentId);
        } else {
            throw "Not implemented";
        }
    });
    
    // Bind events for text-components
    ComponentManager.onComponentTextChanged((componentId, newValue) => updateTextComponent(componentContainer, "text", componentId, newValue));
    ComponentManager.onComponentFontSizeChanged((componentId, newValue) => updateTextComponent(componentContainer, "fontSize", componentId, newValue));
}

function createBaseSvg(componentContainer, componentId) {
    // Creates an svg, adds it to the container, and then returns the node which contents should be added to.
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

    componentContainer.appendChild(svg);
    return svg;
}

function getSvgFor(componentContainer, componentId) {
    // Gets the svg node for the given component from the componentContainer.
    return componentContainer.querySelector(`[data-component-id=${componentId}]`);
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
    console.log(instructions);
    const spacing = calculateScoreComponentSpacing(instructions, new Set([instructions]), ComponentManager.getComponentRhythmLengthHint(componentId));
    renderScoreComponentFromInstructionsAndSpacing(svg, instructions, spacing);
    componentContainer.appendChild(svg);
}
