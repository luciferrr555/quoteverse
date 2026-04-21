/* ═══════════════════════════════
   QuoteVerse — Quote Image Downloader
   Uses html2canvas to render poster
   ═══════════════════════════════ */

function downloadPoster() {
    const poster = document.getElementById('quotePoster');
    if (!poster || typeof html2canvas === 'undefined') {
        showToast('Download feature requires html2canvas. Make sure you\'re online.', 'warning');
        return;
    }

    const btn = event.target.closest('button');
    if (btn) {
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
        btn.disabled = true;
    }

    // Make sure colors are applied before screenshot
    poster.style.minWidth = '500px';

    html2canvas(poster, {
        useCORS: true,
        scale: 2,
        backgroundColor: null,
        logging: false,
        allowTaint: false,
    }).then(canvas => {
        // Create download link
        const link = document.createElement('a');
        link.download = 'quote-quoteverse.png';
        link.href = canvas.toDataURL('image/png', 1.0);
        link.click();
        showToast('Quote image downloaded! 🎨', 'success');

        if (btn) {
            btn.innerHTML = '<i class="fas fa-download"></i> Download Image';
            btn.disabled = false;
        }
    }).catch(err => {
        console.error('html2canvas error:', err);
        showToast('Could not generate image. Try again!', 'danger');
        if (btn) {
            btn.innerHTML = '<i class="fas fa-download"></i> Download Image';
            btn.disabled = false;
        }
    });
}

// Change poster theme before download
function setPosterTheme(gradient) {
    const poster = document.getElementById('quotePoster');
    if (poster) poster.style.background = gradient;
}
