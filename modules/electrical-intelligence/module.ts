import { defineModule } from "@aihot/contracts/modules";

export const ELECTRICAL_INTELLIGENCE_MODULE = defineModule({
  name: "electrical-intelligence",
  pages: [{ path: "radar", file: "./web/radar.tsx" }],
  apiPaths: [/^\/api\/electrical\/radar$/],
});
