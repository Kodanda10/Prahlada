const fs = require('fs');
const path = require('path');

const INPUT_FILE = path.join(__dirname, '../data/parsed_tweets_v8.jsonl');
const OUTPUT_FILE = path.join(__dirname, '../data/ingested_tweets.json');

console.log('🚀 Starting data ingestion (Simple JS)...');

try {
    if (!fs.existsSync(INPUT_FILE)) {
        console.error(`❌ Input file not found: ${INPUT_FILE}`);
        process.exit(1);
    }

    const fileContent = fs.readFileSync(INPUT_FILE, 'utf-8');
    const lines = fileContent.trim().split('\n');
    console.log(`📊 Found ${lines.length} lines to process`);

    const ingestedTweets = [];

    for (const line of lines) {
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
        } catch (e) {
            console.error('Error parsing line:', e.message);
        }
    }

    fs.writeFileSync(OUTPUT_FILE, JSON.stringify(ingestedTweets, null, 2), 'utf-8');
    console.log(`✅ Successfully wrote ${ingestedTweets.length} tweets to ${OUTPUT_FILE}`);

} catch (error) {
    console.error('Fatal error:', error);
    process.exit(1);
}
