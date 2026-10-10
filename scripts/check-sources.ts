// Checks every default public source without writing to the database.
// Run before a release, or when the site has stopped receiving fresh items:
//   node scripts/check-sources.ts
import { readFileSync } from "node:fs";
import path from "node:path";
import { REPO_ROOT } from "@aihot/backend/config";
import { assertSupportedConfig } from "@aihot/backend/sources/config-keys";
import { fetchJsonList } from "@aihot/backend/sources/json-list";
import { fetchRss } from "@aihot/backend/sources/rss";
import { fetchWebList } from "@aihot/backend/sources/web-list";

interface Source {
  id: string;
  name: string;
  kind: "rss" | "web_list" | "json_list";
  config: Record<string, unknown>;
  participation_mode?: string;
}

const parsed = JSON.parse(readFileSync(path.join(REPO_ROOT, "industry/sources.json"), "utf8")) as { sources: Source[] };
let failed = 0;

async function check(source: Source): Promise<void> {
  assertSupportedConfig(source.kind, source.config);
  try {
    const input = { ...source, participation_mode: source.participation_mode ?? "editorial", cursor: null } as never;
    const count = source.kind === "rss"
      ? (await fetchRss(input, { force: true })).candidates.length
      : source.kind === "web_list"
        ? (await fetchWebList(input)).length
        : (await fetchJsonList(input)).length;
    if (count < 1) throw new Error("返回 0 条资料");
    console.log(`✓ ${source.name}: ${count} 条`);
  } catch (error) {
    failed += 1;
    console.error(`✗ ${source.name}: ${(error as Error).message}`);
  }
}

// Bound concurrency so a health check does not look like a burst crawler.
for (let index = 0; index < parsed.sources.length; index += 4) {
  await Promise.all(parsed.sources.slice(index, index + 4).map(check));
}

console.log(failed ? `\n${failed} 个信源不可用` : `\n${parsed.sources.length} 个信源全部可用`);
process.exitCode = failed ? 1 : 0;
