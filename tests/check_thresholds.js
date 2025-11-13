const fs = require('fs');

// Load the Artillery JSON report
const reportFile = 'artillery-report.json';
const report = JSON.parse(fs.readFileSync(reportFile, 'utf-8'));

// Define your thresholds
const thresholds = {
  'http.success_rate': 1,       // must be <= 1 (or < 1 to fail)
  'http.response_time.mean': 0.0001,  // in ms
  'http.response_time.p95': 0.0001
};

// Helper to get nested value
function getNested(obj, path) {
  return path.split('.').reduce((o, key) => (o ? o[key] : undefined), obj);
}

// Check thresholds
let failed = false;
for (const [metric, limit] of Object.entries(thresholds)) {
  const value = getNested(report.aggregate, metric);
  if (value === undefined) continue;
  
  // For success rate, fail if less than threshold (adjust logic if needed)
  if (metric === 'http.success_rate') {
    if (value < limit) {
      console.log(`Threshold failed: ${metric} = ${value} < ${limit}`);
      failed = true;
    }
  } else {
    // For response times, fail if higher than threshold
    if (value > limit) {
      console.log(`Threshold failed: ${metric} = ${value} > ${limit}`);
      failed = true;
    }
  }
}

if (failed) {
  console.error('Performance thresholds violated. Failing the build.');
  process.exit(1); // non-zero exit code fails CI/CD
} else {
  console.log('All thresholds passed.');
  process.exit(0);
}
