"""
GameForge Studio — Interactive 3D Three.js Viewport
Hardware-Accelerated WebGL Asset & Turnaround Inspector
Obsidian Glass Slate UI • OrbitControls • Multi-View 4-Side Camera • Wireframe & Diagnostics
"""

import sys
import os
import json
import base64
from pathlib import Path

# Self-contained Three.js 3D Viewer HTML Template
VIEWER_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GameForge Studio — 3D Asset Viewport</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/OBJLoader.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
        body {
            background-color: #070a0e;
            color: #e2eaf4;
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            overflow: hidden;
            width: 100vw;
            height: 100vh;
        }
        #canvas-container { width: 100%; height: 100%; display: block; }
        
        /* Obsidian Glass Slate Overlay */
        .glass-panel {
            position: absolute;
            background: rgba(15, 23, 36, 0.85);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(56, 189, 248, 0.2);
            border-radius: 10px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
            z-index: 10;
        }

        #header-bar {
            top: 14px;
            left: 14px;
            right: 14px;
            padding: 10px 18px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .title-group { display: flex; align-items: center; gap: 10px; }
        .logo-badge {
            background: linear-gradient(135deg, #f97316, #ef4444);
            color: #fff;
            font-weight: 800;
            font-size: 11px;
            padding: 3px 8px;
            border-radius: 6px;
            letter-spacing: 0.5px;
        }
        .title-text { font-size: 14px; font-weight: 700; color: #f8fafc; }
        .sub-text { font-size: 11px; color: #94a3b8; }

        .btn-group { display: flex; gap: 8px; align-items: center; }
        button {
            background: #1e293b;
            color: #cbd5e1;
            border: 1px solid #334155;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s ease;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        button:hover {
            background: #334155;
            color: #f8fafc;
            border-color: #38bdf8;
        }
        button.active {
            background: rgba(56, 189, 248, 0.2);
            color: #38bdf8;
            border-color: #38bdf8;
        }

        #stats-panel {
            bottom: 14px;
            left: 14px;
            padding: 12px 16px;
            font-size: 11px;
            min-width: 220px;
        }
        .stat-row { display: flex; justify-content: space-between; margin-bottom: 4px; }
        .stat-label { color: #94a3b8; }
        .stat-val { color: #38bdf8; font-family: monospace; font-weight: 600; }

        #camera-controls {
            bottom: 14px;
            right: 14px;
            padding: 8px 12px;
            display: flex;
            gap: 6px;
        }

        #loading-overlay {
            position: absolute;
            inset: 0;
            background: rgba(7, 10, 14, 0.85);
            display: none;
            justify-content: center;
            align-items: center;
            flex-direction: column;
            gap: 12px;
            z-index: 100;
        }
        .spinner {
            width: 36px;
            height: 36px;
            border: 3px solid rgba(56, 189, 248, 0.2);
            border-top-color: #38bdf8;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div id="loading-overlay">
        <div class="spinner"></div>
        <div id="loading-msg" style="font-size: 13px; color: #94a3b8;">Loading 3D Asset...</div>
    </div>

    <div id="header-bar" class="glass-panel">
        <div class="title-group">
            <span class="logo-badge">GAMEFORGE 3D</span>
            <div>
                <div class="title-text" id="model-name">Stylized Character Turnaround (Proxy)</div>
                <div class="sub-text">24-Hour AI Pipeline • 3D Mesh Inspection Viewport</div>
            </div>
        </div>
        <div class="btn-group">
            <input type="file" id="file-input" accept=".gltf,.glb,.obj,.stl" style="display: none;" onchange="handleFileSelect(event)">
            <button onclick="document.getElementById('file-input').click()">📁 Load 3D File</button>
            <button id="btn-wire" onclick="toggleWireframe()">🕸️ Wireframe</button>
            <button id="btn-rotate" class="active" onclick="toggleAutoRotate()">🔄 Turntable</button>
            <button id="btn-grid" class="active" onclick="toggleGrid()">▦ Floor Grid</button>
            <button onclick="resetCamera()">🎯 Reset View</button>
        </div>
    </div>

    <div id="stats-panel" class="glass-panel">
        <div style="font-weight: 700; color: #f8fafc; margin-bottom: 8px; border-bottom: 1px solid #1e293b; padding-bottom: 4px;">
            Asset Diagnostics
        </div>
        <div class="stat-row"><span class="stat-label">Triangles:</span><span class="stat-val" id="stat-poly">4,288</span></div>
        <div class="stat-row"><span class="stat-label">Vertices:</span><span class="stat-val" id="stat-vert">2,154</span></div>
        <div class="stat-row"><span class="stat-label">Materials:</span><span class="stat-val" id="stat-mat">PBR Standard</span></div>
        <div class="stat-row"><span class="stat-label">Shading:</span><span class="stat-val" id="stat-shade">Smooth Lit</span></div>
        <div class="stat-row"><span class="stat-label">FPS:</span><span class="stat-val" id="stat-fps">60</span></div>
    </div>

    <div id="camera-controls" class="glass-panel">
        <button onclick="setCameraView('front')">Front</button>
        <button onclick="setCameraView('side')">Side</button>
        <button onclick="setCameraView('back')">Back</button>
        <button onclick="setCameraView('iso')">Perspective</button>
    </div>

    <div id="canvas-container"></div>

    <script>
        let scene, camera, renderer, controls;
        let currentModel = null;
        let gridHelper, dirLight, ambientLight;
        let isWireframe = false;
        let isAutoRotate = true;
        let frameCount = 0;
        let lastTime = performance.now();

        function init() {
            const container = document.getElementById('canvas-container');
            
            // 1. Scene
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x070a0e);
            scene.fog = new THREE.FogExp2(0x070a0e, 0.04);

            // 2. Camera
            camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(0, 1.8, 4.5);

            // 3. Renderer
            renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;
            renderer.toneMapping = THREE.ACESFilmicToneMapping;
            renderer.toneMappingExposure = 1.2;
            container.appendChild(renderer.domElement);

            // 4. Controls
            controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;
            controls.target.set(0, 1.0, 0);
            controls.autoRotate = isAutoRotate;
            controls.autoRotateSpeed = 1.8;

            // 5. Lighting Setup
            ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
            scene.add(ambientLight);

            dirLight = new THREE.DirectionalLight(0x38bdf8, 1.5);
            dirLight.position.set(4, 8, 4);
            dirLight.castShadow = true;
            dirLight.shadow.mapSize.width = 2048;
            dirLight.shadow.mapSize.height = 2048;
            scene.add(dirLight);

            const rimLight = new THREE.DirectionalLight(0xf97316, 1.2);
            rimLight.position.set(-4, 3, -4);
            scene.add(rimLight);

            // 6. Grid & Shadow Receiver
            gridHelper = new THREE.GridHelper(20, 20, 0x38bdf8, 0x1e293b);
            gridHelper.position.y = -0.01;
            scene.add(gridHelper);

            const planeGeo = new THREE.PlaneGeometry(50, 50);
            const planeMat = new THREE.ShadowMaterial({ opacity: 0.35 });
            const groundPlane = new THREE.Mesh(planeGeo, planeMat);
            groundPlane.rotation.x = -Math.PI / 2;
            groundPlane.receiveShadow = true;
            scene.add(groundPlane);

            // 7. Load Default Samurai Proxy Mesh (matching Shikhar's 24-hr pipeline character)
            loadDefaultSamuraiProxy();

            // 8. Resize Listener
            window.addEventListener('resize', onWindowResize);
            animate();
        }

        function loadDefaultSamuraiProxy() {
            if (currentModel) scene.remove(currentModel);

            const group = new THREE.Group();

            // Stylized materials
            const coatMat = new THREE.MeshStandardMaterial({ color: 0x223245, roughness: 0.7, metalness: 0.1 });
            const armorMat = new THREE.MeshStandardMaterial({ color: 0x475569, roughness: 0.4, metalness: 0.6 });
            const skinMat = new THREE.MeshStandardMaterial({ color: 0xd4a373, roughness: 0.5 });
            const strawMat = new THREE.MeshStandardMaterial({ color: 0xc2a649, roughness: 0.9 });
            const swordMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.9, roughness: 0.2 });

            // Torso / Kimono
            const torsoGeo = new THREE.CylinderGeometry(0.28, 0.38, 0.75, 8);
            const torso = new THREE.Mesh(torsoGeo, coatMat);
            torso.position.y = 1.05;
            torso.castShadow = true;
            group.add(torso);

            // Sash / Belt
            const beltGeo = new THREE.CylinderGeometry(0.32, 0.34, 0.15, 8);
            const belt = new THREE.Mesh(beltGeo, new THREE.MeshStandardMaterial({ color: 0xb91c1c, roughness: 0.6 }));
            belt.position.y = 0.88;
            group.add(belt);

            // Head
            const headGeo = new THREE.SphereGeometry(0.16, 16, 16);
            const head = new THREE.Mesh(headGeo, skinMat);
            head.position.y = 1.55;
            head.castShadow = true;
            group.add(head);

            // Conical Kasa Straw Hat (Shikhar character's signature)
            const hatGeo = new THREE.ConeGeometry(0.58, 0.22, 24);
            const hat = new THREE.Mesh(hatGeo, strawMat);
            hat.position.y = 1.68;
            hat.castShadow = true;
            group.add(hat);

            // Legs / Hakama
            const legGeo = new THREE.CylinderGeometry(0.14, 0.18, 0.75, 8);
            const leftLeg = new THREE.Mesh(legGeo, coatMat);
            leftLeg.position.set(-0.16, 0.42, 0);
            leftLeg.castShadow = true;
            group.add(leftLeg);

            const rightLeg = new THREE.Mesh(legGeo, coatMat);
            rightLeg.position.set(0.16, 0.42, 0);
            rightLeg.castShadow = true;
            group.add(rightLeg);

            // Katana Sheath at waist
            const scabbardGeo = new THREE.CylinderGeometry(0.03, 0.03, 1.1, 6);
            const scabbard = new THREE.Mesh(scabbardGeo, swordMat);
            scabbard.position.set(-0.35, 0.9, 0.05);
            scabbard.rotation.z = 0.55;
            scabbard.rotation.x = -0.3;
            scabbard.castShadow = true;
            group.add(scabbard);

            currentModel = group;
            scene.add(currentModel);
            updateDiagnostics(currentModel, "Samurai Hero (Proxy Mesh)");
        }

        function updateDiagnostics(obj, name) {
            let polys = 0;
            let verts = 0;
            obj.traverse(child => {
                if (child.isMesh && child.geometry) {
                    if (child.geometry.index) {
                        polys += child.geometry.index.count / 3;
                    } else if (child.geometry.attributes.position) {
                        polys += child.geometry.attributes.position.count / 3;
                    }
                    if (child.geometry.attributes.position) {
                        verts += child.geometry.attributes.position.count;
                    }
                }
            });
            document.getElementById('stat-poly').textContent = Math.round(polys).toLocaleString();
            document.getElementById('stat-vert').textContent = Math.round(verts).toLocaleString();
            if (name) document.getElementById('model-name').textContent = name;
        }

        function toggleWireframe() {
            isWireframe = !isWireframe;
            document.getElementById('btn-wire').classList.toggle('active', isWireframe);
            if (currentModel) {
                currentModel.traverse(child => {
                    if (child.isMesh && child.material) {
                        child.material.wireframe = isWireframe;
                    }
                });
            }
        }

        function toggleAutoRotate() {
            isAutoRotate = !isAutoRotate;
            controls.autoRotate = isAutoRotate;
            document.getElementById('btn-rotate').classList.toggle('active', isAutoRotate);
        }

        function toggleGrid() {
            gridHelper.visible = !gridHelper.visible;
            document.getElementById('btn-grid').classList.toggle('active', gridHelper.visible);
        }

        function resetCamera() {
            camera.position.set(0, 1.8, 4.5);
            controls.target.set(0, 1.0, 0);
            controls.update();
        }

        function setCameraView(view) {
            controls.autoRotate = false;
            document.getElementById('btn-rotate').classList.remove('active');
            isAutoRotate = false;

            if (view === 'front') {
                camera.position.set(0, 1.2, 3.8);
            } else if (view === 'side') {
                camera.position.set(3.8, 1.2, 0);
            } else if (view === 'back') {
                camera.position.set(0, 1.2, -3.8);
            } else if (view === 'iso') {
                camera.position.set(2.6, 2.2, 2.8);
            }
            controls.target.set(0, 1.0, 0);
            controls.update();
        }

        function handleFileSelect(e) {
            const file = e.target.files[0];
            if (!file) return;

            const filename = file.name.toLowerCase();
            document.getElementById('loading-overlay').style.display = 'flex';
            document.getElementById('loading-msg').textContent = 'Loading ' + file.name + '...';

            const reader = new FileReader();
            reader.onload = function(evt) {
                const contents = evt.target.result;
                try {
                    if (filename.endsWith('.gltf') || filename.endsWith('.glb')) {
                        const loader = new THREE.GLTFLoader();
                        loader.parse(contents, '', function(gltf) {
                            if (currentModel) scene.remove(currentModel);
                            currentModel = gltf.scene;
                            fitModelToScene(currentModel);
                            scene.add(currentModel);
                            updateDiagnostics(currentModel, file.name);
                            document.getElementById('loading-overlay').style.display = 'none';
                        }, function(err) {
                            alert('GLTF Load Error: ' + err);
                            document.getElementById('loading-overlay').style.display = 'none';
                        });
                    } else if (filename.endsWith('.obj')) {
                        const loader = new THREE.OBJLoader();
                        const obj = loader.parse(contents);
                        if (currentModel) scene.remove(currentModel);
                        currentModel = obj;
                        fitModelToScene(currentModel);
                        scene.add(currentModel);
                        updateDiagnostics(currentModel, file.name);
                        document.getElementById('loading-overlay').style.display = 'none';
                    }
                } catch(ex) {
                    alert('Error parsing 3D file: ' + ex);
                    document.getElementById('loading-overlay').style.display = 'none';
                }
            };

            if (filename.endsWith('.glb')) {
                reader.readAsArrayBuffer(file);
            } else {
                reader.readAsText(file);
            }
        }

        function fitModelToScene(model) {
            const box = new THREE.Box3().setFromObject(model);
            const size = box.getSize(new THREE.Vector3());
            const center = box.getCenter(new THREE.Vector3());

            const maxDim = Math.max(size.x, size.y, size.z);
            if (maxDim > 0) {
                const scale = 2.0 / maxDim;
                model.scale.set(scale, scale, scale);
            }
            box.setFromObject(model);
            box.getCenter(center);
            model.position.sub(center);
            model.position.y += (size.y * (2.0 / maxDim)) / 2;

            model.traverse(child => {
                if (child.isMesh) {
                    child.castShadow = true;
                    child.receiveShadow = true;
                }
            });
        }

        function onWindowResize() {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }

        function animate() {
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);

            // FPS Counter
            frameCount++;
            const now = performance.now();
            if (now >= lastTime + 1000) {
                document.getElementById('stat-fps').textContent = Math.round((frameCount * 1000) / (now - lastTime));
                frameCount = 0;
                lastTime = now;
            }
        }

        window.onload = init;
    </script>
</body>
</html>
"""

def launch_viewport(target_file=None):
    """Launches the 3D Viewport window via pywebview or system browser."""
    try:
        import webview
        # Create interactive window with dark titlebar
        window = webview.create_window(
            title="GameForge Studio — 3D Asset Viewport (Three.js WebGL)",
            html=VIEWER_HTML,
            width=1100,
            height=720,
            background_color='#070a0e'
        )
        webview.start()
    except Exception as ex:
        # Fallback to local HTML file in default browser
        import tempfile
        import webbrowser
        tmp = Path(tempfile.gettempdir()) / "gameforge_3d_viewport.html"
        tmp.write_text(VIEWER_HTML, encoding='utf-8')
        webbrowser.open(tmp.as_uri())

if __name__ == '__main__':
    file_arg = sys.argv[1] if len(sys.argv) > 1 else None
    launch_viewport(file_arg)
