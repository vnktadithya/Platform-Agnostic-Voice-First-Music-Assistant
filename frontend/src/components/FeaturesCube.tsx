
import { useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Html, TrackballControls, Environment, RoundedBox, Outlines } from '@react-three/drei';
import * as THREE from 'three';
import { FeatureCard, features } from './FeatureCard';

// Cube component
const Cube = () => {
    const groupRef = useRef<THREE.Group>(null!);
    const [coreMesh, setCoreMesh] = useState<THREE.Mesh | null>(null); // State ref for occlusion
    const [isHovered, setIsHovered] = useState(false);
    const [hoveredColor, setHoveredColor] = useState<string | null>(null);

    // Auto-rotation - CONTINUOUS (removed !isHovered check)
    useFrame((_state, delta) => {
        if (groupRef.current) {
            groupRef.current.rotation.y += delta * 0.2;
            groupRef.current.rotation.x += delta * 0.1;
        }
    });

    // Positions and rotations for the 6 faces
    // Distance kept at 2.65 for levitation
    const DISTANCE = 2.65;

    const faces = [
        { feature: features[0], position: [0, 0, DISTANCE], rotation: [0, 0, 0] },          // Front
        { feature: features[1], position: [0, 0, -DISTANCE], rotation: [0, Math.PI, 0] },    // Back
        { feature: features[2], position: [DISTANCE, 0, 0], rotation: [0, Math.PI / 2, 0] }, // Right
        { feature: features[3], position: [-DISTANCE, 0, 0], rotation: [0, -Math.PI / 2, 0] },// Left
        { feature: features[4], position: [0, DISTANCE, 0], rotation: [-Math.PI / 2, 0, 0] }, // Top
        { feature: features[5], position: [0, -DISTANCE, 0], rotation: [Math.PI / 2, 0, 0] }, // Bottom
    ];

    return (
        <group
            ref={groupRef}
        >
            {/* 1. The Solid Core - Rounded */}
            <RoundedBox
                ref={setCoreMesh}
                args={[5, 5, 5]}
                radius={0.2}
                smoothness={4}
            >
                <meshPhysicalMaterial
                    color="#050510" // Dark Obsidian
                    metalness={0.9}
                    roughness={0.2}
                    clearcoat={1}
                    clearcoatRoughness={0.1}
                />
            </RoundedBox>

            {/* 2. The Solid Glass Shell with Neon Outlines */}
            <RoundedBox args={[5.05, 5.05, 5.05]} radius={0.2} smoothness={4}>
                <meshPhysicalMaterial
                    color="#00f0ff"
                    transparent
                    opacity={isHovered ? 0.25 : 0.08} // Subtle tint idle, brighter on hover
                    roughness={0} // Glass-like
                    metalness={0.1}
                    side={THREE.DoubleSide}
                    depthWrite={false} // Clean transparency
                />
                {/* Thick Neon Border that follows geometry perfectly */}
                <Outlines
                    thickness={0.1}
                    color={hoveredColor || "white"}
                    screenspace={false}
                    opacity={1}
                    transparent={false}
                    angle={0}
                />
            </RoundedBox>

            {/* 3. The Holographic Faces */}
            {faces.map((face, index) => (
                <Html
                    key={index}
                    position={face.position as [number, number, number]}
                    rotation={face.rotation as [number, number, number]}
                    transform
                    occlude={coreMesh ? [{ current: coreMesh }] : undefined} // Occlude against the solid core
                    distanceFactor={4}
                    style={{
                        width: 0,
                        height: 0,
                        pointerEvents: 'none',
                    }}
                >
                    <div style={{
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        width: '340px',
                        height: '320px',
                        transform: 'translate(-50%, -50%)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                    }}>
                        <div
                            onMouseEnter={() => {
                                setIsHovered(true);
                                setHoveredColor(face.feature.color1);
                            }}
                            onMouseLeave={() => {
                                setIsHovered(false);
                                setHoveredColor(null);
                            }}
                            style={{ width: '100%', height: '100%', pointerEvents: 'auto' }}
                        >
                            <FeatureCard feature={face.feature} index={index} is3D={true} />
                        </div>
                    </div>
                </Html>
            ))}
        </group>
    );
};

const FeaturesCube = () => {
    return (
        <div style={{ width: '100%', height: '600px', position: 'relative' }}>
            <Canvas camera={{ position: [0, 0, 10], fov: 45 }}>
                {/* Lighting to show off the metallic core */}
                <ambientLight intensity={0.5} />
                <pointLight position={[10, 10, 10]} intensity={1} />
                <pointLight position={[-10, -10, -10]} intensity={0.5} color="#bd00ff" />

                {/* Environment for reflections */}
                <Environment preset="city" />

                {/* Scaled down group to fit container */}
                <group scale={0.9}>
                    <Cube />
                </group>

                <TrackballControls
                    noZoom={true}
                    noPan={true}
                    rotateSpeed={5}
                />
            </Canvas>
        </div>
    );
};

export default FeaturesCube;
