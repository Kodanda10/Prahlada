const fs = require('fs');
const path = require('path');
const readline = require('readline');

const INPUT_FILE = path.join(__dirname, '../data/parsed_tweets_v8.jsonl');
const OUTPUT_FILE = path.join(__dirname, '../data/ingested_tweets.json');

async function ingest() {
    console.time('Ingestion');
    console.log('🚀 Starting optimized data ingestion...');

    if (!fs.existsSync(INPUT_FILE)) {
        console.error(`❌ Input file not found: ${INPUT_FILE}`);
        process.exit(1);
    }

    const fileStream = fs.createReadStream(INPUT_FILE);
    const rl = readline.createInterface({
        input: fileStream,
        crlfDelay: Infinity
    });

    const ingestedTweets = [];
    let count = 0;

    for await (const line of rl) {
        if (!line.trim()) continue;
        try {
            const rawTweet = JSON.parse(line);
            const parsedEvent = {
                ...rawTweet,
                approved_by_human: false,
                corrected_fields: {},
                feedback_log: []
            };
            ingestedTweets.push(parsedEvent);
            count++;
            if (count % 500 === 0) process.stdout.write(`\rProcessed ${count} tweets...`);
        } catch (e) {
            // console.error('Error parsing line:', e.message);
        }
    }

    console.log(`\n✅ Processed ${count} tweets.`);
    console.log(`💾 Writing to ${OUTPUT_FILE}...`);
    
    fs.writeFileSync(OUTPUT_FILE, JSON.stringify(ingestedTweets, null, 2), 'utf-8');
    
    console.log('🎉 Done!');
    console.timeEnd('Ingestion');
}

ingest().catch(console.error);
