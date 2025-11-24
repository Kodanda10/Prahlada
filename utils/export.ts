import * as XLSX from 'xlsx';
import jsPDF from 'jspdf';
import 'jspdf-autotable';
import { ParsedEvent } from '../types';

// Add this to make typescript happy with jspdf-autotable
declare module 'jspdf' {
    interface jsPDF {
        autoTable: (options: any) => jsPDF;
    }
}

export const exportToExcel = (data: any[], filename: string) => {
    if (!data || data.length === 0) return;

    let formattedData = data;

    // Check if it's ParsedEvent data
    if (data[0].parsed_data_v8) {
        formattedData = data.map((item: ParsedEvent) => ({
            'Date': item.parsed_data_v8.event_date || item.created_at.split('T')[0],
            'Location': item.parsed_data_v8.location?.ulb || item.parsed_data_v8.location?.village || item.parsed_data_v8.location?.district || "Unknown",
            'Event Type': item.parsed_data_v8.event_type,
            'People/Tags': item.parsed_data_v8.people_canonical?.join(', ') || '-',
            'Description': item.raw_text,
            'Source': `https://twitter.com/i/web/status/${item.tweet_id}`
        }));
    }

    const worksheet = XLSX.utils.json_to_sheet(formattedData);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Data');
    XLSX.writeFile(workbook, `${filename}.xlsx`);
};

export const exportToPDF = (data: any[], filename: string) => {
    if (!data || data.length === 0) return;

    const doc = new jsPDF();
    let tableColumn: string[] = [];
    let tableRows: any[] = [];

    // Check if it's ParsedEvent data
    if (data[0].parsed_data_v8) {
        tableColumn = ["Date", "Location", "Event Type", "People", "Description"];
        data.forEach((tweet: ParsedEvent) => {
            const tweetData = [
                tweet.parsed_data_v8.event_date || tweet.created_at.split('T')[0],
                tweet.parsed_data_v8.location?.ulb || tweet.parsed_data_v8.location?.village || tweet.parsed_data_v8.location?.district || "Unknown",
                tweet.parsed_data_v8.event_type,
                tweet.parsed_data_v8.people_canonical?.join(', ') || '-',
                tweet.raw_text
            ];
            tableRows.push(tweetData);
        });
    } else {
        // Generic data
        tableColumn = Object.keys(data[0]);
        data.forEach((item: any) => {
            tableRows.push(Object.values(item));
        });
    }

    doc.autoTable({
        head: [tableColumn],
        body: tableRows,
        startY: 20,
        styles: { overflow: 'linebreak', cellWidth: 'wrap' },
        columnStyles: {
            // Adjust column styles based on content if needed
            // For generic data, we might need a smarter way to handle widths
        },
        theme: 'grid',
        headStyles: { fillColor: [22, 163, 74] } // Green header
    });

    doc.save(`${filename}.pdf`);
};
