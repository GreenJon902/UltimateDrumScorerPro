// Apparently converting HTML that contains SVGs to PDFs doesn't exist... So I've written it myself.
// Also, respectfully, jsPDF, I don't come from js so I don't know the norm, but yo crap is a mess.

import {ComponentManager} from "./componentManager.js";


const MM_TO_PT = 2.83465;


export function nodeToPDF(node, pdfFileName) {
    // Converts the given node into a PDF.  This will add some metadata which can be loaded by loadMetaFromPDFString;
    // The pdf will be given the given the name `${pdfFileName}.pdf`
    // Note: this requires the jsPDF library, and it requires window.jspdf.jsPDF to exist.
    // Note: this expects the given node to have a size set in style.

    const doc = new window.jspdf.jsPDF({unit: "mm"});

    // Functions to convert from HTML location (in px?) to pdf location (in mm)
    const rootRect = node.getBoundingClientRect();
    const posConvert = (node) => {
        const rect = node.getBoundingClientRect();
        const borderWidth = parseFloat(getComputedStyle(node).borderWidth);  // Account for border width
        
        return {
            x: (rect.x - rootRect.x + borderWidth) / rootRect.width * 210,
            y: (rect.y - rootRect.y + borderWidth) / rootRect.height * 297,
            w: rect.width / rootRect.width * 210,
            h: rect.height / rootRect.height * 297
        };
    };
    
    // Fill content
    addNode(doc, node, posConvert);
    
    // Attach metadata
    addMeta(doc);

    // Open pdf in a new tab
    doc.save(pdfFileName + ".pdf");
}

function addMeta(doc) {
    // Attaches the result of ComponentManager.writeProjectToString to the doc under the namespace "https://github.com/GreenJon902/UltimateDrumScorerPro".
    
    // Get and escape all data
    const stringData = ComponentManager.writeProjectToString();
    const safeStringData = stringData.replace(/[<>&'"]/g, c => {  
        switch (c) {
            case '<': return '&lt;';
            case '>': return '&gt;';
            case '&': return '&amp;';
            case '\'': return '&apos;';
            case '"': return '&quot;';
        }
    });

    // Add to pdf
    doc.addMetadata(safeStringData, "https://github.com/GreenJon902/UltimateDrumScorerPro");
}

