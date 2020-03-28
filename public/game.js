let socket = io.connect('http://localhost:4000');

// ========== FUNCTIONS ==========
// ========== START ==========
let scene = new THREE.Scene();
let camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
let renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

function update() {
    requestAnimationFrame(update);



    renderer.render(scene, camera);
}
update();