import assert from "node:assert/strict";
import test from "node:test";
import { radarHeat } from "../server.ts";

test("technology radar heat keeps the documented 75/25 weighting and 0-100 bound", () => {
  assert.equal(radarHeat(80, 5), 70);
  assert.equal(radarHeat(100, 100), 100);
  assert.equal(radarHeat(0, 0), 0);
});
