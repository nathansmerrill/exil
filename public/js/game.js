let socket = io.connect('http://localhost:4000');

// ========== FUNCTIONS ==========
let inGame = false;

function keyDown(event) {
    let key = keyNames[event.which];
    if (!inputs.keyboard.includes(key)) {
        inputs.keyboard.push(key);
        socket.emit('inputs', inputs);
    }
    if (key === 'enter') {
        lockPointer();
    }
}

function keyUp(event) {
    let key = keyNames[event.which];
    inputs.keyboard = inputs.keyboard.filter(item => item !== key);
    socket.emit('inputs', inputs);
}

function mouseMove(event) {

    if (!inGame) { return; }

    let euler = new THREE.Euler( 0, 0, 0, 'YXZ' );

    let movementX = event.movementX;
    let movementY = event.movementY;

    euler.setFromQuaternion( camera.quaternion );

    euler.y -= movementX * 0.002; // yaw
    euler.x -= movementY * 0.002; // pitch

    euler.x = Math.max( - Math.PI / 2, Math.min( Math.PI / 2, euler.x ) );

    camera.quaternion.setFromEuler( euler );

    inputs.pitch = euler.x;
    inputs.yaw = euler.y;

    socket.emit('inputs', inputs);
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

let waterPlane = new THREE.PlaneGeometry(10000,10000);
let waterMaterial = new THREE.MeshBasicMaterial( {transparent:true, color:0x86caed, opacity:0.8} );
let water = new THREE.Mesh(waterPlane, waterMaterial);
scene.add( water );
water.quaternion.setFromEuler(new THREE.Euler(- Math.PI / 2, 0, 0, 'YXZ'));

let globalPlayers = {};
let globalPlayerObjects = {};

let localPlayer = {
    x: 0,
    y: 0,
    z: 0,
};

let c = document.getElementById("uiCanvas");
let ctx = c.getContext("2d");
ctx.beginPath();
ctx.arc(95, 50, 40, 0, 4 * Math.PI);
ctx.stroke();

loadSkybox();

let inputs = {
    keyboard: [],
    actions: [],
    pitch: 0,
    yaw: 0
};

socket.on('players',  function (data) {
    for (let sid in data) {
        if (sid === socket.id) { // Received Data for Self
            localPlayer.x = data[sid].x;
            localPlayer.y = data[sid].y;
            localPlayer.z = data[sid].z;
        } else { // Received Data for Other Player
            if (globalPlayers[sid] == null) { // Make Player Object
                let plyGeometry = new THREE.BoxGeometry(1,1,1);
                let plyMaterial = new THREE.MeshBasicMaterial({ color : 0xbbffbb });
                globalPlayerObjects[sid] = new THREE.Mesh(plyGeometry, plyMaterial);
                globalPlayerObjects[sid].name = sid;
                scene.add(globalPlayerObjects[sid]);
            }
            globalPlayers[sid] = data[sid];
        }
    }
});

document.addEventListener('keydown', keyDown, false);
document.addEventListener('keyup', keyUp, false);
document.addEventListener('mousedown', mouseDown, false);
document.addEventListener('mousemove', mouseMove, false);
document.addEventListener('pointerlockchange', pointerLockStatus, false);

function update() {
    requestAnimationFrame(update);

    camera.position.x = localPlayer.x;
    camera.position.y = localPlayer.y;
    camera.position.z = localPlayer.z;

    for (let sid in globalPlayers) {
        if (globalPlayerObjects[sid] !== null) {
            let pos = new THREE.Vector3(globalPlayers[sid].x, globalPlayers[sid].y, globalPlayers[sid].z);
            globalPlayerObjects[sid].position.x = pos.x;
            globalPlayerObjects[sid].position.y = pos.y;
            globalPlayerObjects[sid].position.z = pos.z;
            let rotEuler = new THREE.Euler( 0, 0, 0, 'YXZ');
            rotEuler.x = globalPlayers[sid].inputs.pitch;
            rotEuler.y = globalPlayers[sid].inputs.yaw;
            globalPlayerObjects[sid].quaternion.setFromEuler(rotEuler);
            console.log(globalPlayerObjects[sid]);
            console.log(pos);
        }
    }

    renderer.render(scene, camera);
}
update();