const fs = require('fs');
const path = require('path');
const readline = require('readline');

const INPUT_FILE = path.join(__dirname, '../data/parsed_tweets_v8.jsonl');
const OUTPUT_FILE = path.join(__dirname, '../data/ingested_tweets.json');
const TIMEOUT_MS = 30000; // 30 seconds timeout

async function ingest() {
    console.time('Total');
    console.log(`🚀 Starting ingestion from ${INPUT_FILE}`);

    // Safety timeout
    const timeout = setTimeout(() => {
        console.error('\n❌ Script timed out after 30 seconds!');
        process.exit(1);
    }, TIMEOUT_MS);

    if (!fs.existsSync(INPUT_FILE)) {
        console.error(`❌ Input file not found: ${INPUT_FILE}`);
        process.exit(1);
    }

    const fileStream = fs.createReadStream(INPUT_FILE);
    const rl = readline.createInterface({ input: fileStream, crlfDelay: Infinity });

    const tweets = [];
    let count = 0;

    for await (const line of rl) {
        if (!line.trim()) continue;
        try {
            const raw = JSON.parse(line);
            tweets.push({ ...raw, approved_by_human: false, corrected_fields: {}, feedback_log: [] });
            count++;
            if (count % 500 === 0) process.stdout.write(`\rProcessed ${count} tweets...`);
        } catch (e) {
            // ignore parse errors
        }
    }

    console.log(`\n✅ Processed ${count} tweets. Writing to file...`);
    
    try {
        fs.writeFileSync(OUTPUT_FILE, JSON.stringify(tweets), 'utf-8');
        console.log(`🎉 Successfully wrote to ${OUTPUT_FILE}`);
    } catch (err) {
        console.error('❌ Error writing file:', err);
    }

    clearTimeout(timeout);
    console.timeEnd('Total');
    process.exit(0);
}

ingest().catch(err => {
    console.error('Fatal error:', err);
    process.exit(1);
});
