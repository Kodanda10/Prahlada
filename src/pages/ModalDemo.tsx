import React from 'react';
import ReviewCard from '../../components/ReviewCard';
import { ParsedEvent } from '../types';

const MOCK_EVENT = {
    tweet_id: '1234567890',
    raw_text: 'Raipur district ke Abhanpur block me paani ki samasya hai. #WaterCrisis',
    created_at: '2023-10-27T10:00:00Z',
    processed_at: '2023-10-27T10:05:00Z',
    status: 'pending',
    parsed_data_v8: {
        event_type: 'Public Grievance',
        confidence: 0.95,
        location: {
            district: 'Raipur',
            block: 'Abhanpur',
            village: 'Kendri',
            assembly: 'Abhanpur',
            gp: 'Kendri'
        },
        people_canonical: ['Sarpanch'],
        schemes_mentioned: ['Jal Jeevan Mission'],
        target_groups: ['Farmers'],
        communities: ['Rural'],
        organizations: [],
        sentiment: 'Negative',
        language: 'Hindi'
    }
} as unknown as ParsedEvent;

export default function ModalDemo() {
    return (
        <div className="p-10 min-h-screen bg-slate-900 flex justify-center items-start pt-20">
            <div className="w-full max-w-2xl">
                <h1 className="text-white text-2xl mb-6 font-bold">Location Decision Modal Demo</h1>
                <ReviewCard
                    event={MOCK_EVENT}
                    onApprove={() => console.log('Approved')}
                    onEdit={() => console.log('Edit')}
                />
            </div>
        </div>
    );
}
