// The modules this site runs (modules/<name>/, see docs/architecture.md). A module has a line in each list
// it has an entry for: here for its addresses (module.ts), in server.ts for its backend, in web.ts for its
// pages' parts. Each list keeps the order its entries appear in on the site.
import type { ModuleDeclaration } from "@aihot/contracts/modules";
import { ELECTRICAL_INTELLIGENCE_MODULE } from "../../modules/electrical-intelligence/module.ts";
import { UNIVERSITY_RADAR_MODULE } from "../../modules/university-radar/module.ts";

export const MODULES: readonly ModuleDeclaration[] = [ELECTRICAL_INTELLIGENCE_MODULE, UNIVERSITY_RADAR_MODULE];
