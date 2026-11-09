import { Canvas, useFrame } from '@react-three/fiber';
import { ContactShadows, Float } from '@react-three/drei';
import { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';

const fingers: Array<{ name: string; points: [number, number][] }> = [
  { name: 'little', points: [[-.38, .32], [-.48, .66], [-.5, .92]] },
  { name: 'ring', points: [[-.13, .42], [-.17, .8], [-.18, 1.13]] },
  { name: 'middle', points: [[.12, .44], [.13, .87], [.13, 1.22]] },
  { name: 'index', points: [[.35, .36], [.43, .75], [.48, 1.06]] },
];
function Bone({ a, b, radius = .09 }: { a: [number, number]; b: [number, number]; radius?: number }) {
  const dx = b[0] - a[0], dy = b[1] - a[1];
  return <mesh position={[(a[0] + b[0]) / 2, (a[1] + b[1]) / 2, .14]} rotation={[0, 0, -Math.atan2(dx, dy)]} castShadow>
    <capsuleGeometry args={[radius, Math.hypot(dx, dy), 5, 10]}/>
    <meshStandardMaterial color="#d58c70" roughness={.38}/>
  </mesh>;
}
function Hand(){
  const shape = new THREE.Shape();
  shape.moveTo(-.28, -.76); shape.lineTo(.27, -.76); shape.quadraticCurveTo(.36, -.7, .36, -.56);
  shape.lineTo(.44, .17); shape.quadraticCurveTo(.45, .36, .34, .4); shape.quadraticCurveTo(.22, .43, .17, .29);
  shape.quadraticCurveTo(.1, .47, -.04, .46); shape.quadraticCurveTo(-.18, .43, -.2, .3);
  shape.quadraticCurveTo(-.28, .43, -.4, .35); shape.quadraticCurveTo(-.52, .28, -.45, .1);
  shape.lineTo(-.39, -.45); shape.quadraticCurveTo(-.4, -.7, -.28, -.76);
  return <group>
    <mesh position={[0, 0, -.02]} castShadow receiveShadow><extrudeGeometry args={[shape, { depth: .2, bevelEnabled: true, bevelSegments: 4, steps: 1, bevelSize: .055, bevelThickness: .07 }]}/><meshStandardMaterial color="#e4a184" roughness={.4}/></mesh>
    {fingers.map(finger=><group key={finger.name}>{finger.points.slice(0, -1).map((point, i)=><group key={i}><Bone a={point} b={finger.points[i+1] as [number,number]} radius={finger.name==='middle'?.09:.085}/><mesh position={[finger.points[i+1][0], finger.points[i+1][1], .14]} castShadow><sphereGeometry args={[.09, 16, 12]}/><meshStandardMaterial color="#e4a184" roughness={.4}/></mesh></group>)}<mesh position={[finger.points[2][0], finger.points[2][1], .14]} castShadow><sphereGeometry args={[.085, 16, 12]}/><meshStandardMaterial color="#e4a184" roughness={.4}/></mesh></group>)}
    <Bone a={[-.34, -.03]} b={[-.64, .12]} radius={.105}/><Bone a={[-.64, .12]} b={[-.79, .4]} radius={.095}/>
    <mesh position={[-.64,.12,.14]} castShadow><sphereGeometry args={[.105,16,12]}/><meshStandardMaterial color="#e4a184" roughness={.4}/></mesh>
    <mesh position={[0,-.91,.1]} castShadow><capsuleGeometry args={[.18,.48,5,12]}/><meshStandardMaterial color="#d58c70" roughness={.4}/></mesh>
    {/* Diagram-only curved path; this open, relaxed palm is not an ASL sign. */}
    <mesh position={[0,0,.28]}><tubeGeometry args={[new THREE.CatmullRomCurve3([new THREE.Vector3(-.95,.28,.05),new THREE.Vector3(-.76,.82,.08),new THREE.Vector3(-.2,1.46,.08),new THREE.Vector3(.46,1.38,.08),new THREE.Vector3(.87,.75,.06),new THREE.Vector3(.9,.02,.02)]), 120, .035, 8, false]}/><meshStandardMaterial color="#127e78" roughness={.32} metalness={.14}/></mesh>
  </group>;
}
function Sculpture(){
  const group = useRef<THREE.Group>(null), initiallyCompact = window.innerWidth < 760;
  useFrame(({camera}, delta)=>{
    const compact = window.innerWidth < 760, reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const story = document.querySelector('.story'), range = (story?.getBoundingClientRect().height ?? innerHeight) - innerHeight;
    const progress = Math.max(0, Math.min(1, -(story?.getBoundingClientRect().top ?? 0) / Math.max(range, 1))), beat = progress * 5;
    if(!reduce){camera.position.lerp(new THREE.Vector3(.1+beat*(compact?.035:.25),compact?1.12+Math.sin(beat*.7)*.04:1.5+Math.sin(beat*.7)*.12,compact?5.35-beat*.06:7-beat*.3),1-Math.exp(-delta*2));camera.lookAt(beat*(compact?.025:.18),compact?.05:0,0);}
    if(group.current){group.current.scale.setScalar(compact?.62:.72);group.current.position.x=(compact?0:1.55)+beat*(compact?.025:.06);if(!reduce)group.current.rotation.y=-.28+beat*.16;}
  });
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  return <group ref={group} position={[initiallyCompact?0:1.55,.2,0]} scale={initiallyCompact?.62:.72}>
    <Float speed={reduced?0:.3} rotationIntensity={reduced?0:.025} floatIntensity={reduced?0:.045}><Hand/></Float>
    <mesh position={[0,-1.47,0]} receiveShadow><cylinderGeometry args={[1.55,1.74,.18,64]}/><meshStandardMaterial color="#23605d" roughness={.42}/></mesh>
    <mesh position={[0,-1.59,0]}><cylinderGeometry args={[1.66,1.66,.08,64]}/><meshStandardMaterial color="#d5e3d7" roughness={.6}/></mesh>
  </group>;
}
function IllustratedFallback(){return <div className="webgl-fallback" role="img" aria-label="Ilustrasi tangan netral; bukan demonstrasi isyarat ASL"><svg viewBox="0 0 520 420" aria-hidden="true"><ellipse cx="270" cy="365" rx="190" ry="28" fill="#dfe8dc"/><path d="M185 325c-21-18-17-45-15-78l5-83c1-16 23-17 26 0l7 52 2-123c0-18 25-18 26 0l2 111 7-139c1-18 26-16 26 2l1 137 8-115c2-17 25-15 25 3v133l11-80c3-17 27-13 24 4l-16 151c-5 48-39 71-82 71h-21c-35 0-51-19-59-46z" fill="#e4a184" stroke="#b97058" strokeWidth="7" strokeLinejoin="round"/><path d="M126 142c43-66 206-75 261 6 26 38 21 76-3 98" fill="none" stroke="#147b72" strokeWidth="12" strokeLinecap="round"/><circle cx="124" cy="145" r="13" fill="#147b72"/><circle cx="384" cy="246" r="13" fill="#147b72"/></svg><p>Ilustrasi gerak tangan · bukan demonstrasi ASL</p></div>}
export default function Journey(){
  const [desktop,setDesktop]=useState(()=>window.innerWidth>760);
  useEffect(()=>{const resize=()=>setDesktop(window.innerWidth>760);window.addEventListener('resize',resize);return()=>window.removeEventListener('resize',resize)},[]);
  return <div className="canvas-wrap" aria-hidden="true">
    <Canvas shadows={desktop?'percentage':false} dpr={desktop?[1,1.4]:[1,1.15]} camera={{position:desktop?[.1,1.5,7]:[0,1.12,5.35],fov:desktop?34:38}}>
      <color attach="background" args={['#f4f1e9']}/><ambientLight intensity={desktop?1.15:1.3}/><directionalLight position={[3,5,4]} intensity={desktop?2.4:1.8} castShadow={desktop} shadow-mapSize={[1024,1024]}/><hemisphereLight args={['#f8e5d5','#738c83',.55]}/>
      <Sculpture/>{desktop&&<ContactShadows position={[0,-1.7,0]} opacity={.2} blur={2.4} scale={7} far={4}/>}
    </Canvas>
  </div>;
}
