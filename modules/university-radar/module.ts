import { defineModule } from "@aihot/contracts/modules";

export const UNIVERSITY_RADAR_MODULE = defineModule({
  name: "university-radar",
  pages: [{ path: "university-radar", file: "./web/university-radar.tsx" }],
  apiPaths: [/^\/api\/university-radar$/],
});
