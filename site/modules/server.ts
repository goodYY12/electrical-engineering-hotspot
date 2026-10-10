// The backend of the site's modules, installed by the api and the worker when they start (site/modules/index.ts).
import type { ServerModule } from "@aihot/backend/modules";
import { ELECTRICAL_INTELLIGENCE_SERVER } from "../../modules/electrical-intelligence/server.ts";
import { UNIVERSITY_RADAR_SERVER } from "../../modules/university-radar/server.ts";

export const SERVER_MODULES: readonly ServerModule[] = [ELECTRICAL_INTELLIGENCE_SERVER, UNIVERSITY_RADAR_SERVER];
