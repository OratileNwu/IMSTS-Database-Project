// static/js/products.js
(function () {
    const exportBtn = document.getElementById('exportBtn');
    const table = document.getElementById('productTable');

    function exportToCSV() {
        if (!table) return;

        let csv = [];
        let rows = table.querySelectorAll('tbody tr');
        let hasData = false;

        for (let row of rows) {
            // Skip empty state row
            if (row.id === 'emptyStateRow') continue;

            let rowData = [];
            let cells = row.querySelectorAll('td');

            // Get all cells except the last one (actions column)
            for (let i = 0; i < cells.length - 1; i++) {
                let text = cells[i].innerText || '';
                // Clean up the text (remove extra spaces, handle commas)
                text = text.trim().replace(/"/g, '""');
                rowData.push('"' + text + '"');
            }

            if (rowData.length > 0) {
                csv.push(rowData.join(','));
                hasData = true;
            }
        }

        if (!hasData) {
            alert('No data to export');
            return;
        }

        // Add headers
        const headers = ['ID', 'Name', 'SKU', 'Category', 'Supplier', 'Price', 'Stock', 'Status'];
        csv.unshift(headers.map(h => '"' + h + '"').join(','));

        // Download CSV
        const blob = new Blob([csv.join('\n')], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.href = url;
        link.setAttribute('download', `products_export_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }

    if (exportBtn) {
        exportBtn.addEventListener('click', exportToCSV);
    }
})();