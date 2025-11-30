// import ExcelJS from 'exceljs';
import jsPDF from 'jspdf';
import 'jspdf-autotable';
import { ParsedEvent } from '../types';

// Add this to make typescript happy with jspdf-autotable
declare module 'jspdf' {
    interface jsPDF {
        autoTable: (options: any) => jsPDF;
    }
}

export const exportToExcel = async (data: any[], filename: string) => {
    console.log("Export to Excel disabled for debugging");
    /*
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

    const workbook = new ExcelJS.Workbook();
    const worksheet = workbook.addWorksheet('Data');

    // Generate columns from the first item keys
    if (formattedData.length > 0) {
        const columns = Object.keys(formattedData[0]).map(key => ({ header: key, key: key, width: 20 }));
        worksheet.columns = columns;
    }

    // Add rows
    worksheet.addRows(formattedData);

    // Style header
    worksheet.getRow(1).font = { bold: true };

    // Write buffer and trigger download
    const buffer = await workbook.xlsx.writeBuffer();
    const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    const url = window.URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = `${filename}.xlsx`;
    anchor.click();
    window.URL.revokeObjectURL(url);
    */
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
