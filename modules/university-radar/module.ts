import { defineModule } from "@aihot/contracts/modules";

export const UNIVERSITY_RADAR_MODULE = defineModule({
  name: "university-radar",
  pages: [
    { path: "university-radar", file: "./web/university-radar.tsx" },
    { path: "graduation-topics", file: "./web/graduation-topics.tsx" },
  ],
  apiPaths: [/^\/api\/university-radar(?:\/graduation-topics)?$/],
});
