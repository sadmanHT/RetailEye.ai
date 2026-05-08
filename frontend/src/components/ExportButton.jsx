import React from 'react';
import { Download } from 'lucide-react';
import { formatDuration } from '../utils/formatters.js';

const ExportButton = ({ analyticsData }) => {
  const handleExport = () => {
    if (!analyticsData) return;

    const summary = analyticsData.summary_metrics || {};
    const zoneData = analyticsData.zone_analytics || [];
    const tracks = analyticsData.tracked_individuals || [];
    
    // Extract derived metrics
    const totalPeople = summary.total_unique_people || 0;
    const duration = formatDuration(summary.processed_duration_seconds || 0);
    const busiestZone = summary.busiest_zone || 'N/A';
    const avgDwell = formatDuration(summary.average_dwell_time_all_zones || 0);

    const generationDate = new Date().toLocaleString();

    // Create a new window for the print layout
    const printWindow = window.open('', '_blank');
    if (!printWindow) {
      alert("Please allow popups to generate the report.");
      return;
    }

    const htmlContent = `
      <!DOCTYPE html>
      <html>
      <head>
        <title>RetailEye AI - Analytics Report</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
          @media print {
            body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
            @page { margin: 20mm; }
            .page-break { page-break-before: always; }
          }
          body { font-family: 'Inter', system-ui, sans-serif; color: #111827; background: white; }
          table { width: 100%; border-collapse: collapse; margin-bottom: 2rem; }
          th { background-color: #f3f4f6; text-align: left; padding: 12px; font-weight: 600; border-bottom: 2px solid #e5e7eb; }
          td { padding: 12px; border-bottom: 1px solid #e5e7eb; }
          tr:nth-child(even) { background-color: #f9fafb; }
        </style>
      </head>
      <body class="p-8">
        
        <!-- Header -->
        <header class="border-b-2 border-gray-900 pb-4 mb-8 flex justify-between items-end">
          <div>
            <h1 class="text-3xl font-bold tracking-tight text-gray-900">RetailEye AI</h1>
            <p class="text-gray-500 mt-1">Store Intelligence & Analytics Report</p>
          </div>
          <div class="text-right">
            <p class="text-sm text-gray-500 font-medium">Generated On</p>
            <p class="text-gray-900">${generationDate}</p>
          </div>
        </header>

        <!-- Summary Section -->
        <section class="mb-10">
          <h2 class="text-xl font-bold mb-4 text-gray-800">Executive Summary</h2>
          <div class="grid grid-cols-4 gap-4">
            <div class="bg-gray-50 p-4 rounded-lg border border-gray-200">
              <p class="text-xs text-gray-500 font-semibold uppercase tracking-wider">Total People Tracked</p>
              <p class="text-2xl font-bold text-gray-900 mt-1">${totalPeople}</p>
            </div>
            <div class="bg-gray-50 p-4 rounded-lg border border-gray-200">
              <p class="text-xs text-gray-500 font-semibold uppercase tracking-wider">Video Duration</p>
              <p class="text-2xl font-bold text-gray-900 mt-1">${duration}</p>
            </div>
            <div class="bg-gray-50 p-4 rounded-lg border border-gray-200">
              <p class="text-xs text-gray-500 font-semibold uppercase tracking-wider">Busiest Zone</p>
              <p class="text-2xl font-bold text-gray-900 mt-1">${busiestZone}</p>
            </div>
            <div class="bg-gray-50 p-4 rounded-lg border border-gray-200">
              <p class="text-xs text-gray-500 font-semibold uppercase tracking-wider">Avg Dwell Time</p>
              <p class="text-2xl font-bold text-gray-900 mt-1">${avgDwell}</p>
            </div>
          </div>
        </section>

        <!-- Zone Analytics Table -->
        <section class="mb-10">
          <h2 class="text-xl font-bold mb-4 text-gray-800">Zone Analytics</h2>
          <table>
            <thead>
              <tr>
                <th>Zone Name</th>
                <th>Total Entered</th>
                <th>Avg Dwell Time</th>
                <th>Currently Present</th>
              </tr>
            </thead>
            <tbody>
              ${zoneData.map(zone => `
                <tr>
                  <td class="font-medium">${zone.zone_name}</td>
                  <td>${zone.total_people_entered}</td>
                  <td>${formatDuration(zone.average_dwell_time)}</td>
                  <td>${zone.current_people_count || 0}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </section>

        <div class="page-break"></div>

        <!-- Header for second page -->
        <header class="border-b-2 border-gray-900 pb-4 mb-8 flex justify-between items-end">
          <div>
            <h1 class="text-2xl font-bold tracking-tight text-gray-900">RetailEye AI</h1>
          </div>
          <div class="text-right">
            <p class="text-gray-500 text-sm">Tracked Entities Report</p>
          </div>
        </header>

        <!-- Target Dwell Time Table -->
        <section class="mb-10">
          <h2 class="text-xl font-bold mb-4 text-gray-800">Tracked Individuals Overview</h2>
          <table>
            <thead>
              <tr>
                <th>Track ID</th>
                <th>Total Screen Time</th>
                <th>Zones Visited</th>
                <th>Max Dwell Time</th>
              </tr>
            </thead>
            <tbody>
              ${tracks.slice(0, 50).map(track => {
                const maxDwell = Math.max(...Object.values(track.dwell_times || { 0: 0 }));
                return `
                  <tr>
                    <td class="font-medium">#${track.track_id}</td>
                    <td>${formatDuration(track.total_time_in_frame)}</td>
                    <td>${track.zones_visited?.join(', ') || 'None'}</td>
                    <td>${formatDuration(maxDwell)}</td>
                  </tr>
                `;
              }).join('')}
            </tbody>
          </table>
          ${tracks.length > 50 ? `<p class="text-sm text-gray-500">* Showing top 50 tracked individuals.</p>` : ''}
        </section>

        <!-- Footer -->
        <footer class="mt-16 pt-8 border-t border-gray-200 text-sm text-gray-500 flex justify-between">
          <p>&copy; ${new Date().getFullYear()} RetailEye AI - Confidential</p>
          <p>Page <span class="page-number"></span></p>
        </footer>

        <script>
          // Wait for Tailwind to process, then print
          setTimeout(() => {
            window.print();
            // Optional: close window after print dialog is handled.
            // window.onafterprint = () => window.close();
          }, 1000);
        </script>
      </body>
      </html>
    `;

    printWindow.document.open();
    printWindow.document.write(htmlContent);
    printWindow.document.close();
  };

  return (
    <button
      onClick={handleExport}
      disabled={!analyticsData}
      className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium rounded-lg transition-colors border border-blue-500 shadow-sm shadow-blue-900/20"
    >
      <Download size={16} />
      <span>Export PDF</span>
    </button>
  );
};

export default ExportButton;