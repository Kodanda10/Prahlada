import fs from 'fs';
import path from 'path';
import { ParsedEvent } from '../types';

export const loadRealTweets = (): ParsedEvent[] => {
  const filePath = path.resolve(__dirname, '../data/parsed_tweets_gemini_parser_v2.jsonl');
  try {
    const fileContent = fs.readFileSync(filePath, 'utf-8');
    const lines = fileContent.trim().split('\n');
    return lines.map(line => JSON.parse(line));
  } catch (error) {
    console.warn(`Failed to load real tweets from ${filePath}:`, error);
    return [];
  }
};

export const loadGoldStandard = (): any[] => {
    const filePath = path.resolve(__dirname, '../data/gold_standard_tweets.csv');
    try {
        const fileContent = fs.readFileSync(filePath, 'utf-8');
        const lines = fileContent.trim().split('\n');
        const headers = lines[0].split(',');
        return lines.slice(1).map(line => {
            const values = line.split(',');
            return headers.reduce((obj, header, index) => {
                obj[header.trim()] = values[index]?.trim();
                return obj;
            }, {} as any);
        });
    } catch (error) {
        console.warn(`Failed to load gold standard from ${filePath}:`, error);
        return [];
    }
};
