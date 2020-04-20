let socket = io.connect('http://localhost:4000');

// ========== FUNCTIONS ==========
let inGame = false;

function keyDown(event) {
    let key = keyNames[event.which];
    if (!inputs['keyboard'].includes(key)) {
        inputs['keyboard'].push(key);
        socket.emit('inputs', inputs);
    }
    if (key === 'enter') {
        lockPointer();
    }
}

function keyUp(event) {
    let key = keyNames[event.which];
    inputs['keyboard'] = inputs['keyboard'].filter(item => item !== key);
    socket.emit('inputs', inputs);
}


function mouseMove(event) {

    if (!inGame) { return; }

    let euler = new THREE.Euler( 0, 0, 0, 'YXZ' );

    let movementX = event.movementX;
    let movementY = event.movementY;

    euler.setFromQuaternion( camera.quaternion );

    euler.y -= movementX * 0.002;
    euler.x -= movementY * 0.002;

    euler.x = Math.max( - Math.PI / 2, Math.min( Math.PI / 2, euler.x ) );

    camera.quaternion.setFromEuler( euler );

    inputs['pitch'] = euler.x;
    inputs['yaw'] = euler.y;
}

function mouseDown(event) {
}

function pointerLockStatus() {
    inGame = document.pointerLockElement != null;
}

function lockPointer() {
    renderer.domElement.requestPointerLock();
}

function loadSkybox() {
    let textures = [];
    let texture_bt = new THREE.TextureLoader().load('textures/skybox_bt.png');
    let texture_sd = new THREE.TextureLoader().load('textures/skybox_sd.png');
    let texture_tp = new THREE.TextureLoader().load('textures/skybox_tp.png');

    textures.push(new THREE.MeshBasicMaterial({ map : texture_sd }));
    textures.push(new THREE.MeshBasicMaterial({ map : texture_sd }));
    textures.push(new THREE.MeshBasicMaterial({ map : texture_tp }));
    textures.push(new THREE.MeshBasicMaterial({ map : texture_bt}));
    textures.push(new THREE.MeshBasicMaterial({ map : texture_sd }));
    textures.push(new THREE.MeshBasicMaterial({ map : texture_sd }));

    for (let i = 0; i < 6; i++) { textures[i].side = THREE.BackSide; }

    let skyboxGeometry = new THREE.BoxGeometry( 10000, 10000, 10000);
    let skybox = new THREE.Mesh(skyboxGeometry, textures);
    scene.add(skybox);
}

// ========== START ==========
let scene = new THREE.Scene();
let camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 30000);
let renderer = new THREE.WebGLRenderer({antialias : true});
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

let geometry = new THREE.BoxGeometry();
let material = new THREE.MeshBasicMaterial( { color: 0x00ff00 } );
let cube = new THREE.Mesh( geometry, material );
scene.add( cube );
camera.position.z = 5;

let connection = ":NOT CONNECTED:";
let socketStatus = "..."
let frameConnected = 0;
let frameDataReceived = 0;
let frameDelay = 0;

loadSkybox();

let inputs = {
    'keyboard': [],
    'actions': [],
    'pitch': 0,
    'yaw': 0
};

socket.on('update',  function (data) {
    console.log('update received!')
    socket.emit('updateBack', data)
});

socket.on('player',  function (data) {
    frameDataReceived++;
    connection = ":CONNECTED?: (" + frameConnected + "." + frameDataReceived + " frames) data: "
    let parsedData = JSON.parse(data);
    if (parsedData['sid'] === socket.id) {
        frameConnected++;
        connection = ":CONNECTED: (" + frameConnected + " frames) data: "+ parsedData;
    }
});

document.addEventListener('keydown', keyDown, false);
document.addEventListener('keyup', keyUp, false);
document.addEventListener('mousedown', mouseDown, false);
document.addEventListener('mousemove', mouseMove, false);
document.addEventListener('pointerlockchange', pointerLockStatus, false);

function update() {
    requestAnimationFrame(update);

    document.getElementById("debugInfo").innerHTML = "==== DEBUG INFORMATION ==== <br> SID: " + socket.id + "<br> KEYBOARD: " + inputs['keyboard'] + "<br>CONNECTION: " + connection + "<br>SOCKET STATUS: " + socketStatus;

    renderer.render(scene, camera);
}
update();
socket.on('connect', () => {
    socketStatus = "Connected!"
});


socket.on('error', (error) => {
    socketStatus = "ER " + error;
});

socket.on('disconnect', (reason) => {
    socketStatus = "DC " + reason;
});

socket.on('reconnect', (attemptNumber) => {
    socketStatus = "RC! " + attemptNumber;
});

socket.on('reconnect_attempt', (attemptNumber) => {
    socketStatus = "RCA " + attemptNumber;
});

socket.on('reconnecting', (attemptNumber) => {
    socketStatus = "RC " + attemptNumber;
});

socket.on('reconnect_error', (error) => {
    socketStatus = "RE " + error;
});

socket.on('reconnect_failed', () => {
    socketStatus = "Reconnect Failed"
});