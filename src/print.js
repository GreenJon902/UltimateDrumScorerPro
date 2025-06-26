// Apparently converting HTML that contains SVGs to PDFs doesn't exist... So I've written it myself.
// Also, respectfully, jsPDF, I don't come from js so I don't know the norm, but yo crap is a mess.

const MM_TO_PT = 2.83465;


export function nodeToPDF(node) {
    // Converts the given node into a PDF.
    // Note: this requires the jsPDF library, and it requires window.jspdf.jsPDF to exist.
    // Note: this expects the given node to have a size set in style.

    const doc = new window.jspdf.jsPDF({unit: "mm"});

    // Functions to convert from HTML location (in px?) to pdf location (in mm)
    const rootRect = node.getBoundingClientRect();
    const posConvert = (node) => {
        const rect = node.getBoundingClientRect();
        
        return {
            x: (rect.x - rootRect.x) / rootRect.width * 210,
            y: (rect.y - rootRect.y) / rootRect.height * 297,
            w: rect.width / rootRect.width * 210,
            h: rect.height / rootRect.height * 297
        };
    };
    
    // Fill content
    addNode(doc, node, posConvert);

    // Open pdf in a new tab
    doc.save("pdf.pdf");
}

function pushTranslation(doc, x, y) {
    // Pushes a translation matrix of (x, y)mm onto the given jsPDF doc.
    // This exists because setCurrentTransformationMatrix actually pushes, and I find the naming unintuative. Also setCurrentTransformationMatrix doesn't use mm, so we need to multiply by doc.internal.scaleFactor.
    // I also find the fact that I need to negate y, but not x, unintuative.
    
    doc.setCurrentTransformationMatrix(doc.Matrix(1, 0, 0, 1, x * doc.internal.scaleFactor, -y * doc.internal.scaleFactor));
}


function addNode(doc, node, posConvert) {
    // Add the given node to the document, where width and height are is the size of the whole document.
    //      posConvert(node|[int, int, int, int]) => {x, y, w, h} - Convert the locations of the given node / the [x, y, w, h] to pdf metrics.
    
    // Save state
    doc.saveGraphicsState();  // We do this for two reasons: a) to allow matrixes to be popped. b) to reduce the impact of changing styling settings (like stroke width and fill)
    
    // Extract some information we may need
    let relativeLocation = posConvert(node);

    // If there is a transform then apply it
    if (node.getAttribute("transform") !== null) {
        const transform = node.getAttribute("transform").match("^([a-z]+)\\(([[0-9. -]+]*)\\)$");
        const args = transform[2].split(" ");
        if (transform[1] === "translate") {
            const x = parseFloat(args[0]);
            const y = parseFloat(args[1]);
            pushTranslation(doc, x, y);
        } else {
            throw "Unexpected transform type";
        }
    }

    // Handle the node
    const nodeName = node.nodeName.toUpperCase();
    if (nodeName === "DIV") {  // Run for each child
        Array.from(node.children).forEach(childNode => addNode(doc, childNode, posConvert));
    } else if (nodeName === "SVG") {  // Translate, then run for each child
        // Account for left and top of svg
        pushTranslation(doc, relativeLocation.x, relativeLocation.y);  // TODO: Account for border width
        // Account for viewbox of svg
        const viewbox = node.getAttribute("viewBox").split(" ").map(n => parseFloat(n));
        pushTranslation(doc, -viewbox[0], -viewbox[1]);
        // TODO: Size of viewbox
        // Draw children
        Array.from(node.children).forEach(childNode => addNode(doc, childNode, posConvert));
    } else if (nodeName === "PATH") {  // Convert path to a bunch of individual lines
        // Set up styling
        doc.setLineWidth(1);

        // Hope the path is correctly formed... and then just parse it
        const matches = node.getAttribute("d").matchAll("([a-zA-Z]) *([-0-9.]+) +([-0-9.]+)");
        let currentX = 0;
        let currentY = 0;
        for (let match of matches) {
            const c = match[1];  // The character (e.g. M, l)
            const argX = parseFloat(match[2]);
            const argY = parseFloat(match[3]);
            
            if (c === "M") {  // Absolute move
                currentX = argX;
                currentY = argY;
            } else if (c === "m") {  // Relative move
                currentY += argY;
                currentX += argX;      
            } else if (c === "L") {  // Absolute line
                doc.line(currentX, currentY, argX, argY);
                currentY = argY;
                currentX = argX;      
            } else if (c === "l") {  // Relative line
                doc.line(currentX, currentY, currentX + argX, currentY + argY);
                currentY += argY;
                currentX += argX;      
            } else {
                throw "Unexpected path character";
            }
            
                  
        }
    } else if (nodeName === "USE") {  // Translate, then run for children of def
        Array.from(document.querySelector(node.getAttribute("href")).children).forEach(childNode => addNode(doc, childNode, posConvert));
    } else if (nodeName === "CIRCLE") {  // Just draw a circle, with/without a fill as required
        // Set up styling
        const computedStyle = getComputedStyle(node);
        doc.setLineWidth((computedStyle.stroke === "none") ? 0 : 1);  // If no stroke then width is 0 too, else assume stroke width 1mm
        const circleStyle = (computedStyle.fill === "none") ? "S" : "DF";  // S for stroke-only, DF for fill then stroke
        // Get sizing
        const cx = parseFloat(node.getAttribute("cx"));
        const cy = parseFloat(node.getAttribute("cy"));
        const r = parseFloat(node.getAttribute("r"));
        // Draw circle
        doc.circle(cx, cy, r, circleStyle);
    } else if (nodeName === "TEXT") {
        // Set up styling
        doc.setFont("helvetica", "bolditalic");
        doc.setFontSize(((node.style.fontSize === "") ? 5 : parseFloat(node.style.fontSize)) * MM_TO_PT);  // Default font-size=5
        // Get location
        let x = parseFloat(node.getAttribute("x"));
        if (isNaN(x)) {x = 0;}  // If no location specified then x is NaN
        let y = parseFloat(node.getAttribute("y"));
        if (isNaN(y)) {y = 0;}
        // Draw text
        doc.text(node.innerHTML, x, y, {align: "center", baseline: "middle"});
        
    } else {
        throw "Unexpected node type";
    }
    
    // Restore state
    doc.restoreGraphicsState();
}
