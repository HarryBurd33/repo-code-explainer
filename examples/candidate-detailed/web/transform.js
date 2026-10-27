// Read UTF-8 JSON from stdin (descriptor 0) and parse it; invalid JSON throws.
const input = JSON.parse(require("fs").readFileSync(0, "utf8"));
// For array input, retain values comparing >= 0 and double them in order.
// These operators can coerce nonnumeric values; there is no type validation.
const result = input.filter(value => value >= 0).map(value => value * 2);
// Serialize the transformed array to stdout for bridge.run to decode.
process.stdout.write(JSON.stringify(result));