export function loadMetaFromPDFString(pdfString) {
    // Loads data written to the pdf by addMeta, this will forward it to ComponentManager.loadProjectFromString.
    // This throws the error string "Malformed PDF" if it fails.

    // Get and unescape data
    const safeStringData = pdfString.match(/https:\/\/github\.com\/GreenJon902\/UltimateDrumScorerPro"><jspdf:metadata>(.*)<\/jspdf:metadata>/);
    if (safeStringData === null) {  // Did we find out custom metadata?
        // Match failed so throw error
        throw "Malformed PDF";
    }
    let stringData = safeStringData[1];  // SafeStringData is a array of groups, so [1] is the group we want
    stringData = stringData.replace(/&lt;/g, '<');
    stringData = stringData.replace(/&gt;/g, '>');
    stringData = stringData.replace(/&amp;/g, '&'); // Must be done before &apos; and &quot;
    stringData = stringData.replace(/&apos;/g, "'");
    stringData = stringData.replace(/&quot;/g, '"');
    
    // Load as current project
    ComponentManager.loadProjectFromString(stringData);
}

function pushTranslation(doc, x, y) {
    // Pushes a translation matrix of (x, y)mm onto the given jsPDF doc.
    // This exists because setCurrentTransformationMatrix actually pushes, and I find the naming unintuative. Also setCurrentTransformationMatrix doesn't use mm, so we need to multiply by doc.internal.scaleFactor.
    // I also find the fact that I need to negate y, but not x, unintuative.
    
    doc.setCurrentTransformationMatrix(doc.Matrix(1, 0, 0, 1, x * doc.internal.scaleFactor, -y * doc.internal.scaleFactor));
}

function pushScale(doc, x, y) {
    // Pushes a scale matrix of SF (x, y)mm onto the given jsPDF doc.
    // This exists because setCurrentTransformationMatrix actually pushes, and I find the naming unintuative.
    
    doc.setCurrentTransformationMatrix(doc.Matrix(x, 0, 0, y, 0, 0));
}


function addNode(doc, node, posConvert) {
    // Add the given node to the document, where width and height are is the size of the whole document.
    //      posConvert(node|[int, int, int, int]) => {x, y, w, h} - Converts the locations of the given node / the [x, y, w, h] to pdf metrics.
    
    // Save state
    doc.saveGraphicsState();  // We do this for two reasons: a) to allow matrixes to be popped. b) to reduce the impact of changing styling settings (like stroke width and fill)
    
    // Extract some information we may need
    let relativeLocation = posConvert(node);

    // If there is a transform then apply it
    if (node.getAttribute("transform") !== null) {
        const transforms = Array.from(
            node.getAttribute("transform")
                .replace(/(?:, *)|(?: +)/, " ")  // Commas or spaces work, so just convert commas to spaces to simplify the regex
                .matchAll(/([a-z]+)\(([[0-9. -]+]*)\)/g));
        
        for (let i=0; i<transforms.length; i++) {
            const transform = transforms[i];
            const args = transform[2].split(" ");
            console.log(transform, args);
            if (transform[1] === "translate") {
                const x = parseFloat(args[0]);
                const y = parseFloat(args[1]);
                pushTranslation(doc, x, y);
            } else if (transform[1] === "scale") {
                const x = parseFloat(args[0]);
                const y = parseFloat(args[1]);
                pushScale(doc, x, y);
            } else {
                throw "Unexpected transform type";
            }
        }
    }

    // Handle the node
    const nodeName = node.nodeName.toUpperCase();
    if (nodeName === "DIV" || nodeName === "G") {  // Run for each child
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
        const matches = node.getAttribute("d").match(/[A-Za-z]|[-0-9\.]+/g);
        let currentX = 0;
        let currentY = 0;
        let lastMoveX, lastMoveY;  // Location just after last move command. Used for path closing
        let currentArgs = [];
        for (let i=0; i<matches.length;) {  // i is incremented in loop
            // Get all instruction information
            const c = matches[i];
            i++;

            currentArgs = [];  // Empty array
            while (i<matches.length && matches[i].match(/[A-Za-z]/) === null) {  // While more matches left and match ins't a char
                currentArgs.push(parseFloat(matches[i]));
                i++;
            }
            
            // Handle instruction
            if (c === "M") {  // Absolute move
                currentX = currentArgs[0];
                currentY = currentArgs[1];
                lastMoveX = currentX;
                lastMoveY = currentY;
            } else if (c === "m") {  // Relative move
                currentX += currentArgs[0];
                currentY += currentArgs[1];      
                lastMoveX = currentX;
                lastMoveY = currentY;
            } else if (c === "L") {  // Absolute line
                doc.line(currentX, currentY, currentArgs[0], currentArgs[1]);
                currentX = currentArgs[0];
                currentY = currentArgs[1];      
            } else if (c === "l") {  // Relative line
                doc.line(currentX, currentY, currentX + currentArgs[0], currentY + currentArgs[1]);
                currentX += currentArgs[0];
                currentY += currentArgs[1];      
            } else if (c === "A") {  // Absolute arc
                 
                // PDF doesn't support arc, so we convert to a bezier
                const bezier = arcToBezier(currentX, currentY, currentArgs[0], currentArgs[1], currentArgs[2], currentArgs[3], currentArgs[4], currentArgs[5], currentArgs[6]);         
                // Convert bezier to the format doc.path uses
                const path = [{ op: "m", c: [currentX, currentY] }];  // Move to current coordinates
                for (let bezI = 0; bezI < bezier.length / 6; bezI++) {
                    path.push({ op: "c", c: bezier.slice(bezI * 6, bezI * 6 + 6) });  // Add the 6 control points of the bezier
                }
                
                // Draw and move currentX, currentY
                doc.path(path, "S");
                doc.line(0, 0, 0, 0);  // For some reason the path doesn't draw correctly without this
                currentX = currentArgs[5];
                currentY = currentArgs[6];
                
            } else if (c === "Q") {  // Absolute bezier
                doc.lines([[0, 0, currentArgs[0] - currentX, currentArgs[1] - currentY, currentArgs[2] - currentX, currentArgs[3] - currentY]], currentX, currentY);  // Subtract currentX and currentY as points are all relative to initial coords (currentX, currentY)
                currentX = currentArgs[2];
                currentY = currentArgs[3];
            } else if (c === "q") {  // Relative bezier
                doc.lines([[0, 0, currentArgs[0], currentArgs[1], currentArgs[2], currentArgs[3]]], currentX, currentY);
                currentX += currentArgs[2];
                currentY += currentArgs[3];
            } else if (c === "z" || c === "Z") {  // Close path
                doc.line(currentX, currentY, lastMoveX, lastMoveY);
                currentX = lastMoveX;
                currentY = lastMoveY;
            } else {
                throw "Unexpected path character";
            }
            
                  
        }
    } else if (nodeName === "USE") {  // Translate, then run for children of def
        addNode(doc, document.querySelector(node.getAttribute("href")), posConvert);
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
        const isBold = getDeclaredCSSProperty(node, "font-weight") === "bold";
        const isItalic = getDeclaredCSSProperty(node, "font-style") === "italic";
        doc.setFont("helvetica", (isBold ? "bold" : "") + (isItalic ? "italic" : ""));
        doc.setFontSize(((node.style.fontSize === "") ? 5 : parseFloat(node.style.fontSize)) * MM_TO_PT);  // Default font-size=5
        // Get location
        let x = parseFloat(node.getAttribute("x"));
        if (isNaN(x)) {x = 0;}  // If no location specified then x is NaN
        let y = parseFloat(node.getAttribute("y"));
        if (isNaN(y)) {y = 0;}
        // Draw text
        doc.text(node.innerHTML, x, y, {align: "center", baseline: "middle"});
        
    } else if (nodeName === "DEFS") {
        // We skip defs because these are added in-place when a "USE" node us handled
    } else {
        throw "Unexpected node type";
    }
    
    // Restore state
    doc.restoreGraphicsState();
}

function getDeclaredCSSProperty(element, propertyName) {
    // Returns the value behind propertyName or null if it doesn't exit.
    // This will only look at values explictly defined by me (e.g. inline css + classes + etc.).

    function getInDeclaration(declaration, propertyName) {
        // Returns the value behind propertyName in a given CSSDeclaration, else null.
        const val = declaration.getPropertyValue(propertyName);
        if (val === "") {
            return null;
        } else {
            return val;
        }
    }
    
    // First search in inline-css
    const value = getInDeclaration(element.style, propertyName);
    if (value !== null) {
        return value;
    }

    // Search in styles-sheets
    for (let i = 0; i<document.styleSheets.length; i++) {
        const styleSheet = document.styleSheets[i];
        for (let j = 0; j<styleSheet.cssRules.length; j++) {
            const cssRule = styleSheet.cssRules[j];

            // Check if this rule applies to element
            if (!element.matches(cssRule.selectorText)) {
                continue;
            }
            
            // Check if the property is set
            const value = getInDeclaration(cssRule.style, propertyName);
            if (value !== null) {
                return value;
            }
        }
    }

    // Not found so return null
    return null;
}

function arcToBezier(x1, y1, rx, ry, angle, large_arc_flag, sweep_flag, x2, y2, recursive) {
    // THIS IS NOT MY CODE, THIS IS TAKEN FROM:
    //      https://github.com/DmitryBaranovskiy/raphael/blob/ea2562a6290c0a158c3db09f5c55042d6870c17c/dev/raphael.core.js#L1837
    // The recursive parameter is not given, it is used internally.
    // This returns absolute coordinates for control points in groups of six:
    //      So [x11, y11, x12, y12, x13, y13, x21, y21, 22, y22, x23, y23, ...]
    
    const math = Math;
    const abs = Math.abs;
    const PI = math.PI;
    const a2c = arcToBezier;
    const concat = "concat";
    const split = "split";

    // for more information of where this math came from visit:
    // http://www.w3.org/TR/SVG11/implnote.html#ArcImplementationNotes
    var _120 = PI * 120 / 180,
        rad = PI / 180 * (+angle || 0),
        res = [],
        xy,
        rotate = /*cacher*/(function (x, y, rad) {
            var X = x * math.cos(rad) - y * math.sin(rad),
                Y = x * math.sin(rad) + y * math.cos(rad);
            return {x: X, y: Y};
        });
    if (!recursive) {
        xy = rotate(x1, y1, -rad);
        x1 = xy.x;
        y1 = xy.y;
        xy = rotate(x2, y2, -rad);
        x2 = xy.x;
        y2 = xy.y;
        var cos = math.cos(PI / 180 * angle),
            sin = math.sin(PI / 180 * angle),
            x = (x1 - x2) / 2,
            y = (y1 - y2) / 2;
        var h = (x * x) / (rx * rx) + (y * y) / (ry * ry);
        if (h > 1) {
            h = math.sqrt(h);
            rx = h * rx;
            ry = h * ry;
        }
        var rx2 = rx * rx,
            ry2 = ry * ry,
            k = (large_arc_flag == sweep_flag ? -1 : 1) *
                math.sqrt(abs((rx2 * ry2 - rx2 * y * y - ry2 * x * x) / (rx2 * y * y + ry2 * x * x))),
            cx = k * rx * y / ry + (x1 + x2) / 2,
            cy = k * -ry * x / rx + (y1 + y2) / 2,
            f1 = math.asin(((y1 - cy) / ry).toFixed(9)),
            f2 = math.asin(((y2 - cy) / ry).toFixed(9));

        f1 = x1 < cx ? PI - f1 : f1;
        f2 = x2 < cx ? PI - f2 : f2;
        f1 < 0 && (f1 = PI * 2 + f1);
        f2 < 0 && (f2 = PI * 2 + f2);
        if (sweep_flag && f1 > f2) {
            f1 = f1 - PI * 2;
        }
        if (!sweep_flag && f2 > f1) {
            f2 = f2 - PI * 2;
        }
    } else {
        f1 = recursive[0];
        f2 = recursive[1];
        cx = recursive[2];
        cy = recursive[3];
    }
    var df = f2 - f1;
    if (abs(df) > _120) {
        var f2old = f2,
            x2old = x2,
            y2old = y2;
        f2 = f1 + _120 * (sweep_flag && f2 > f1 ? 1 : -1);
        x2 = cx + rx * math.cos(f2);
        y2 = cy + ry * math.sin(f2);
        res = a2c(x2, y2, rx, ry, angle, 0, sweep_flag, x2old, y2old, [f2, f2old, cx, cy]);
    }
    df = f2 - f1;
    var c1 = math.cos(f1),
        s1 = math.sin(f1),
        c2 = math.cos(f2),
        s2 = math.sin(f2),
        t = math.tan(df / 4),
        hx = 4 / 3 * rx * t,
        hy = 4 / 3 * ry * t,
        m1 = [x1, y1],
        m2 = [x1 + hx * s1, y1 - hy * c1],
        m3 = [x2 + hx * s2, y2 - hy * c2],
        m4 = [x2, y2];
    m2[0] = 2 * m1[0] - m2[0];
    m2[1] = 2 * m1[1] - m2[1];
    if (recursive) {
        return [m2, m3, m4][concat](res);
    } else {
        res = [m2, m3, m4][concat](res).join()[split](",");
        var newres = [];
        for (var i = 0, ii = res.length; i < ii; i++) {
            newres[i] = i % 2 ? rotate(res[i - 1], res[i], rad).y : rotate(res[i], res[i + 1], rad).x;
        }
        return newres;
    }
}
