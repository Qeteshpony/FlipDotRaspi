const pixelPadding = 2;
let pixelSize = 25;
let pixelarray = [];
let lastchange = 0;
let pixelChanges = [];
let textboxtext = "";
let sendTimeout = -1;

const canvas = document.createElement('canvas');
const context = canvas.getContext('2d');

const getPixelPos = (event) => {
    const rect = canvas.getBoundingClientRect();
    const absoluteX = event.clientX - rect.left;
    const absoluteY = event.clientY - rect.top;

    return {
        x: Math.floor(absoluteX / pixelSize),
        y: Math.floor(absoluteY / pixelSize),
    }
}

const drawPixel = async (x, y, mode, save) => {
    context.fillStyle = mode === '1' ? 'yellow' : '#151515';

    context.beginPath();
    context.arc(
        x * pixelSize + pixelSize / 2,
        y * pixelSize + pixelSize / 2,
        (pixelSize - pixelPadding) / 2,
        0,
        2 * Math.PI,
        false
    );
    context.fill();
    context.lineWidth = pixelPadding;
    context.strokeStyle = '#000000';
    context.stroke();

    if (save) {
        pixelarray[y][x] = mode;
        pixelChanges.push({"x": x, "y": y, "c": mode});
        if (sendTimeout === -1) {
            sendTimeout = setTimeout(async () => {
                sendTimeout = -1;
                const changes = pixelChanges;
                pixelChanges = [];
                await postData({"setpixel": changes});
            }, 100)
        }

    }
    updateColValue(x);

}

const columnValue = (column) => {
    let val = 0;
    for (let row=0; row < pixelarray.length; row++) {
        val += (2 ** row) * parseInt(pixelarray[row][column], 10);
    }
    return val.toString(16).padStart(2, "0").toUpperCase();
}

const updateColValue = (column) => {
    document.getElementById("colVal"+column).textContent = columnValue(column);
}

const updatePixels = async () => {
    const statusResponse = await fetch('/pixels');
    const status = await statusResponse.text();
    pixelarray = status.split('\n').map(row => row.split(''));
}

const drawPixels = async () => {
    for (let y = 0; y < pixelarray.length; ++y) {
        for (let x = 0; x < pixelarray[0].length; ++x) {
            void await drawPixel(x, y, pixelarray[y][x], false);
        }
    }
};

const postData = async (data = {}) => {
  const response = await fetch('/json/', {
    method: 'POST', // *GET, POST, PUT, DELETE, etc.
    cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
    credentials: 'same-origin', // include, *same-origin, omit
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data) // body data type must match "Content-Type" header
  });
  return response.json(); // parses JSON response into native JavaScript objects
};

const updateCanvas = async () => {
    if (lastchange + 1 < Math.floor(Date.now() / 1000)) {
        await updatePixels();
        await drawPixels(context);
    }
};

const createCanvas = async () => {
    const display = document.getElementById('display');
    canvas.id = "displaycanvas";
    display.appendChild(canvas);

    // await updatePixels();
    let wwidth = window.innerWidth - 20;
    pixelSize = Math.floor(wwidth / pixelarray[0].length)

    canvas.width = pixelarray[0].length * pixelSize;
    canvas.height = pixelarray.length * pixelSize;

    context.fillStyle = 'black';
    context.fillRect(0, 0, canvas.width, canvas.height);

    // create value table
    const values = document.createElement('div');
    values.id = "values";
    display.appendChild(values);
    for (let i = 0; i < pixelarray[0].length; i++) {
        const valuecell = document.createElement('span');
        valuecell.className = "valuecell";
        valuecell.style.position = "fixed";
        valuecell.style.top = (canvas.height + pixelSize / 2 + 20).toString() + "px";
        valuecell.style.left = (i * pixelSize + Math.floor(pixelSize / 2)).toString() + "px";
        if (pixelSize < 15) valuecell.style.fontSize = "0";
        values.appendChild(valuecell);

        const prefix = document.createElement('span');
        prefix.className = "prefix";
        prefix.textContent = "\\x";
        valuecell.appendChild(prefix);

        const value = document.createElement('span');
        value.id = "colVal" + i.toString();
        value.className = "value";
        value.textContent = columnValue(i);
        valuecell.appendChild(value);
    }

    // create col-numbers
    const colnums = document.createElement('div');
    colnums.id = "colnums";
    display.appendChild(colnums);
    for (let i = 0; i < pixelarray[0].length; i++) {
        const colnumscell = document.createElement('span');
        colnumscell.className = "colnumscell";
        colnumscell.style.position = "fixed";
        colnumscell.style.top = (canvas.height + pixelSize / 2).toString() + "px";
        colnumscell.style.left = (i * pixelSize + Math.floor(pixelSize / 2)).toString() + "px";
        colnums.appendChild(colnumscell);

        const value = document.createElement('span');
        value.id = "colVal" + i.toString();
        value.className = "value";
        let valstr = i.toString();
        if (i < 10) valstr = "0" + valstr
        value.textContent = valstr;
        colnumscell.appendChild(value);
    }

    await drawPixels();
};

