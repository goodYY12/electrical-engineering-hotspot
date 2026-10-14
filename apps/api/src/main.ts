import { assertProductionSecrets, config } from "@aihot/backend/config";
import { closeDb } from "@aihot/backend/db";
import { installModules } from "@aihot/backend/modules";
import { SERVER_MODULES } from "@aihot/site/modules/server";
import { DEPLOYMENT } from "@aihot/site";
import { feishuLoginConfigured } from "@aihot/backend/admin/auth";
import { startHeartbeat } from "@aihot/backend/operations/heartbeat";
import { startWorkerWatchdog } from "@aihot/backend/operations/watch";
import { buildApp } from "./app.ts";

installModules(SERVER_MODULES);
assertProductionSecrets([
  ["auth", "SESSION_SECRET"],
  ["auth", "IMG_PROXY_SIGN_SECRET"],
  ...DEPLOYMENT.requiredSecrets,
]);
// Somebody must be able to sign in to the admin.
if (config.environmentName === "production" && !(config.adminPassword && config.adminPassword.length >= 12) && !feishuLoginConfigured()) {
  throw new Error("Refusing to start in production: set ADMIN_PASSWORD (at least 12 characters) or configure Feishu sign-in");
}

const app = await buildApp();
// Railway and other managed runtimes provide PORT and require binding on all interfaces.
const port = Number.parseInt(process.env.PORT || process.env.API_PORT || String(config.apiPort), 10);
const host = process.env.API_HOST || "0.0.0.0";
await app.listen({ port, host });
startHeartbeat(`api:${config.apiPort}`);
startWorkerWatchdog();

let stopping = false;
const shutdown = async () => {
  if (stopping) return;
  stopping = true;
  await app.close();
  await closeDb();
  process.exit(0);
};
process.on("SIGTERM", shutdown);
process.on("SIGINT", shutdown);
