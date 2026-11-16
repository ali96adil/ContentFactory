import {defineConfig} from 'vite';
import motionCanvas from '@motion-canvas/vite-plugin';

export default defineConfig({
  server: {
    host: '127.0.0.1',
    cors: false,
    fs: {strict: true},
    allowedHosts: [],
  },
  plugins: [
    motionCanvas(),
    {
      name: 'motion-canvas-vite7-target-compat',
      config: () => ({build: {target: 'esnext'}}),
    },
  ],
});
