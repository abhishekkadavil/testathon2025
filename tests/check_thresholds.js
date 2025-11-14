const fs = require("fs");

const report = JSON.parse(fs.readFileSync("artillery-report.json", "utf8"));
const metrics = report.aggregate.summaries["http.response_time"];

const mean = metrics.mean;
const p95 = metrics.p95;

// Fail conditions
let failed = false;

if (mean > 0.5) {
  console.error("❌ Mean response time too high:", mean);
  failed = true;
}

if (p95 > 1) {
  console.error("❌ p95 response time too high:", p95);
  failed = true;
}

if (failed) {
  process.exit(1); // Fail CI
} else {
  console.log("✔️ Performance thresholds passed");
}
