// src/lib/useAvatarPreload.ts
import { useEffect, useState } from "react";
import { useFBX } from "@react-three/drei";

// List of asset paths to preload
const assets = [
  "/juli.fbx",
  "/Idle.fbx",
  "/Talking.fbx",
  "/Thinking.fbx",
  "/Waving.fbx",
];

/**
 * Hook that preloads all avatar assets.
 * Returns a boolean indicating whether all assets have been queued for loading.
 * In @react-three/drei, useFBX.preload queues the asset; the actual loading
 * happens when the component using useFBX mounts.
 */
export function useAvatarPreload(): boolean {
  const [ready, setReady] = useState(false);

  useEffect(() => {
    assets.forEach((path) => {
      // @ts-ignore – useFBX.preload is a static method
      (useFBX as any).preload(path);
    });
    setReady(true);
  }, []);

  return ready;
}
