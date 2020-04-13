let socket = io.connect('http://localhost:4000');

// ========== THREE.JS SETUP ==========
let scene = new THREE.Scene();
let camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
let renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// ========== FUNCTIONS ==========
function keyDown(event) {
    let key = keyNames[event.which];
    if (!inputs['keyboard'].includes(key)) {
        inputs['keyboard'].push(key);
    }
}

function keyUp(event) {
    let key = keyNames[event.which];
    inputs['keyboard'] = inputs['keyboard'].filter(item => item !== key);
}

// ========== START ==========
var geometry = new THREE.BoxGeometry();
var material = new THREE.MeshBasicMaterial( { color: 0x00ff00 } );
var cube = new THREE.Mesh( geometry, material );
scene.add( cube );
camera.position.z = 5;

let inputs = {
    'keyboard': [],
    'mouseX': 0,
    'mouseY': 0
};

document.addEventListener('keydown', keyDown, false);
document.addEventListener('keyup', keyUp, false);
// document.addEventListener('mousemove', mouseMove, false);

function update() {
    requestAnimationFrame(update);



    renderer.render(scene, camera);
}
update();
