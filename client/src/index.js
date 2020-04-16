import * as THREE from 'three';
import PointerLockControls from "three-pointerlock";
import io from 'socket.io-client';

import {keyNames} from "./common";
import './styles/main.css';

const socket = io('http://localhost:4001');

// ========== FUNCTIONS ==========
function keyDown(event) {
    let key = keyNames[event.which];
    if (!inputs['keyboard'].includes(key)) {
        inputs['keyboard'].push(key);
        console.log(inputs['keyboard']);
    }
}

function keyUp(event) {
    let key = keyNames[event.which];
    inputs['keyboard'] = inputs['keyboard'].filter(item => item !== key);
    console.log(inputs['keyboard']);
}

function mouseDown(event) {
    lockPointer();
}

function lockPointer() {
    document.body.requestPointerLock();
}

function unlockPointer() {

}

function loadSkybox() {
    let skybox_tx = [];
    //let skybox_top = new THREE.TextureLoader().load("textures/skybox_tp.png");
    //let skybox_bottom = new THREE.TextureLoader().load("textures/skybox_bt.png");
    //let skybox_side = new THREE.TextureLoader().load("textures/skybox_sd.png");

    //skybox_tx.push(new THREE.MeshBasicMaterial({map: skybox_side} ));
    //skybox_tx.push(new THREE.MeshBasicMaterial({map: skybox_side} ));
    //skybox_tx.push(new THREE.MeshBasicMaterial({map: skybox_top} ));
    //skybox_tx.push(new THREE.MeshBasicMaterial({map: skybox_bottom} ));
    //skybox_tx.push(new THREE.MeshBasicMaterial({map: skybox_side} ));
    //skybox_tx.push(new THREE.MeshBasicMaterial({map: skybox_side} ));

    skybox_tx.push(new THREE.MeshBasicMaterial({color: new THREE.Color(200, 0, 0)} ));
    skybox_tx.push(new THREE.MeshBasicMaterial({color: new THREE.Color(0, 200, 0)} ));
    skybox_tx.push(new THREE.MeshBasicMaterial({color: new THREE.Color(0, 0, 200)} ));
    skybox_tx.push(new THREE.MeshBasicMaterial({color: new THREE.Color(200, 0, 200)} ));
    skybox_tx.push(new THREE.MeshBasicMaterial({color: new THREE.Color(200, 200, 0)} ));
    skybox_tx.push(new THREE.MeshBasicMaterial({color: new THREE.Color(0, 200, 200)} ));

    let skyboxGeometry = new THREE.BoxGeometry(10000, 10000, 10000);
    let skybox = new THREE.Mesh(skyboxGeometry, skybox_tx);

    scene.add(skybox);
}

// ========== START ==========
let scene = new THREE.Scene();
let camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 100000);
let renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

let controls = new PointerLockControls(camera, document.body);
let time;
scene.add( controls.getObject() );
loadSkybox();

let geometry = new THREE.BoxGeometry();
let material = new THREE.MeshBasicMaterial( { color: 0x00ff00 } );
let cube = new THREE.Mesh( geometry, material );
scene.add( cube );
camera.position.z = 5;

let inputs = {
    'keyboard': [],
    'mouseX': 0,
    'mouseY': 0
};

document.addEventListener('keydown', keyDown, false);
document.addEventListener('keyup', keyUp, false);
document.addEventListener('mousedown', mouseDown, false)
// document.addEventListener('mousemove', mouseMove, false);

function update() {
    requestAnimationFrame(update);

    // console.log(controls.getDirection(new THREE.Vector3(0,0,0)))

    controls.isOnObject( false );

    controls.update( Date.now() - time );

    renderer.render( scene, camera );

    time = Date.now();


    renderer.render(scene, camera);
}
update();
