import test from "node:test";
import assert from "node:assert/strict";
test("demo identifiers are clearly distinguishable", () => {
  const id = `DEMO-${1042}`;
  assert.match(id, /^DEMO-\d{4}$/);
});
