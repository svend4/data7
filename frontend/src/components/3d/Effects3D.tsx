import React from 'react'
import { EffectComposer, Bloom, Vignette, SMAA } from '@react-three/postprocessing'
import { BlendFunction } from 'postprocessing'

export const Effects3D: React.FC = () => {
  return (
    <EffectComposer>
      {/* SMAA - Anti-aliasing for smooth edges */}
      <SMAA />

      {/* Bloom - Glow effect for emissive materials (Art Deco golden glow) */}
      <Bloom
        intensity={0.6}
        luminanceThreshold={0.4}
        luminanceSmoothing={0.7}
        mipmapBlur={true}
        blendFunction={BlendFunction.SCREEN}
      />

      {/* Vignette - Cinematic edge darkening */}
      <Vignette
        offset={0.3}
        darkness={0.5}
        blendFunction={BlendFunction.NORMAL}
      />
    </EffectComposer>
  )
}