const addCanvasListeners = async () => {
    let drawingMode = null;

    canvas.addEventListener('mousedown', event => {
        document.getElementById("draw").click()
        const pixelPos = getPixelPos(event);
        drawingMode = pixelarray[pixelPos.y][pixelPos.x] === '1' ? '0' : '1';
        pixelarray[pixelPos.y][pixelPos.x] = drawingMode;

        void drawPixel(pixelPos.x, pixelPos.y, pixelarray[pixelPos.y][pixelPos.x], true);
    });

    canvas.addEventListener('mousemove', event => {
        if (drawingMode === null) {
            return;
        }

        lastchange = Math.floor(Date.now() / 1000);

        const pixelPos = getPixelPos(event);

        if (pixelarray[pixelPos.y][pixelPos.x] === drawingMode) {
            return;
        }

        pixelarray[pixelPos.y][pixelPos.x] = drawingMode;
        void drawPixel(pixelPos.x, pixelPos.y, pixelarray[pixelPos.y][pixelPos.x], true);
    });

    window.addEventListener('mouseup', () => {
        drawingMode = null;
    });

    window.addEventListener('mouseleave', () => {
        drawingMode = null;
    });
};

const createControls = async () => {
    const modes = ['Draw', 'Dayclock', 'Text'];
    let mode = "dayclock";

    const controls = document.getElementById('controls');
    controls.style.position = 'fixed';
    controls.style.top = (canvas.height + 50).toString() + "px";

    // Create mode switcher
    let modediv = document.createElement('div');
    modediv.id = "modediv";
    let intervalid = 0;
    controls.appendChild(modediv);

    // Create radio-buttons for mode switcher
    for (let i=0; i < modes.length; i++) {
        const radio = document.createElement('input');
        radio.name = 'mode';
        radio.id = modes[i].toLowerCase();
        radio.type = 'radio';
        radio.addEventListener('input', async () => {
            await postData({"mode": radio.id});
            mode = radio.id;
            //if (mode === "dayclock") intervalid = setInterval(updateCanvas, 1000, context);
            //else clearInterval(intervalid);
        });
        const label = document.createElement('label');
        label.htmlFor = modes[i];
        label.innerText = modes[i];
        const br = document.createElement('br');
        modediv.appendChild(radio);
        modediv.appendChild(label);
        modediv.appendChild(br);
    }

    // Create Text-Input
    const textdiv = document.createElement('div');
    textdiv.id = "textdiv";
    controls.appendChild(textdiv);
    const textbox = document.createElement('input');
    textbox.type = 'text';
    textbox.id = 'textbox';
    textbox.width = Math.floor(pixelarray[0].length / 4);
    textbox.maxLength = Math.floor(pixelarray[0].length / 2);
    textbox.placeholder = "Enter your Text here"

    textbox.addEventListener('input', async () => {
        document.getElementById("text").click()
        textboxtext = textbox.value;
        if (sendTimeout === -1) {
            sendTimeout = setTimeout(async () => {
                sendTimeout = -1;
                await postData({"text": {"text": textboxtext}});
                await updateCanvas();
            }, 250)
        }
    });
    textdiv.appendChild(textbox);
    const br = document.createElement('br');
    textdiv.appendChild(br);

    // Alignment- and Font-Selector
    const alignment = document.createElement('select');
    alignment.id = "alignment";
    alignment.addEventListener('input', async event => {
        await postData({"text": {"align": event.target.value}});
        await updateCanvas(context);
    })
    textdiv.appendChild(alignment);
    const alignments = ["left", "center", "right"];
    for (let i=0; i < alignments.length; i++) {
        const option = document.createElement('option');
        option.value = alignments[i];
        option.text = alignments[i];
        alignment.appendChild(option);
    }

    const fontselect = document.createElement('select');
    fontselect.id = "fontselect";
    fontselect.addEventListener('input', async event => {
        await postData({"text": {"font": event.target.value}});
        await updateCanvas(context);
    });
    textdiv.appendChild(fontselect);

    const initstate = await postData({'mode': null, 'text': null, 'fonts': null});
    document.getElementById(initstate['mode']).checked = true;
    document.getElementById('alignment').value = initstate["text"]["align"];
    document.getElementById('textbox').value = initstate["text"]["text"];

    for (let i=0; i < initstate["fonts"].length; i++) {
        const option = document.createElement('option');
        option.value = initstate["fonts"][i];
        option.text = initstate["fonts"][i];
        fontselect.appendChild(option);
    }
    document.getElementById('fontselect').value = initstate["text"]["font"];

    // Create buttons for filling the canvas
    const filldiv = document.createElement('div');
    filldiv.id = "filldiv";
    controls.appendChild(filldiv)
    const allon = document.createElement('input');
    allon.name = "allon";
    allon.id = "allon";
    allon.type = "button";
    allon.value = "All on"
    allon.addEventListener("mousedown", async () => {
        document.getElementById("draw").click();
        await postData({"fill": 1});
        await updateCanvas();
    });
    filldiv.appendChild(allon);

    const alloff = document.createElement('input');
    alloff.name = "alloff";
    alloff.id = "alloff";
    alloff.type = "button";
    alloff.value = "All off"
    alloff.addEventListener("mousedown", async () => {
        document.getElementById("draw").click();
        await postData({"fill": 0});
        await updateCanvas();
    });
    filldiv.appendChild(alloff);

};


document.addEventListener('DOMContentLoaded', async () => {
    await updatePixels();
    await createCanvas();
    await addCanvasListeners();
    await createControls();
    setInterval(updateCanvas, 1000);

    window.addEventListener('resize', async () => {
        console.log("Redraw");
        const c = document.getElementById('displaycanvas');
        const v = document.getElementById('values');
        c.remove();
        v.remove();
        await createCanvas();
    });
});


