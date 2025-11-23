#!/usr/bin/env node
/**
 * Data Ingestion Script
 * 
 * Loads 2,611 parsed tweets from parsed_tweets_v8.jsonl into the application.
 * Implements Zero-Trust Analytics Protocol: all tweets start with approved_by_human = false
 */

import * as fs from 'fs';
import * as path from 'path';
import { fileURLToPath } from 'url';
import { ParsedEvent } from '../types.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const INPUT_FILE = path.join(__dirname, '../data/parsed_tweets_v8.jsonl');
const OUTPUT_FILE = path.join(__dirname, '../data/ingested_tweets.json');


interface IngestionStats {
    total_read: number;
    successfully_ingested: number;
    skipped: number;
    errors: number;
    error_details: Array<{ line: number; error: string }>;
}

async function ingestTweets(): Promise<IngestionStats> {
    const stats: IngestionStats = {
        total_read: 0,
        successfully_ingested: 0,
        skipped: 0,
        errors: 0,
        error_details: []
    };

    console.log('🚀 Starting data ingestion...');
    console.log(`📂 Reading from: ${INPUT_FILE}`);

    // Read the JSONL file
    const fileContent = fs.readFileSync(INPUT_FILE, 'utf-8');
    const lines = fileContent.trim().split('\n');

    console.log(`📊 Found ${lines.length} lines to process`);

    const ingestedTweets: ParsedEvent[] = [];

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        if (!line) {
            stats.skipped++;
            continue;
        }

        stats.total_read++;

        try {
            const rawTweet = JSON.parse(line);

            // Transform to ParsedEvent with HITL fields
            const parsedEvent: ParsedEvent = {
                ...rawTweet,
                // Zero-Trust Protocol: All tweets start as NOT approved
                approved_by_human: false,
                corrected_fields: {},
                feedback_log: []
            };

            ingestedTweets.push(parsedEvent);
            stats.successfully_ingested++;

            if (stats.successfully_ingested % 500 === 0) {
                console.log(`✅ Processed ${stats.successfully_ingested} tweets...`);
            }
        } catch (error) {
            stats.errors++;
            stats.error_details.push({
                line: i + 1,
                error: error instanceof Error ? error.message : String(error)
            });

            if (stats.errors <= 5) {
                console.error(`❌ Error on line ${i + 1}:`, error);
            }
        }
    }

    // Write ingested data to output file
    console.log(`\n💾 Writing ${ingestedTweets.length} tweets to ${OUTPUT_FILE}...`);
    fs.writeFileSync(OUTPUT_FILE, JSON.stringify(ingestedTweets, null, 2), 'utf-8');

    // Generate summary report
    console.log('\n' + '='.repeat(60));
    console.log('📈 INGESTION SUMMARY');
    console.log('='.repeat(60));
    console.log(`Total lines read:        ${stats.total_read}`);
    console.log(`Successfully ingested:   ${stats.successfully_ingested}`);
    console.log(`Skipped (empty lines):   ${stats.skipped}`);
    console.log(`Errors:                  ${stats.errors}`);
    console.log('='.repeat(60));

    if (stats.errors > 0 && stats.error_details.length > 0) {
        console.log('\n⚠️  Error Details (first 5):');
        stats.error_details.slice(0, 5).forEach(({ line, error }) => {
            console.log(`  Line ${line}: ${error}`);
        });
    }

    // Verify count
    if (stats.successfully_ingested === 2611) {
        console.log('\n✅ SUCCESS: All 2,611 tweets ingested correctly!');
    } else {
        console.log(`\n⚠️  WARNING: Expected 2,611 tweets but got ${stats.successfully_ingested}`);
    }

    // Zero-Trust Protocol Verification
    const approvedCount = ingestedTweets.filter(t => t.approved_by_human).length;
    console.log(`\n🔒 Zero-Trust Protocol: ${approvedCount} tweets approved (should be 0)`);

    if (approvedCount === 0) {
        console.log('✅ Zero-Trust Protocol VERIFIED: Analytics will be empty until human approval');
    } else {
        console.log('⚠️  WARNING: Some tweets are pre-approved!');
    }

    return stats;
}

// Run the ingestion
if (import.meta.url === `file://${process.argv[1]}`) {
    ingestTweets()
        .then(() => {
            console.log('\n🎉 Ingestion complete!');
            process.exit(0);
        })
        .catch((error) => {
            console.error('\n💥 Fatal error during ingestion:', error);
            process.exit(1);
        });
}

export { ingestTweets };
