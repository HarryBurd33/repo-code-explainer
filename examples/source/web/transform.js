const input = JSON.parse(require("fs").readFileSync(0, "utf8"));
const result = input.filter(value => value >= 0).map(value => value * 2);
process.stdout.write(JSON.stringify(result));
