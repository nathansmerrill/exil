let socket = io.connect('http://localhost:4000');

// ========== FUNCTIONS ==========

function getUsernamePassword() {
    return {
        'username': $('#username').val(),
        'password': $('#password').val()
    }
}

// ========== START ==========

let scene = new THREE.Scene();
let camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
let renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);

$('#signup').hide();
$('#game').hide().append(renderer.domElement);
$('#loginButton').click(function() {
    socket.emit('login', getUsernamePassword());
});
$('#signupButton').click(function() {
    socket.emit('signup', getUsernamePassword());
});

function update() {
    requestAnimationFrame(update);

    renderer.render(scene, camera);
}
update();
