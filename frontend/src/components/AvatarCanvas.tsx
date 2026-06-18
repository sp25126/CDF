"use client";

import React, { useRef, useEffect } from "react";
import { useFrame, useThree } from "@react-three/fiber";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, useFBX } from "@react-three/drei";
import * as THREE from "three";

// ─── Skin tones ───────────────────────────────────────────────────────────────
const SKIN_TONE      = new THREE.Color(0xE5D0B5); // noticeably lighter warm Indian beige
const SKIN_DARK_TONE = new THREE.Color(0xD1BC9E); // lighter shadow / neck

function isNearWhite(c: THREE.Color) {
  return c.r > 0.70 && c.g > 0.70 && c.b > 0.70;
}

function patchMaterials(fbx: THREE.Group) {
  fbx.traverse((child) => {
    if (!(child as THREE.Mesh).isMesh) return;
    const mesh = child as THREE.Mesh;
    mesh.castShadow = true;
    mesh.receiveShadow = true;

    const mats = Array.isArray(mesh.material)
      ? (mesh.material as THREE.Material[])
      : [mesh.material as THREE.Material];

    mats.forEach((mat) => {
      if (!mat) return;

      const n = (mat.name ?? "").toLowerCase();
      if (process.env.NODE_ENV === "development") {
        console.log("[Avatar mat]", n, mat.type, (mat as any).color?.getHexString?.(), "hasMap:", !!(mat as any).map);
      }

      const isClothing =
        n.includes("cloth") || n.includes("hair") || n.includes("shoe") ||
        n.includes("jean")  || n.includes("jacket") || n.includes("shirt") ||
        n.includes("pant")  || n.includes("glass") || n.includes("teeth") ||
        n.includes("eye");

      const isExplicitSkin =
        n.includes("skin") || n.includes("face") || n.includes("head") ||
        n.includes("body") || n.includes("lip")  || n.includes("ear");

      // Fix texture color-space
      (["map", "normalMap", "roughnessMap", "metalnessMap", "emissiveMap"] as const).forEach((k) => {
        const tex = (mat as any)[k] as THREE.Texture | undefined;
        if (tex) { tex.colorSpace = THREE.SRGBColorSpace; tex.needsUpdate = true; }
      });

      mat.needsUpdate = true;

      // Apply color even when map exists — THREE multiplies color × texture
      const applyColor = (target: THREE.Color) => {
        if ((mat as any).color) (mat as any).color.copy(target);
      };

      if (mat instanceof THREE.MeshStandardMaterial) {
        mat.roughness = 0.65;
        mat.metalness = 0.0;
        const nearWhite = isNearWhite(mat.color);
        if (isExplicitSkin || (!isClothing && nearWhite)) applyColor(SKIN_TONE);
        else if (!isClothing && mat.color.r > 0.55) applyColor(SKIN_DARK_TONE);
      } else if (mat instanceof THREE.MeshPhongMaterial) {
        mat.shininess = 15;
        const nearWhite = isNearWhite(mat.color);
        if (isExplicitSkin || (!isClothing && nearWhite)) applyColor(SKIN_TONE);
        else if (!isClothing && mat.color.r > 0.55) applyColor(SKIN_DARK_TONE);
      } else if (mat instanceof THREE.MeshBasicMaterial) {
        const nearWhite = isNearWhite(mat.color);
        if (isExplicitSkin || (!isClothing && nearWhite)) applyColor(SKIN_TONE);
      }
    });
  });
}


