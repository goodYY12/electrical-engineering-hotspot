// What the site's modules add to the web pages (site/modules/index.ts).
import type { WebModule } from "@aihot/web/modules";
import { ELECTRICAL_INTELLIGENCE_WEB } from "../../modules/electrical-intelligence/web.tsx";
import { UNIVERSITY_RADAR_WEB } from "../../modules/university-radar/web.tsx";

export const WEB_MODULES: readonly WebModule[] = [ELECTRICAL_INTELLIGENCE_WEB, UNIVERSITY_RADAR_WEB];
