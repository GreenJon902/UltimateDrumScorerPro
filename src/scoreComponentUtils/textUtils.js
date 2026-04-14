const TEST_SVG_ID = "textHelperTestSvg";

function checkInitTextHelper() {
    // Checks if the test svg - used to calculate size of text - has been created, if not then creates it.
    
    if (!document.getElementById(TEST_SVG_ID)) {
        // Test div does not exist so create a new one
        const testSvg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        testSvg.setAttribute("id", TEST_SVG_ID);
        testSvg.style.setProperty("visibility", "hidden");
        document.body.appendChild(testSvg);
    }
}

function getTestSvg() {
    // Gets the test svg div. This will run checkInitTextHelper.
    checkInitTextHelper();
    return document.getElementById(TEST_SVG_ID);
}

export function calculateRenderedTextSize(createFunc, text) {
    // Returns the {sizeLeft, sizeUp, sizeRight, sizeDown} of the rendered text.
    // Note, this must not already be added to the DOM.
    // createFunc(svg, svg, text, [0, 0]) takes the text and optionally the coordinates and adds and returns a node in the svg namespace (but not an svg).

    const svg = getTestSvg();
    const node = createFunc(svg, svg, text, 0, 0);
    const bbox = node.getBBox();
    node.remove();
    return {
        sizeLeft: -bbox.x,
        sizeRight: bbox.x + bbox.width,
        sizeUp: -bbox.y,
        sizeDown: bbox.y + bbox.height
    };
}