// ─── AvatarModel ─────────────────────────────────────────────────────────────
function AvatarModel({ state }: { state: string }) {
  const fbx        = useFBX("/juli.fbx");
  const idleAnim   = useFBX("/Idle.fbx");
  const talkAnim   = useFBX("/Talking.fbx");
  const thinkAnim  = useFBX("/Thinking.fbx");
  const waveAnim   = useFBX("/Waving.fbx");

  const mixerRef       = useRef<THREE.AnimationMixer | null>(null);
  const actionsRef     = useRef<Record<string, THREE.AnimationAction>>({});
  const activeRef      = useRef<THREE.AnimationAction | null>(null);

  // ── Setup: runs every time fbx is available (safe under StrictMode) ────────
  useEffect(() => {
    if (!fbx) return;

  // Patch materials every mount so code changes take effect immediately
    patchMaterials(fbx);

    // Always (re-)create the mixer so StrictMode double-invoke is safe
    const mixer = new THREE.AnimationMixer(fbx);
    mixerRef.current = mixer;

    const rawClips: [string, THREE.AnimationClip | undefined][] = [
      ["idle",     idleAnim.animations[0]],
      ["speaking", talkAnim.animations[0]],
      ["thinking", thinkAnim.animations[0]],
      ["waving",   waveAnim.animations[0]],
    ];

    const map: Record<string, THREE.AnimationAction> = {};
    rawClips.forEach(([name, clip]) => {
      if (!clip) return;
      const c = clip.clone();
      c.name = name;
      const action = mixer.clipAction(c);   // ← no explicit root arg; mixer owns fbx
      action.setLoop(THREE.LoopRepeat, Infinity);
      map[name] = action;
    });
    actionsRef.current = map;

    // Kick off idle immediately
    const idle = map["idle"];
    if (idle) {
      idle.reset().play();
      activeRef.current = idle;
    } else {
      console.warn("[Avatar] No idle clip found – model will T-pose");
    }

    return () => {
      // Cleanup for StrictMode / unmount
      mixer.stopAllAction();
      mixer.uncacheRoot(fbx);
      mixerRef.current  = null;
      activeRef.current = null;
      actionsRef.current = {};
    };
  // fbx object ref changes only when useFBX gives a new object (cache miss)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fbx]);

  // ── State transitions ──────────────────────────────────────────────────────
  useEffect(() => {
    const map = actionsRef.current;
    if (!mixerRef.current || !map) return;

    const targetName = (state === "listening" ? "idle" : state) || "idle";
    const next    = map[targetName];
    const current = activeRef.current;

    if (!next || next === current) return;

    current?.fadeOut(0.25);
    next.reset().fadeIn(0.25).play();
    next.setLoop(targetName === "waving" ? THREE.LoopOnce : THREE.LoopRepeat,
                 targetName === "waving" ? 1 : Infinity);
    if (targetName === "waving") next.clampWhenFinished = true;
    activeRef.current = next;
  }, [state]);

  // ── Tick ──────────────────────────────────────────────────────────────────
  useFrame((_, delta) => mixerRef.current?.update(delta));

  return (
    <primitive
      object={fbx}
      scale={0.015}
      position={[0, -2.15, 0]}
      rotation={[0, 0, 0]}
    />
  );
}

// ─── Canvas shell ─────────────────────────────────────────────────────────────
export function AvatarCanvas({ state }: { state: string }) {
  return (
    <Canvas
      shadows
      camera={{ position: [0, 0.25, 2.0], fov: 40 }}
      style={{ width: "100%", height: "100%" }}
      gl={{
        outputColorSpace:    THREE.SRGBColorSpace,
        toneMapping:         THREE.ACESFilmicToneMapping,
        toneMappingExposure: 1.1,
      }}
    >
      <directionalLight position={[1, 3, 2]}   intensity={2.0} castShadow shadow-mapSize={[1024, 1024]} />
      <directionalLight position={[-2, 1, -1]} intensity={0.8} />
      <directionalLight position={[0, 2, -3]}  intensity={0.5} color="#ffe0c0" />
      <ambientLight intensity={0.9} />
      <pointLight position={[0, 1.5, 1.2]} intensity={1.4} color="#fff8f0" />

      <React.Suspense fallback={null}>
        <AvatarModel state={state} />
      </React.Suspense>

      <OrbitControls
        enableZoom={false}
        enablePan={false}
        minPolarAngle={Math.PI / 2.2}
        maxPolarAngle={Math.PI / 2}
        minAzimuthAngle={-Math.PI / 12}
        maxAzimuthAngle={Math.PI / 12}
        target={[0, -0.4, 0]}
      />
    </Canvas>
  );
}

// NOTE: preload calls intentionally removed — they use browser-only APIs
// that crash during Next.js SSR module evaluation even in "use client" files.
// The <React.Suspense> fallback handles the loading state gracefully.
